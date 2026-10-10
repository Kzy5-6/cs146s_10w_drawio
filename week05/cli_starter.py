"""Starter CLI for exporting notes from the local course project API."""

import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export meeting notes")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--output", default="notes-export.json")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    # TODO: Fetch the notes, handle HTTP and file errors, and write valid JSON.
    # In --dry-run mode, describe the planned output without writing a file.
    print(f"TODO: export notes from {args.base_url} to {args.output}")
    if args.dry_run:
        print("Dry run: no file should be written.")


if __name__ == "__main__":
    main()
