"""CLI: run FirefighterReviewer on all session JSON files in a directory, write JSONL predictions."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from tqdm import tqdm

from models import SessionLog
from reviewer import FirefighterReviewer


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze SAP firefighter session JSON files and append ReviewResult lines to a JSONL file."
    )
    parser.add_argument(
        "--input_dir",
        required=True,
        help="Directory containing session .json files (e.g. dataset_candidate/train/sessions)",
    )
    parser.add_argument(
        "--output_file",
        required=True,
        help="Output JSONL path (e.g. predictions.jsonl); each successful result is appended as one line",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_path = Path(args.output_file)

    if not input_dir.is_dir():
        print(f"Error: not a directory: {input_dir}", file=sys.stderr)
        sys.exit(1)

    json_files = sorted(input_dir.glob("*.json"))
    if not json_files:
        print(f"Warning: no .json files in {input_dir}", file=sys.stderr)

    reviewer = FirefighterReviewer()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "a", encoding="utf-8") as out_f:
        for path in tqdm(json_files, desc="Sessions"):
            try:
                session = SessionLog.model_validate_json(path.read_text(encoding="utf-8"))
                result = reviewer.analyze_session(session)
                out_f.write(result.model_dump_json() + "\n")
                out_f.flush()
            except Exception as exc:
                print(f"{path.name}: {exc}", file=sys.stderr)
            finally:
                time.sleep(20)


if __name__ == "__main__":
    main()
