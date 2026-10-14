# TaskFlow — To-Do List Manager

A desktop task management application built with **Python, Tkinter, and SQLite**. TaskFlow helps users organize tasks, manage deadlines, set priorities, categorize work, and monitor their progress through a dashboard.

## Features

- **Task Management (CRUD):** Create, view, update, complete, and delete tasks.
- **Persistent Storage:** Save task information locally using SQLite.
- **Due Dates:** Assign deadlines and identify overdue tasks.
- **Priority Levels:** Classify tasks as High, Medium, or Low.
- **Categories:** Organize tasks by work, study, personal activities, or custom categories.
- **Search and Filtering:** Find tasks by title and filter by status, priority, and category.
- **Dashboard:** Display total, completed, pending, overdue, and high-priority tasks, plus completion statistics and category totals.
- **Database Migration:** Add missing database columns while preserving existing task records.
- **Desktop Interface:** Use a graphical interface built with Tkinter.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Tkinter / ttk | Desktop graphical user interface |
| SQLite | Local database and persistent storage |
| SQL | Data retrieval and CRUD operations |
| Git and GitHub | Version control and project hosting |


## Requirements

- Python 3.10 or newer recommended.
- A Python installation with Tkinter support.
- No third-party Python packages are required by the application.

SQLite is accessed through Python's built-in `sqlite3` module.

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/eksllbrs-xx/taskflow-todo-manager.git
cd taskflow-todo-manager
```



### 2. Open the project in PyCharm

Open the project folder in PyCharm and select a compatible Python interpreter.

### 3. Run the application

```bash
python main.py
```

On Windows, you can also use:

```bash
py main.py
```

The application uses `todo.db` in the same directory as `main.py`. If the database does not exist, it creates the database and initializes the required table automatically.

### 4. Start managing tasks

Use the graphical interface to create tasks, set due dates, select priorities, organize categories, filter records, and track completion progress.

## Database Design

The application uses a local SQLite database with a `tasks` table.

| Column | Description |
|---|---|
| `id` | Unique task identifier |
| `title` | Task description |
| `completed` | Completion status |
| `due_date` | Optional deadline in `YYYY-MM-DD` format |
| `priority` | High, Medium, or Low |
| `category` | Task category |

The database initialization routine checks the existing table structure and adds missing columns when necessary. Existing records are retained during the supported schema migration.

## Testing Checklist

- [ ] Add a new task.
- [ ] View existing tasks.
- [ ] Edit a task and save changes.
- [ ] Mark a task as completed.
- [ ] Delete a task after confirmation.
- [ ] Search for a task by title.
- [ ] Filter tasks by status, priority, and category.
- [ ] Verify overdue task detection.
- [ ] Compare dashboard statistics with saved records.
- [ ] Restart the application and verify data persistence.
- [ ] Confirm that invalid dates and empty titles are rejected.

These are manual verification steps. Add automated tests as a future improvement.

## Project Structure

```text
taskflow-todo-manager/
├── main.py
├── README.md
├── requirements.txt
├── .gitignore
└── screenshots/
    ├── dashboard.png
    ├── task-management.png
    ├── search-filter.png
    └── summary-dashboard.png
```

## Future Improvements

- Automated unit and integration tests.
- Improved task completion progress visualization.
- Task sorting and additional dashboard statistics.
- Export tasks to CSV.
- Packaging as a standalone Windows executable.
- Additional accessibility and interface improvements.

## Learning Outcomes

This project demonstrates practical experience with Python programming, GUI development, SQL queries, SQLite persistence, database schema migration, input validation, and version control.

## License

This project is intended for educational and portfolio use. Add a license file if you decide to distribute it publicly.

---

**Author:** ERIKA LLABRE

**Project:** TaskFlow — To-Do List Manager

**Technologies:** Python · Tkinter · SQLite · SQL · Git
