# Evolution of Todo - Phase I: CLI Todo App

This document provides details for Phase I of the "Evolution of Todo" project, which is a command-line interface (CLI) application for managing tasks.

## 🎯 Project Overview

This phase implements a simple yet functional Todo application that runs entirely in the console. It's built with Python and uses an in-memory list to store tasks, meaning all data is cleared when the application closes. This phase laid the foundation for the project's evolution, focusing on core business logic and a clean, testable codebase.

## 🛠️ Tech Stack

- **Language**: Python 3.13+
- **Storage**: In-memory list (data is not persisted)
- **Testing**: `pytest` and `pytest-cov` for test coverage analysis.
- **Code Quality**: `ruff` for linting and formatting to ensure clean, consistent code.

## ✨ Features

This phase includes 5 core features and 3 enhanced features for a better user experience.

### ✅ Core Features
1.  **Add Tasks**: Users can add new tasks with a title, description, and priority.
2.  **View Tasks**: All tasks can be displayed, sorted by priority and grouped by their completion status.
3.  **Mark Complete/Incomplete**: Tasks can be toggled between complete and incomplete states.
4.  **Update Tasks**: Existing tasks can be modified, either partially or fully.
5.  **Delete Tasks**: Tasks can be removed from the list by their ID.

### ✅ Enhanced Features
1.  **Priority Levels**: Tasks can be assigned a priority of 'High', 'Medium', or 'Low'.
2.  **Input Validation**: The application validates user input to prevent errors.
3.  **Colored CLI Output**: Completed tasks are displayed in green for better visual distinction.

## 🚀 Getting Started

To run the Phase I CLI application, follow these steps:

### Prerequisites

- Python 3.13+
- `uv` Python package manager

### Setup and Execution

1.  **Navigate to the Phase I directory**:
    ```bash
    cd phase-1-cli
    ```

2.  **Create a virtual environment and install dependencies**:
    ```bash
    uv venv
    source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
    uv pip install pytest pytest-cov ruff
    ```

3.  **Run the CLI application**:
    ```bash
    python src/main.py
    ```

4.  **Run tests (82% coverage)**:
    ```bash
    pytest --cov=src --cov-report=term-missing
    ```

## 📂 Project Structure

```
phase-1-cli/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── cli/
│   │   └── ... (CLI interaction logic)
│   ├── models/
│   │   └── ... (Task data model)
│   └── services/
│       └── ... (Business logic for task management)
└── tests/
    ├── __init__.py
    ├── integration/
    │   └── ...
    └── unit/
        └── ...
```
