
# TaskFlow — To-Do List Manager

A desktop task management application built with Python, Tkinter, and SQLite.

## Features

- Create, view, edit, complete, and delete tasks.
- Persist tasks using SQLite.
- Assign due dates and detect overdue tasks.
- Set High, Medium, or Low priorities.
- Organize tasks by category.
- Search and filter by title, status, priority, and category.
- View task summary statistics and completion rates.
- Migrate supported existing database schemas safely.

## Technology Stack

- Python
- Tkinter and ttk
- SQLite and SQL
- Git and GitHub

## Requirements

- Python 3.10 or newer recommended.
- Tkinter support in your Python installation.
- No third-party packages required.

## How to Run

1. Clone or download this repository.
2. Open the project in PyCharm.
3. Select a compatible Python interpreter.
4. Run `main.py`.

The application creates `todo.db` next to `main.py` when needed.

## Project Structure

```text
to-do-list-manager/
├── main.py
├── README.md
├── requirements.txt
├── .gitignore
└── screenshots/
```

## Testing

Manually verify CRUD operations, dates, priorities, categories, search, filtering, dashboard calculations, and persistence after restarting.

## Future Improvements

- Automated tests
- CSV export
- Additional dashboard visualizations
- Windows executable packaging
