#!/usr/bin/env python3
"""Copy blank project templates into a NEW directory; never overwrite a project."""
import argparse
import shutil
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1] / 'templates'
    try:
        shutil.copytree(source, args.destination)
    except FileExistsError:
        parser.exit(1, 'Destination already exists. Copy individual templates after reviewing conflicts.\n')
    except OSError as error:
        parser.exit(1, f'Could not initialize project: {error}\n')
    print(f'Created draft project at {args.destination.resolve()}')
    print('Edit the charter and record genuine owner adoption. The ledger is empty; nothing is approved.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
