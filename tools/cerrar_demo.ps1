$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$taskTunnel = Join-Path $taskRoot '.model-cache\demo\cloudflared.exe'
$taskPython = Join-Path $taskRoot '.venv-tests\Scripts\python.exe'
# Sólo procesos de este proyecto y del puerto de la demo; nunca otras instancias.
$taskProcesses = Get-CimInstance Win32_Process
foreach ($taskProcess in $taskProcesses) {
    if ($taskProcess.ExecutablePath -eq $taskTunnel -and
        $taskProcess.CommandLine -match '127\.0\.0\.1:8081') {
        Stop-Process -Id $taskProcess.ProcessId
    }
}
foreach ($taskProcess in $taskProcesses) {
    if ($taskProcess.ExecutablePath -eq $taskPython -and
        $taskProcess.CommandLine -match 'tools[\\/]servidor_demo\.py') {
        Stop-Process -Id $taskProcess.ProcessId
    }
}
Write-Output 'Túnel y servidor de esta demostración cerrados.'
