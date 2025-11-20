"""
fuzz.py — Hybrid Fuzzing Suite for Team Glitch (Fall 2025 SQA)
---------------------------------------------------------------
This script fuzzes 5 functions across the MLForensics project using
a hybrid strategy:
  - Hypothesis-based property fuzzing for AST and parsing functions
  - Random fuzzing for filesystem-dependent functions

All crashes are logged to fuzz_artifacts/fuzz_crashes.log.
This file is executed automatically by GitHub Actions.
"""

import os
import random
import logging
from pathlib import Path
import importlib.util
import sys

from hypothesis import given, settings, strategies as st

# ARTIFACT DIRECTORY
ARTIFACT_DIR = Path("fuzz_artifacts")
ARTIFACT_DIR.mkdir(exist_ok=True)

# DYNAMIC IMPORTS
def load_module(path, module_name):
    """Dynamically load a Python module from a given file path."""
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

constants = load_module("FAME-ML/constants.py", "constants")
py_parser = load_module("FAME-ML/py_parser.py", "py_parser")
lint_engine = load_module("FAME-ML/lint_engine.py", "lint_engine")
gitminer = load_module("mining/git.repo.miner.py", "gitminer")
freq = load_module("empirical/frequency.py", "freq")

# Logging Setup
LOGFILE = ARTIFACT_DIR / "fuzz_crashes.log"
logging.basicConfig(
    level=logging.INFO,
    filename=str(LOGFILE),
    filemode="w",
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("fuzzer")


"""
1. FUZZ: py_parser.getPythonParseObject(path)
"""
@given(st.text(min_size=1, max_size=200))
@settings(max_examples=40)
def fuzz_getPythonParseObject(random_text):
    tmp_path = ARTIFACT_DIR / "tmp_fuzz1.py"
    tmp_path.write_text(random_text)

    try:
        py_parser.getPythonParseObject(str(tmp_path))
    except Exception:
        logger.exception(f"[getPythonParseObject] Crash on input: {random_text}")
        raise

"""
2. FUZZ: py_parser.getPythonAtrributeFuncs(py_tree)
"""
@given(st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=10))
@settings(max_examples=40)
def fuzz_getPythonAtrributeFuncs(str_list):
    content = "\n".join(str_list)
    tmp_file = ARTIFACT_DIR / "tmp_fuzz2.py"
    tmp_file.write_text(content)

    try:
        tree = py_parser.getPythonParseObject(str(tmp_file))
        py_parser.getPythonAtrributeFuncs(tree)
    except Exception:
        logger.exception(f"[getPythonAtrributeFuncs] Crash on: {content}")
        raise

"""
3. FUZZ: lint_engine.getIncompleteLoggingCount(path)
"""
def fuzz_getIncompleteLoggingCount():
    for i in range(40):
        if random.random() < 0.5:
            path = ARTIFACT_DIR / f"tmp_bad_{i}.py"
            random_text = "".join(random.choice("abc{}()[]") for _ in range(300))
            path.write_text(random_text)
        else:
            path = ARTIFACT_DIR / f"nonexistent_{random.randint(1000,9999)}.py"

        try:
            lint_engine.getIncompleteLoggingCount(str(path))
        except Exception:
            logger.exception(f"[getIncompleteLoggingCount] Crash on path: {path}")

"""
4. FUZZ: git.repo.miner.getGitRepos(input_file)
"""
def fuzz_getGitRepos():
    charset = "abcdefghijklmnopqrstuvwxyz/:.@#$_-0123456789"

    for i in range(40):
        tmp_file = ARTIFACT_DIR / f"repo_fuzz_{i}.txt"
        content = "\n".join(
            "".join(random.choice(charset) for _ in range(random.randint(5, 80)))
            for _ in range(random.randint(1, 10))
        )
        tmp_file.write_text(content)

        try:
            gitminer.getGitRepos(str(tmp_file))
        except Exception:
            logger.exception(f"[getGitRepos] Crash on input: {content}")


"""
5. FUZZ: frequency.getEventFrequency(input_file)
"""
def fuzz_getEventFrequency():
    """Fuzz CSV-like inputs with random malformed fields."""
    tokens = ["0", "1", "2", "error", ",", ";", ":", "NaN", "???"]

    for i in range(40):
        tmp_file = ARTIFACT_DIR / f"freq_fuzz_{i}.txt"
        content = "\n".join(
            "".join(random.choice(tokens) for _ in range(random.randint(3, 15)))
            for _ in range(random.randint(1, 10))
        )
        tmp_file.write_text(content)

        try:
            freq.getEventFrequency(str(tmp_file))
        except Exception:
            logger.exception(f"[getEventFrequency] Crash on: {content}")

if __name__ == "__main__":
    print("Running fuzz tests...")

    # Hypothesis tests
    fuzz_getPythonParseObject()
    fuzz_getPythonAtrributeFuncs()

    # Manual fuzzers
    fuzz_getIncompleteLoggingCount()
    fuzz_getGitRepos()
    fuzz_getEventFrequency()

    print("Fuzzing complete. Check fuzz_artifacts/ for all outputs.")
