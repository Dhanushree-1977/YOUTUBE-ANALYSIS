# Contributing to YouTube Analytics & Trends Platform

Thank you for your interest in contributing to the **YouTube Analytics & Trends Platform**! We welcome contributions from developers, data scientists, and creators of all skill levels.

---

## 📋 Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

---

## 🛠️ Development Setup

### 1. Fork & Clone the Repository
```bash
git clone https://github.com/Dhanushree-1977/YOUTUBE-ANALYSIS.git
cd YOUTUBE-ANALYSIS
```

### 2. Create and Activate a Virtual Environment
```bash
# On Windows
python -m venv venv
.\venv\Scripts\activate

# On Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Setup Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(Optional)* Add your YouTube Data API v3 key from Google Cloud Console if you wish to run live data fetches. If left empty, the platform automatically runs against the included verified demo dataset.

---

## 🧪 Running Tests

Always ensure all unit tests pass before submitting a Pull Request:
```bash
# Using Python's standard test runner
python -m unittest discover tests

# Or using the master runner CLI
python run_project.py --test
```

---

## 🚀 Branching Strategy & Commits

1. **Create a Feature Branch:**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. **Commit Messages:**
   Follow conventional commits:
   - `feat: add new retention curve metric`
   - `fix: resolve zero-comment sentiment edge case`
   - `docs: update API endpoints in README`
   - `test: add unit test for Views/Day calculation`

3. **Submitting a Pull Request:**
   - Push your branch to GitHub.
   - Open a PR against the `main` branch.
   - Fill out the PR template with clear context and test results.

---

## 📜 Coding Guidelines

- Follow [PEP 8](https://peps.python.org/pep-0008/) style standards.
- Add docstrings to all newly introduced functions and classes.
- Ensure no data leakage occurs in ML pipelines (pre-publication features only for view predictors).
- Keep all unit tests decoupled and fast-running.
