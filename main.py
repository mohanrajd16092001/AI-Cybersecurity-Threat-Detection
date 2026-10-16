import argparse
from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parent

COMMANDS = {
    "inspect": "load_data.py",
    "train": "train_model.py",
    "evaluate": "evaluate_model.py",
    "simulate": "detect_threats.py",
    "serve": "app.py",
}


def main():
    parser = argparse.ArgumentParser(
        description="AI-Powered Cybersecurity Threat Detection"
    )

    parser.add_argument(
        "command",
        choices=COMMANDS,
        help="Choose which project task to run.",
    )

    args = parser.parse_args()
    script = PROJECT_ROOT / "src" / COMMANDS[args.command]

    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=PROJECT_ROOT,
            check=False,
        )
        return result.returncode
    except KeyboardInterrupt:
        print("\nStopped.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())