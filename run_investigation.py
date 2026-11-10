
import argparse
import json
import os

from dotenv import load_dotenv

from devlens.agent import investigate


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="DevLens: AI-powered API failure investigation"
    )

    parser.add_argument(
        "--repo",
        required=True,
        help="Path to the Python repository",
    )

    parser.add_argument(
        "--failure",
        required=True,
        help="Description of the observed API failure",
    )

    args = parser.parse_args()

    report, trace = investigate(
        failure_description=args.failure,
        repo_root=args.repo,
    )

    print("\n=== Tool Trace ===")
    for index, call in enumerate(trace, start=1):
        print(f"{index}. {call['tool']}: {call['arguments']}")

    print("\n=== Investigation Report ===")
    print(report.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
