#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import pathlib
import sys
import traceback

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def load_module(path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    failures = 0
    total = 0
    for path in sorted((ROOT / "tests").glob("test_*.py")):
        module = load_module(path)
        for name in sorted(dir(module)):
            if not name.startswith("test_"):
                continue
            total += 1
            try:
                getattr(module, name)()
                print(f"PASS {name}")
            except Exception:
                failures += 1
                print(f"FAIL {name}")
                traceback.print_exc(limit=2)
    print(f"\n{total - failures}/{total} tests passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
