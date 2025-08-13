# Contributing to Fash AI Agent

Thank you for your interest in contributing! This guide will help you set up the project, follow coding standards, and submit your contributions smoothly.

---

## 📌 Fork and Clone the Repository

1. **Fork** the repository by clicking the **Fork** button on GitHub.  
2. **Clone your fork locally**:
   ```bash
   git clone https://github.com/your-username/fash-ai-agent.git
   cd fash-ai-agent
Replace `your-username` with your GitHub username.

---

## ⚙️ Set Up the Development Environment

1. Make sure you have **Python 3.8 or above** installed.

2. Create and activate a **virtual environment** (recommended):

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate

3. Install dependencies:
   
   ```bash
   pip install -r requirements.txt

---
   
## 🔑 Configure Environment Variables

1. Create a `.env` file by copying from the example:

   ```bash
   copy .env.example .env   # Windows PowerShell

   cp .env.example .env   # macOS/Linux

2. Update `.env` with your API keys (e.g., OpenAI, SERP API) and other required secrets.

---

## 📝 Code Style Guidelines

- Follow **[PEP8](https://peps.python.org/pep-0008/)** for Python code style.
- Use **descriptive variable and function names**.
- Keep your code **modular** and **readable**.
- Use tools like [`flake8`](https://flake8.pycqa.org/) or [`black`](https://black.readthedocs.io/en/stable/) to lint and format your code.

---

## 🌱 Branch Naming Conventions

Use clear, descriptive branch names prefixed by the work type:

| Prefix      | Usage Example               |
|-------------|-----------------------------|
| `feature/`  | `feature/add-new-scraper`    |
| `bugfix/`   | `bugfix/fix-login-error`     |
| `docs/`     | `docs/update-readme`         |
| `refactor/` | `refactor/optimize-search`   |

Example:

```bash
git checkout -b feature/add-new-scraper
```

---

## 🚀 Pull Request Submission Process

1. **Fork** and **clone** the repo.
2. **Create a branch** following the naming conventions.
3. Make your changes with **meaningful commit messages** (e.g., `fix: resolve error in price tracking`).
4. Update documentation in `docs/api_docs.md` if your changes affect the API.
5. Run tests to ensure they pass: `pytest --cov=src tests/`.
6. **Push** your branch to your fork.
7. **Open a Pull Request (PR)** to the main repo's `main` branch.
8. Fill out the **PR description** with:
   - What was changed and why.
   - Related issue numbers (e.g., “Closes #123”).
   - How it was tested.
9. Keep PRs focused on a single change.
10. Respond to **review comments** and update your PR if needed.

---

## 📜 License

Contributions are subject to the [MIT License](LICENSE). Ensure your changes align with the project’s licensing terms.

---

## ❓ Support

For questions or issues, please open a [GitHub issue](https://github.com/Sunzzx/fash-ai-agent/issues).

---

## ✅ Thank You

Thank you for contributing to **Fash AI Agent**! Your efforts help improve this AI-powered shopping assistant for everyone.