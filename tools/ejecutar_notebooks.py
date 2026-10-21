"""Ejecuta los notebooks con el intérprete actual y conserva salidas auténticas."""
import json
import os
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager

ROOT = Path(__file__).resolve().parents[1]
runtime = ROOT / '.model-cache/jupyter'
runtime.mkdir(parents=True, exist_ok=True)
os.environ['JUPYTER_RUNTIME_DIR'] = str(runtime)
os.environ['IPYTHONDIR'] = str(ROOT / '.model-cache/ipython')
report = []
for path in sorted((ROOT / 'notebooks').glob('0*.ipynb')):
    notebook = nbformat.read(path, as_version=4)
    km = KernelManager(kernel_name='python3')
    km.kernel_spec.argv[0] = sys.executable
    client = NotebookClient(notebook, km=km, timeout=180,
                            resources={'metadata': {'path': str(ROOT)}})
    try:
        client.execute()
    finally:
        if km.has_kernel:
            km.shutdown_kernel(now=True)
    nbformat.validate(notebook)
    nbformat.write(notebook, path)
    report.append({'notebook': path.name, 'code_cells': sum(c.cell_type=='code' for c in notebook.cells),
                   'errors': sum(o.output_type=='error' for c in notebook.cells
                                 if c.cell_type=='code' for o in c.outputs),
                   'new_training_executed': False})
    print(f'Ejecutado: {path.name}', flush=True)
(ROOT/'results/reports/ejecucion_notebooks.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
