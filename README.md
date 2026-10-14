# TaskFlow — To-Do List Manager

A desktop task management application built with Python, Tkinter, and SQLite.

## Features

- Create, view, edit, complete, and delete tasks.
- Store tasks persistently using SQLite.
- Assign due dates and detect overdue tasks.
- Set High, Medium, or Low priorities.
- Organize tasks by category.
- Search and filter tasks.
- View dashboard statistics and completion rates.
- Automatically migrate supported existing database schemas.

## Technologies

- Python
- Tkinter and ttk
- SQLite
- SQL
- Git and GitHub

## Requirements

- Python 3.10 or newer recommended.
- A Python installation with Tkinter support.
- No third-party Python packages required.

## How to Run

1. Clone or download this repository.
2. Open the project folder in PyCharm.
3. Select a compatible Python interpreter.
4. Run `main.py`.

The application creates `todo.db` beside `main.py` if the database does not exist.

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

Verify task creation, editing, completion, deletion, search, filtering, overdue detection, dashboard calculations, and persistence after restarting the application.

## Future Improvements

- Automated unit tests
- CSV export
- Additional dashboard visualizations
- Windows executable packaging

## Author

ERIKA LLABRES