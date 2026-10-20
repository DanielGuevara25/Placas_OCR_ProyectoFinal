"""Rutas compartidas independientes del directorio de ejecución."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / 'data/processed/dataset_placas'
TRAINING = ROOT / 'results/training'
DEFAULT_WEIGHTS = ROOT / 'models/best.pt'
