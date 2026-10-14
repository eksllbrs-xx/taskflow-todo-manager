
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from contextlib import contextmanager
from datetime import date


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

DATABASE_FILE = Path(__file__).resolve().parent / "todo.db"

PRIORITIES = ("High", "Medium", "Low")
STATUSES = ("All", "Pending", "Completed")
DEFAULT_CATEGORY = "General"


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

@contextmanager
def connect_db():
    """Manage SQLite connections and transactions."""
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database():
    """Create or safely upgrade the existing tasks table."""
    with connect_db() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0
            )
        """)

        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(tasks)"
            ).fetchall()
        }

        migrations = {
            "due_date": "ALTER TABLE tasks ADD COLUMN due_date TEXT",
            "priority": (
                "ALTER TABLE tasks ADD COLUMN priority "
                "TEXT NOT NULL DEFAULT 'Medium'"
            ),
            "category": (
                "ALTER TABLE tasks ADD COLUMN category "
                "TEXT NOT NULL DEFAULT 'General'"
            ),
        }

        for name, sql in migrations.items():
            if name not in columns:
                connection.execute(sql)

        # Normalize existing values without removing any tasks.
        connection.execute("""
            UPDATE tasks
            SET priority = 'Medium'
            WHERE priority IS NULL
               OR priority NOT IN ('High', 'Medium', 'Low')
        """)

        connection.execute("""
            UPDATE tasks
            SET category = 'General'
            WHERE category IS NULL OR TRIM(category) = ''
        """)


def fetch_tasks(keyword="", status="All",
                priority="All", category="All"):
    """Retrieve tasks matching the selected filters."""
    conditions = []
    parameters = []

    if keyword.strip():
        conditions.append("title LIKE ?")
        parameters.append(f"%{keyword.strip()}%")

    if status == "Pending":
        conditions.append("completed = 0")
    elif status == "Completed":
        conditions.append("completed = 1")

    if priority != "All":
        conditions.append("priority = ?")
        parameters.append(priority)

    if category != "All":
        conditions.append("LOWER(category) = LOWER(?)")
        parameters.append(category)

    sql = "SELECT * FROM tasks"

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += """
        ORDER BY
            completed ASC,
            CASE priority
                WHEN 'High' THEN 1
                WHEN 'Medium' THEN 2
                ELSE 3
            END,
            CASE WHEN due_date IS NULL THEN 1 ELSE 0 END,
            due_date ASC,
            id ASC
    """

    with connect_db() as connection:
        return connection.execute(sql, parameters).fetchall()


def fetch_task(task_id):
    with connect_db() as connection:
        return connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,)
        ).fetchone()


# --------------------------------------------------
# VALIDATION AND DATE HELPERS
# --------------------------------------------------

def validate_due_date(value):
    """Return a normalized date or None; reject invalid dates."""
    value = value.strip()

    if not value:
        return None

    parsed = date.fromisoformat(value)

    if parsed.isoformat() != value:
        raise ValueError("Use the YYYY-MM-DD date format.")

    return value


def deadline_status(task):
    if task["completed"]:
        return "Completed"

    due_date = task["due_date"]

    if not due_date:
        return "No deadline"

    try:
        due = date.fromisoformat(due_date)
    except ValueError:
        return "Invalid date"

    today = date.today()

    if due < today:
        return "OVERDUE"
    if due == today:
        return "Due today"

    return "Upcoming"


# --------------------------------------------------
# MAIN APPLICATION
# --------------------------------------------------

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List Manager | Version 4")
        self.root.geometry("1180x760")
        self.root.minsize(900, 620)

        self.selected_id = None

        self.setup_styles()
        self.build_interface()
        self.refresh_categories()
        self.refresh_tasks()
        self.refresh_dashboard()

    def setup_styles(self):
        """Apply a modern, consistent desktop theme."""
        self.colors = {
            "navy": "#172554",
            "navy_light": "#243B6B",
            "blue": "#4169E1",
            "blue_hover": "#3154C5",
            "background": "#F4F6FB",
            "white": "#FFFFFF",
            "text": "#1E293B",
            "muted": "#64748B",
            "border": "#E2E8F0",
            "green": "#15803D",
            "green_bg": "#DCFCE7",
            "red": "#B91C1C",
            "red_bg": "#FEE2E2",
            "orange": "#B45309",
            "orange_bg": "#FEF3C7",
            "purple": "#6D28D9",
            "purple_bg": "#EDE9FE",
        }

        self.root.configure(bg=self.colors["background"])
        self.root.title("TaskFlow | To-Do List Manager")
        self.root.geometry("1280x820")
        self.root.minsize(1020, 680)

        style = ttk.Style()

        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure(
            "TFrame",
            background=self.colors["background"]
        )

        style.configure(
            "Card.TFrame",
            background=self.colors["white"]
        )

        style.configure(
            "TLabel",
            background=self.colors["background"],
            foreground=self.colors["text"],
            font=("Segoe UI", 10)
        )

        style.configure(
            "Title.TLabel",
            background=self.colors["background"],
            foreground=self.colors["text"],
            font=("Segoe UI", 25, "bold")
        )

        style.configure(
            "Subtitle.TLabel",
            background=self.colors["background"],
            foreground=self.colors["muted"],
            font=("Segoe UI", 10)
        )

        style.configure(
            "Section.TLabel",
            background=self.colors["white"],
            foreground=self.colors["text"],
            font=("Segoe UI", 12, "bold")
        )

        style.configure(
            "TButton",
            font=("Segoe UI", 9),
            padding=(12, 8),
            background=self.colors["white"],
            foreground=self.colors["text"],
            borderwidth=1
        )

        style.map(
            "TButton",
            background=[
                ("active", "#E8EDF7"),
                ("disabled", "#F1F5F9")
            ]
        )

        style.configure(
            "Accent.TButton",
            background=self.colors["blue"],
            foreground=self.colors["white"],
            font=("Segoe UI", 9, "bold"),
            padding=(13, 9),
            borderwidth=0
        )

        style.map(
            "Accent.TButton",
            background=[
                ("active", self.colors["blue_hover"]),
                ("disabled", "#94A3B8")
            ],
            foreground=[("disabled", "#FFFFFF")]
        )

        style.configure(
            "Treeview",
            background=self.colors["white"],
            fieldbackground=self.colors["white"],
            foreground=self.colors["text"],
            font=("Segoe UI", 10),
            rowheight=38,
            borderwidth=0
        )

        style.configure(
            "Treeview.Heading",
            background="#EEF2F8",
            foreground="#475569",
            font=("Segoe UI", 9, "bold"),
            padding=(8, 12),
            relief="flat"
        )

        style.map(
            "Treeview",
            background=[("selected", "#DBEAFE")],
            foreground=[("selected", "#1D4ED8")]
        )

        style.configure(
            "TEntry",
            padding=8,
            fieldbackground=self.colors["white"]
        )

        style.configure(
            "TCombobox",
            padding=7,
            fieldbackground=self.colors["white"]
        )

    def build_interface(self):
        """Build the redesigned TaskFlow desktop interface."""

        C = self.colors

        # ==========================
        # MAIN WINDOW LAYOUT
        # ==========================

        shell = tk.Frame(self.root, bg=C["background"])
        shell.pack(fill="both", expand=True)

        # ==========================
        # LEFT SIDEBAR
        # ==========================

        sidebar = tk.Frame(
            shell,
            bg=C["navy"],
            width=220
        )
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        brand = tk.Frame(sidebar, bg=C["navy"])
        brand.pack(fill="x", padx=20, pady=(28, 34))

        tk.Label(
            brand,
            text="TF",
            bg=C["blue"],
            fg=C["white"],
            font=("Segoe UI", 17, "bold"),
            width=3,
            height=1
        ).pack(anchor="w", pady=(0, 12))

        tk.Label(
            brand,
            text="TaskFlow",
            bg=C["navy"],
            fg=C["white"],
            font=("Segoe UI", 19, "bold")
        ).pack(anchor="w")

        tk.Label(
            brand,
            text="PERSONAL TASK MANAGER",
            bg=C["navy"],
            fg="#A5B4D4",
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", pady=(4, 0))

        tk.Label(
            sidebar,
            text="WORKSPACE",
            bg=C["navy"],
            fg="#94A3B8",
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", padx=22, pady=(0, 10))

        def sidebar_button(text, command, active=False):
            button = tk.Button(
                sidebar,
                text=text,
                command=command,
                anchor="w",
                padx=18,
                pady=11,
                relief="flat",
                bd=0,
                cursor="hand2",
                bg=C["navy_light"] if active else C["navy"],
                fg=C["white"] if active else "#CBD5E1",
                activebackground=C["navy_light"],
                activeforeground=C["white"],
                font=("Segoe UI", 10, "bold" if active else "normal")
            )
            button.pack(fill="x", padx=10, pady=2)
            return button

        sidebar_button(
            "▦   Dashboard",
            self.show_dashboard,
            active=True
        )

        sidebar_button(
            "☷   All Tasks",
            lambda: self.set_sidebar_status("All")
        )

        sidebar_button(
            "◷   Pending",
            lambda: self.set_sidebar_status("Pending")
        )

        sidebar_button(
            "✓   Completed",
            lambda: self.set_sidebar_status("Completed")
        )

        tk.Frame(
            sidebar,
            bg="#354568",
            height=1
        ).pack(fill="x", padx=18, pady=24)

        tk.Label(
            sidebar,
            text="QUICK ACTION",
            bg=C["navy"],
            fg="#94A3B8",
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", padx=22, pady=(0, 10))

        sidebar_button(
            "＋   New Task",
            self.start_new_task
        )

        sidebar_button(
            "⟳   Reset Filters",
            self.reset_filters
        )

        # Bottom sidebar information
        bottom = tk.Frame(sidebar, bg=C["navy"])
        bottom.pack(side="bottom", fill="x", padx=20, pady=22)

        tk.Frame(
            bottom,
            bg="#354568",
            height=1
        ).pack(fill="x", pady=(0, 12))

        tk.Label(
            bottom,
            text="TASKFLOW DESKTOP",
            bg=C["navy"],
            fg="#CBD5E1",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w")

        tk.Label(
            bottom,
            text="Python + SQLite",
            bg=C["navy"],
            fg="#94A3B8",
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(4, 0))

        # ==========================
        # MAIN CONTENT AREA
        # ==========================

        content = tk.Frame(shell, bg=C["background"])
        content.pack(side="left", fill="both", expand=True)

        page = tk.Frame(content, bg=C["background"])
        page.pack(fill="both", expand=True, padx=24, pady=22)

        # Header
        header = tk.Frame(page, bg=C["background"])
        header.pack(fill="x", pady=(0, 18))

        header_text = tk.Frame(header, bg=C["background"])
        header_text.pack(side="left", fill="x", expand=True)

        ttk.Label(
            header_text,
            text="Good day!",
            style="Title.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            header_text,
            text="Plan your work. Prioritize what matters. Get things done.",
            style="Subtitle.TLabel"
        ).pack(anchor="w", pady=(5, 0))

        ttk.Button(
            header,
            text="＋  Add New Task",
            style="Accent.TButton",
            command=self.start_new_task
        ).pack(side="right", anchor="center")

        # ==========================
        # DASHBOARD SUMMARY CARDS
        # ==========================

        dashboard = tk.Frame(page, bg=C["background"])
        dashboard.pack(fill="x", pady=(0, 12))

        self.metric_labels = {}

        metric_info = [
            ("total", "TOTAL TASKS", "#4169E1"),
            ("completed", "COMPLETED", "#15803D"),
            ("pending", "PENDING", "#B45309"),
            ("overdue", "OVERDUE", "#B91C1C"),
            ("high", "HIGH PRIORITY", "#6D28D9"),
        ]

        for index, (key, label, accent) in enumerate(metric_info):
            dashboard.columnconfigure(index, weight=1)

            card = tk.Frame(
                dashboard,
                bg=C["white"],
                highlightbackground=C["border"],
                highlightthickness=1
            )
            card.grid(
                row=0,
                column=index,
                sticky="nsew",
                padx=(0 if index == 0 else 6, 0)
            )

            tk.Frame(
                card,
                bg=accent,
                height=4
            ).pack(fill="x")

            inner = tk.Frame(card, bg=C["white"])
            inner.pack(fill="both", padx=12, pady=12)

            tk.Label(
                inner,
                text=label,
                bg=C["white"],
                fg=C["muted"],
                font=("Segoe UI", 8, "bold")
            ).pack(anchor="w")

            value = tk.Label(
                inner,
                text="0",
                bg=C["white"],
                fg=C["text"],
                font=("Segoe UI", 23, "bold")
            )
            value.pack(anchor="w", pady=(6, 0))

            self.metric_labels[key] = value

        self.completion_label = tk.Label(
            page,
            text="Completion rate: 0%",
            bg=C["background"],
            fg=C["muted"],
            font=("Segoe UI", 9)
        )
        self.completion_label.pack(anchor="w", pady=(0, 14))

        # ==========================
        # TASK EDITOR
        # ==========================

        form = tk.Frame(
            page,
            bg=C["white"],
            highlightbackground=C["border"],
            highlightthickness=1
        )
        form.pack(fill="x", pady=(0, 14))

        form_inner = tk.Frame(form, bg=C["white"])
        form_inner.pack(fill="x", padx=16, pady=14)

        tk.Label(
            form_inner,
            text="Task details",
            bg=C["white"],
            fg=C["text"],
            font=("Segoe UI", 12, "bold")
        ).grid(row=0, column=0, columnspan=4,
               sticky="w", pady=(0, 12))

        for column in range(4):
            form_inner.columnconfigure(column, weight=1)

        def field_label(text, row, column):
            tk.Label(
                form_inner,
                text=text,
                bg=C["white"],
                fg=C["muted"],
                font=("Segoe UI", 9, "bold")
            ).grid(
                row=row, column=column,
                sticky="w", padx=(0, 12), pady=(0, 5)
            )

        field_label("TASK TITLE", 1, 0)
        field_label("DUE DATE", 1, 1)
        field_label("PRIORITY", 1, 2)
        field_label("CATEGORY", 1, 3)

        self.title_var = tk.StringVar()
        self.due_var = tk.StringVar()
        self.priority_var = tk.StringVar(value="Medium")
        self.category_var = tk.StringVar(value="General")

        self.title_entry = ttk.Entry(
            form_inner,
            textvariable=self.title_var
        )
        self.title_entry.grid(
            row=2, column=0, sticky="ew",
            padx=(0, 12), pady=(0, 12)
        )

        ttk.Entry(
            form_inner,
            textvariable=self.due_var
        ).grid(
            row=2, column=1, sticky="ew",
            padx=(0, 12), pady=(0, 12)
        )

        ttk.Combobox(
            form_inner,
            textvariable=self.priority_var,
            values=PRIORITIES,
            state="readonly"
        ).grid(
            row=2, column=2, sticky="ew",
            padx=(0, 12), pady=(0, 12)
        )

        ttk.Entry(
            form_inner,
            textvariable=self.category_var
        ).grid(
            row=2, column=3, sticky="ew",
            pady=(0, 12)
        )

        action_row = tk.Frame(form_inner, bg=C["white"])
        action_row.grid(
            row=3, column=0, columnspan=4, sticky="w"
        )

        ttk.Button(
            action_row,
            text="＋ Add Task",
            style="Accent.TButton",
            command=self.add_task
        ).pack(side="left", padx=(0, 7))

        ttk.Button(
            action_row,
            text="Update",
            command=self.update_task
        ).pack(side="left", padx=4)

        ttk.Button(
            action_row,
            text="✓ Complete",
            command=self.complete_task
        ).pack(side="left", padx=4)

        ttk.Button(
            action_row,
            text="Delete",
            command=self.delete_task
        ).pack(side="left", padx=4)

        ttk.Button(
            action_row,
            text="Clear",
            command=self.clear_form
        ).pack(side="left", padx=4)

        # ==========================
        # SEARCH AND FILTERS
        # ==========================

        filters = tk.Frame(
            page,
            bg=C["white"],
            highlightbackground=C["border"],
            highlightthickness=1
        )
        filters.pack(fill="x", pady=(0, 12))

        filter_inner = tk.Frame(filters, bg=C["white"])
        filter_inner.pack(fill="x", padx=14, pady=12)

        tk.Label(
            filter_inner,
            text="Find your tasks",
            bg=C["white"],
            fg=C["text"],
            font=("Segoe UI", 11, "bold")
        ).grid(row=0, column=0, columnspan=5,
               sticky="w", pady=(0, 10))

        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar(value="All")
        self.filter_priority_var = tk.StringVar(value="All")
        self.filter_category_var = tk.StringVar(value="All")

        filter_fields = [
            ("Search title", self.search_var, None, 25),
            ("Status", self.status_var, STATUSES, 13),
            (
                "Priority",
                self.filter_priority_var,
                ("All",) + PRIORITIES,
                13
            ),
        ]

        for index, (label, variable, values, width) in enumerate(
                filter_fields
        ):
            tk.Label(
                filter_inner,
                text=label,
                bg=C["white"],
                fg=C["muted"],
                font=("Segoe UI", 9)
            ).grid(
                row=1, column=index, sticky="w",
                padx=(0, 12), pady=(0, 4)
            )

            if values is None:
                widget = ttk.Entry(
                    filter_inner,
                    textvariable=variable,
                    width=width
                )
            else:
                widget = ttk.Combobox(
                    filter_inner,
                    textvariable=variable,
                    values=values,
                    state="readonly",
                    width=width
                )

            widget.grid(
                row=2, column=index, sticky="ew",
                padx=(0, 12)
            )

        tk.Label(
            filter_inner,
            text="Category",
            bg=C["white"],
            fg=C["muted"],
            font=("Segoe UI", 9)
        ).grid(row=1, column=3, sticky="w", pady=(0, 4))

        self.category_filter = ttk.Combobox(
            filter_inner,
            textvariable=self.filter_category_var,
            values=("All",),
            state="readonly",
            width=15
        )
        self.category_filter.grid(
            row=2, column=3, sticky="ew", padx=(0, 12)
        )

        ttk.Button(
            filter_inner,
            text="Reset",
            command=self.reset_filters
        ).grid(row=2, column=4, sticky="e")

        for column in range(4):
            filter_inner.columnconfigure(column, weight=1)

        # ==========================
        # TASK TABLE
        # ==========================

        table_card = tk.Frame(
            page,
            bg=C["white"],
            highlightbackground=C["border"],
            highlightthickness=1
        )
        table_card.pack(fill="both", expand=True)

        table_header = tk.Frame(table_card, bg=C["white"])
        table_header.pack(fill="x", padx=14, pady=(12, 8))

        tk.Label(
            table_header,
            text="Your task list",
            bg=C["white"],
            fg=C["text"],
            font=("Segoe UI", 12, "bold")
        ).pack(side="left")

        table_columns = (
            "id", "title", "status", "priority",
            "category", "due_date", "deadline"
        )

        table_container = tk.Frame(table_card, bg=C["white"])
        table_container.pack(
            fill="both", expand=True, padx=12, pady=(0, 10)
        )

        self.tree = ttk.Treeview(
            table_container,
            columns=table_columns,
            show="headings",
            selectmode="browse"
        )

        headings = {
            "id": ("ID", 48),
            "title": ("Task", 230),
            "status": ("Status", 90),
            "priority": ("Priority", 90),
            "category": ("Category", 115),
            "due_date": ("Due date", 105),
            "deadline": ("Deadline", 110),
        }

        for column, (heading, width) in headings.items():
            self.tree.heading(column, text=heading)
            self.tree.column(
                column,
                width=width,
                minwidth=45,
                anchor="w",
                stretch=(column == "title")
            )

        scrollbar = ttk.Scrollbar(
            table_container,
            orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Priority and deadline indicators
        self.tree.tag_configure(
            "overdue", foreground=C["red"]
        )
        self.tree.tag_configure(
            "completed", foreground=C["muted"]
        )
        self.tree.tag_configure(
            "high", foreground=C["orange"]
        )

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.on_task_select
        )

        # ==========================
        # FOOTER
        # ==========================

        self.footer_var = tk.StringVar(value="Ready")

        footer = tk.Frame(page, bg=C["background"])
        footer.pack(fill="x", pady=(9, 0))

        tk.Label(
            footer,
            textvariable=self.footer_var,
            bg=C["background"],
            fg=C["muted"],
            font=("Segoe UI", 9)
        ).pack(side="left")

        tk.Label(
            footer,
            text="TaskFlow  •  Local SQLite storage",
            bg=C["background"],
            fg=C["muted"],
            font=("Segoe UI", 9)
        ).pack(side="right")

        # Live search and filter behavior
        self.search_var.trace_add(
            "write", self.on_filter_change
        )
        self.status_var.trace_add(
            "write", self.on_filter_change
        )
        self.filter_priority_var.trace_add(
            "write", self.on_filter_change
        )
        self.filter_category_var.trace_add(
            "write", self.on_filter_change
        )

    def set_sidebar_status(self, status):
        """Filter the task list from sidebar navigation."""
        self.status_var.set(status)

    def show_dashboard(self):
        """Show all tasks and refresh the dashboard."""
        self.reset_filters()
        self.refresh_dashboard()
        self.footer_var.set("Dashboard overview")

    def start_new_task(self):
        """Prepare the form for a new task."""
        self.clear_form()
        self.footer_var.set("Ready to create a new task.")

    # --------------------------------------------------
    # TASK FORM
    # --------------------------------------------------

    def validate_form(self):
        title = self.title_var.get().strip()
        category = self.category_var.get().strip()
        priority = self.priority_var.get()

        if not title:
            messagebox.showwarning(
                "Missing title",
                "Please enter a task title."
            )
            return None

        if not category:
            messagebox.showwarning(
                "Missing category",
                "Please enter a task category."
            )
            return None

        if priority not in PRIORITIES:
            messagebox.showwarning(
                "Invalid priority",
                "Choose High, Medium, or Low."
            )
            return None

        try:
            due_date = validate_due_date(
                self.due_var.get()
            )
        except ValueError:
            messagebox.showwarning(
                "Invalid date",
                "Enter a valid date using YYYY-MM-DD, "
                "or leave it blank."
            )
            return None

        return title, due_date, priority, category

    def add_task(self):
        values = self.validate_form()

        if values is None:
            return

        try:
            with connect_db() as connection:
                connection.execute("""
                    INSERT INTO tasks
                        (title, due_date, priority, category)
                    VALUES (?, ?, ?, ?)
                """, values)

            self.after_task_change()
            self.clear_form()
            self.footer_var.set("Task added successfully.")

        except sqlite3.Error as error:
            messagebox.showerror(
                "Database error", str(error)
            )

    def update_task(self):
        if self.selected_id is None:
            messagebox.showinfo(
                "Select a task",
                "Select a task from the table first."
            )
            return

        values = self.validate_form()

        if values is None:
            return

        try:
            with connect_db() as connection:
                cursor = connection.execute("""
                    UPDATE tasks
                    SET title = ?,
                        due_date = ?,
                        priority = ?,
                        category = ?
                    WHERE id = ?
                """, (*values, self.selected_id))

                if cursor.rowcount == 0:
                    messagebox.showwarning(
                        "Task not found",
                        "This task no longer exists."
                    )
                    self.after_task_change()
                    return

            self.after_task_change()
            self.clear_form()
            self.footer_var.set("Task updated successfully.")

        except sqlite3.Error as error:
            messagebox.showerror(
                "Database error", str(error)
            )

    def complete_task(self):
        if self.selected_id is None:
            messagebox.showinfo(
                "Select a task",
                "Select a task from the table first."
            )
            return

        task = fetch_task(self.selected_id)

        if task is None:
            messagebox.showwarning(
                "Task not found",
                "This task no longer exists."
            )
            self.after_task_change()
            return

        if task["completed"]:
            messagebox.showinfo(
                "Already completed",
                "This task is already completed."
            )
            return

        try:
            with connect_db() as connection:
                connection.execute(
                    "UPDATE tasks SET completed = 1 WHERE id = ?",
                    (self.selected_id,)
                )

            self.after_task_change()
            self.clear_form()
            self.footer_var.set("Task marked as completed.")

        except sqlite3.Error as error:
            messagebox.showerror(
                "Database error", str(error)
            )

    def delete_task(self):
        if self.selected_id is None:
            messagebox.showinfo(
                "Select a task",
                "Select a task from the table first."
            )
            return

        task = fetch_task(self.selected_id)

        if task is None:
            messagebox.showwarning(
                "Task not found",
                "This task no longer exists."
            )
            self.after_task_change()
            return

        if not messagebox.askyesno(
            "Confirm deletion",
            f"Delete this task?\n\n{task['title']}"
        ):
            return

        try:
            with connect_db() as connection:
                connection.execute(
                    "DELETE FROM tasks WHERE id = ?",
                    (self.selected_id,)
                )

            self.after_task_change()
            self.clear_form()
            self.footer_var.set("Task deleted successfully.")

        except sqlite3.Error as error:
            messagebox.showerror(
                "Database error", str(error)
            )

    def clear_form(self):
        self.selected_id = None

        self.title_var.set("")
        self.due_var.set("")
        self.priority_var.set("Medium")
        self.category_var.set("General")

        for selected in self.tree.selection():
            self.tree.selection_remove(selected)

        self.title_entry.focus_set()

    def on_task_select(self, _event=None):
        selected = self.tree.selection()

        if not selected:
            return

        task_id = int(selected[0])
        task = fetch_task(task_id)

        if task is None:
            return

        self.selected_id = task_id
        self.title_var.set(task["title"])
        self.due_var.set(task["due_date"] or "")
        self.priority_var.set(task["priority"])
        self.category_var.set(task["category"])

    # --------------------------------------------------
    # SEARCH AND FILTERS
    # --------------------------------------------------

    def on_filter_change(self, *_args):
        self.refresh_tasks()

    def reset_filters(self):
        self.search_var.set("")
        self.status_var.set("All")
        self.filter_priority_var.set("All")
        self.filter_category_var.set("All")

    def refresh_categories(self):
        with connect_db() as connection:
            categories = connection.execute("""
                SELECT DISTINCT category
                FROM tasks
                WHERE category IS NOT NULL
                  AND TRIM(category) <> ''
                ORDER BY category COLLATE NOCASE
            """).fetchall()

        values = ["All"] + [
            row["category"] for row in categories
        ]

        self.category_filter["values"] = values

        if self.filter_category_var.get() not in values:
            self.filter_category_var.set("All")

    def refresh_tasks(self):
        try:
            tasks = fetch_tasks(
                keyword=self.search_var.get(),
                status=self.status_var.get(),
                priority=self.filter_priority_var.get(),
                category=self.filter_category_var.get()
            )

            for item in self.tree.get_children():
                self.tree.delete(item)

            for task in tasks:
                status = (
                    "Completed" if task["completed"]
                    else "Pending"
                )

                deadline = deadline_status(task)

                if task["completed"]:
                    tag = "completed"
                elif deadline == "OVERDUE":
                    tag = "overdue"
                elif task["priority"] == "High":
                    tag = "high"
                else:
                    tag = ""

                self.tree.insert(
                    "",
                    "end",
                    iid=str(task["id"]),
                    values=(
                        task["id"],
                        task["title"],
                        status,
                        task["priority"],
                        task["category"],
                        task["due_date"] or "—",
                        deadline
                    ),
                    tags=(tag,) if tag else ()
                )

            self.footer_var.set(
                f"Showing {len(tasks)} matching task(s)."
            )

        except sqlite3.Error as error:
            messagebox.showerror(
                "Database error", str(error)
            )

    # --------------------------------------------------
    # SUMMARY DASHBOARD
    # --------------------------------------------------

    def refresh_dashboard(self):
        today = date.today().isoformat()

        with connect_db() as connection:
            stats = connection.execute("""
                SELECT
                    COUNT(*) AS total,
                    COALESCE(SUM(
                        CASE WHEN completed = 1
                        THEN 1 ELSE 0 END
                    ), 0) AS completed,
                    COALESCE(SUM(
                        CASE WHEN completed = 0
                        THEN 1 ELSE 0 END
                    ), 0) AS pending,
                    COALESCE(SUM(
                        CASE
                            WHEN completed = 0
                             AND due_date IS NOT NULL
                             AND due_date < ?
                            THEN 1 ELSE 0
                        END
                    ), 0) AS overdue,
                    COALESCE(SUM(
                        CASE
                            WHEN completed = 0
                             AND priority = 'High'
                            THEN 1 ELSE 0
                        END
                    ), 0) AS high
                FROM tasks
            """, (today,)).fetchone()

            categories = connection.execute("""
                SELECT category, COUNT(*) AS total
                FROM tasks
                GROUP BY category
                ORDER BY total DESC, category
            """).fetchall()

        for key in self.metric_labels:
            self.metric_labels[key].configure(
                text=str(stats[key])
            )

        rate = (
            stats["completed"] / stats["total"] * 100
            if stats["total"] else 0
        )

        category_summary = " | ".join(
            f"{row['category']}: {row['total']}"
            for row in categories
        )

        self.completion_label.configure(
            text=(
                f"Completion rate: {rate:.1f}%"
                f"    •    Tasks by category: "
                f"{category_summary or 'None'}"
            )
        )

    def after_task_change(self):
        self.refresh_categories()
        self.refresh_tasks()
        self.refresh_dashboard()


# --------------------------------------------------
# START APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    try:
        initialize_database()

        root = tk.Tk()
        app = TodoApp(root)
        root.mainloop()

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database error",
            f"Could not initialize the task database:\n{error}"
        )
    except tk.TclError as error:
        print(f"Could not start the graphical interface: {error}")
