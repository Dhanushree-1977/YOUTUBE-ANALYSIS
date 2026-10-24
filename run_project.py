"""
run_project.py - Master Pipeline Runner
========================================
Single entry point to run any or all modules of the YouTube Analysis project:
1. Fetch YouTube Channel Data & Today's Trending Videos
2. Analyze Video Performance & Today's Viral Trends
3. Reproduce PPTX Presentation Benchmark Dataset & Charts
4. Run Machine Learning Predictions & Sentiment Analysis
5. Launch Interactive Web Dashboard
"""

import sys
import os
import argparse
import subprocess

PYTHON_EXE = os.path.join(os.path.dirname(__file__), "venv", "Scripts", "python.exe")
if not os.path.exists(PYTHON_EXE):
    PYTHON_EXE = os.path.join(os.path.dirname(__file__), "venv", "bin", "python")
if not os.path.exists(PYTHON_EXE):
    PYTHON_EXE = sys.executable


def run_script(script_name, description):
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    print("\n" + "=" * 70)
    print(f"[*] RUNNING: {description} ({script_name})")
    print("=" * 70)
    result = subprocess.run([PYTHON_EXE, script_path])
    if result.returncode != 0:
        print(f"[!] Warning: {script_name} exited with code {result.returncode}")
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Master Runner for YouTube Analytics Platform")
    parser.add_argument("--all", action="store_true", help="Run the entire pipeline end-to-end")
    parser.add_argument("--fetch", action="store_true", help="Fetch channel and today's trending metadata")
    parser.add_argument("--analyze", action="store_true", help="Clean data and generate analytical charts")
    parser.add_argument("--benchmark", action="store_true", help="Reproduce PPTX presentation dataset and charts")
    parser.add_argument("--ml", action="store_true", help="Run ML view predictions and comment sentiment analysis")
    parser.add_argument("--test", action="store_true", help="Run automated test suite (tests/test_*.py)")
    parser.add_argument("--web", action="store_true", help="Launch interactive Web Dashboard")

    args = parser.parse_args()

    if args.test:
        print("\n" + "=" * 70)
        print("[*] RUNNING AUTOMATED TEST SUITE (unittest)")
        print("=" * 70)
        res = subprocess.run([PYTHON_EXE, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"])
        return res.returncode

    if not (args.all or args.fetch or args.analyze or args.benchmark or args.ml or args.web):
        args.all = True

    if args.all or args.fetch:
        run_script("fetch_data.py", "Step 1: YouTube Channel & Today's Trending Data Ingestion")

    if args.all or args.analyze:
        run_script("analyze_data.py", "Step 2: Video Performance & Today's Trends Analytics")

    if args.all or args.benchmark:
        run_script("presentation_benchmark.py", "Step 3: Presentation Benchmark Reproduction")

    if args.all or args.ml:
        run_script("advanced_analysis.py", "Step 4: ML Prediction & Sentiment Analysis")

    if args.web:
        run_script("app.py", "Step 5: Launch Web Dashboard")
    elif args.all:
        print("\n" + "=" * 70)
        print(" [SUCCESS] All analyses and charts generated successfully!")
        print(" To launch the interactive web dashboard, run:")
        print("   python run_project.py --web")
        print(" Or:")
        print("   python app.py")
        print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
