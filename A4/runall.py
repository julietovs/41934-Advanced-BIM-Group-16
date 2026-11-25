import argparse
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from ventilation_check.src.exports import build_ids, write_room_outputs
from ventilation_check.src.main import analyse as check_ventilation, read_inputs
from settings import MODEL_PATH

ANALYSES = {"ventilation_check": check_ventilation}


def save_result(result, results_dir):
    # Reject unsupported values before creating a run folder.
    content = json.dumps(result, indent=2, allow_nan=False)
    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = Path(tempfile.mkdtemp(prefix=f"run-{timestamp}-", dir=results_dir))
    output = run_dir / "result.json"
    output.write_text(content + "\n", encoding="utf-8")
    return output


def main(model_path=MODEL_PATH):
    parser = argparse.ArgumentParser(description="Run your analysis on a local IFC.")
    parser.add_argument(
        "model", nargs="?", type=Path,
        help="IFC path (defaults to MODEL_PATH in settings.py)",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        help="Optional output root; writes <root>/<analysis-name>/run-.../result.json",
    )
    parser.add_argument("--data", type=Path, help="Completed room_inputs.csv")
    parser.add_argument("--ids", action="store_true", help="Generate ventilation_inputs.ids")
    args = parser.parse_args()
    if args.model is None:
        if not str(model_path).strip():
            parser.error("Set MODEL_PATH in settings.py or pass an IFC path.")
        args.model = Path(model_path)
        if not args.model.is_absolute():
            args.model = Path(__file__).resolve().parent / args.model
    if not args.model.is_file():
        parser.error(f"IFC file not found: {args.model}")

    import ifcopenshell

    try:
        model = ifcopenshell.open(str(args.model))
        room_inputs = read_inputs(args.data) if args.data else None
        run_analyses(model, args.results_dir, room_inputs=room_inputs, export_ids=args.ids)
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(1, f"Error: {error}\n")


def run_analyses(model, results_dir=None, *, room_inputs=None, export_ids=False):
    for name, analyse in ANALYSES.items():
        is_ventilation = name == "ventilation_check"
        result = analyse(model, room_inputs=room_inputs) if is_ventilation else analyse(model)
        ids_document = build_ids(result) if is_ventilation and export_ids else None
        destination = (
            Path(__file__).resolve().parent / name / "results"
            if results_dir is None else Path(results_dir) / name
        )
        output = save_result(result, destination)
        if is_ventilation:
            write_room_outputs(output.parent, model, result, write_scope_template=room_inputs is None)
        if ids_document is not None:
            if not ids_document.to_xml(str(output.parent / "ventilation_inputs.ids")):
                raise RuntimeError("Generated IDS XML did not pass schema validation.")
        print(f"{name}: Result saved to: {output.resolve()}")


if __name__ == "__main__":
    main()
