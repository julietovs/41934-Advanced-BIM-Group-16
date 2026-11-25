"""Command-line entry point for the A4 assignment."""

from runall import main
from settings import MODEL_PATH

model_path = MODEL_PATH

if __name__ == "__main__":
    main(model_path=model_path)
