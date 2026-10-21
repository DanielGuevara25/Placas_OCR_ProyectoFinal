"""Añade evidencias reales de Semana 5 conservando las celdas históricas."""
from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
TAG = "semana5_ampliada"


def actualizar():
    path = ROOT / "notebooks/04_optimizacion.ipynb"
    nb = nbf.read(path, as_version=4)
    nb.cells = [c for c in nb.cells if TAG not in c.metadata.get("tags", [])]
    md = nbf.v4.new_markdown_cell(
        "## Estudio ampliado de Semana 5\n\n"
        "Las secciones anteriores describen las tres corridas históricas. Esta sección "
        "consulta el nuevo estudio autorizado el 20/10/2026; su estado impide confundir "
        "un entrenamiento en curso con resultados completos. El diseño está en "
        "`docs/estudio_semana5.md`. Test no participa en este estudio.\n\n"
        "Los ensayos cortos usan 35% de train y 12 épocas. Su métrica no es comparable "
        "directamente con las corridas de 100 épocas. Los ajustes finales comparten "
        "SGD y presupuesto; una semilla no prueba significancia entre entrenamientos.")
    state = nbf.v4.new_code_cell('''study_dir = ROOT / "results/semana5"
if not (study_dir / "estado.json").exists():
    print("No hay estado guardado: estudio todavía sin iniciar.")
else:
    state = load("results/semana5/estado.json")
    display(state)
    print("Estudio completado:", state["stage"] == "completado")
    if (study_dir / "ensayos.json").exists():
        trials = load("results/semana5/ensayos.json")
        from collections import Counter
        print("Estados de ensayos:", dict(Counter(t["state"] for t in trials)))
        table([{k:v for k,v in t.items() if k != "intermediate"} for t in trials])
    for name in ["seleccion", "sustituto", "final_referencia", "final_optimizado"]:
        if (study_dir / (name+".json")).exists():
            print(name); display(load("results/semana5/"+name+".json"))
    for name in ["historial", "importancia", "slice", "pdp_interaccion"]:
        if (study_dir / (name+".png")).exists():
            display(Image(filename=str(study_dir/(name+".png")), width=1000))
    if (study_dir / "robustez_resumen.json").exists():
        table(load("results/semana5/robustez_resumen.json"))
        print("Bootstrap pareado por imagen; no mide incertidumbre entre entrenamientos.")
    print("Val se reutiliza para desarrollo. No es una evaluación independiente de test.")''')
    for cell in [md, state]:
        cell.metadata["tags"] = [TAG]
    nb.cells.extend([md, state])
    nbf.validate(nb); nbf.write(nb, path)


if __name__ == "__main__":
    actualizar()
