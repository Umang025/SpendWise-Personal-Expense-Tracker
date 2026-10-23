"""Personal Expense Tracker GUI.

Features:
- Set a monthly budget.
- Add, view, and delete expenses.
- Save expenses in CSV format and the budget in a text file.
- View category, daily, monthly, and budget comparison charts.
"""

import math
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import date

import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


APP_DIR = Path(__file__).resolve().parent
EXPENSE_FILE = APP_DIR / "expenses.csv"
BUDGET_FILE = APP_DIR / "budget.txt"

COLUMNS = ["Date", "Category", "Description", "Amount"]
CATEGORIES = ["Food", "Travel", "Bills", "Shopping", "Other"]


class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Expense Tracker")
        self.root.geometry("800x500")
        self.root.minsize(700, 420)

        self.df = self.load_expenses()
        self.budget = self.load_budget()

        self.build_ui()
        self.refresh()

    # ---------- data ----------
    def load_expenses(self):
        if not EXPENSE_FILE.exists():
            return pd.DataFrame(columns=COLUMNS)

        try:
            data = pd.read_csv(EXPENSE_FILE)
            missing = [column for column in COLUMNS if column not in data.columns]
            if missing:
                raise ValueError("The CSV file is missing required columns.")

            data = data[COLUMNS].copy()
            data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
            data["Amount"] = pd.to_numeric(data["Amount"], errors="coerce")
            valid = (
                data["Date"].notna()
                & data["Amount"].notna()
                & np.isfinite(data["Amount"])
                & (data["Amount"] > 0)
                & data["Category"].isin(CATEGORIES)
            )
            invalid_count = int((~valid).sum())
            data = data.loc[valid].reset_index(drop=True)

            if invalid_count:
                messagebox.showwarning(
                    "Invalid saved records",
                    f"{invalid_count} invalid record(s) were ignored while loading expenses.",
                )
            return data
        except (OSError, pd.errors.ParserError, UnicodeDecodeError, ValueError) as exc:
            messagebox.showerror(
                "Could not load expenses",
                f"The saved expense file could not be read:\n{exc}\n\n"
                "The existing file has not been deleted. A new file will be created "
                "if you save expenses.",
            )
            return pd.DataFrame(columns=COLUMNS)

    def load_budget(self):
        if not BUDGET_FILE.exists():
            return 0.0

        try:
            value = float(BUDGET_FILE.read_text(encoding="utf-8").strip())
            if math.isfinite(value) and value >= 0:
                return value
        except (OSError, ValueError):
            pass

        messagebox.showwarning(
            "Invalid saved budget",
            "The saved budget is invalid. The budget has been set to 0.00.",
        )
        return 0.0

    def save_expenses(self):
        self.df.to_csv(EXPENSE_FILE, index=False, date_format="%Y-%m-%d")

    # ---------- UI ----------
    def build_ui(self):
        top = ttk.LabelFrame(self.root, text="Monthly Budget")
        top.pack(fill="x", padx=10, pady=5)

        self.budget_entry = ttk.Entry(top, width=15)
        self.budget_entry.pack(side="left", padx=5, pady=5)
        self.budget_entry.insert(0, f"{self.budget:.2f}")
        ttk.Button(top, text="Set Budget", command=self.set_budget).pack(
            side="left", padx=5
        )

        form = ttk.LabelFrame(self.root, text="Add Expense")
        form.pack(fill="x", padx=10, pady=5)

        for column, label in enumerate(["Date (YYYY-MM-DD)", "Category", "Description", "Amount"]):
            ttk.Label(form, text=label).grid(row=0, column=column, padx=5, pady=(5, 0))

        self.date_e = ttk.Entry(form, width=14)
        self.date_e.insert(0, str(date.today()))

        self.cat_e = ttk.Combobox(
            form, values=CATEGORIES, width=12, state="readonly"
        )
        self.cat_e.current(0)
        self.desc_e = ttk.Entry(form, width=22)
        self.amt_e = ttk.Entry(form, width=12)

        for column, widget in enumerate(
            [self.date_e, self.cat_e, self.desc_e, self.amt_e]
        ):
            widget.grid(row=1, column=column, padx=5, pady=5, sticky="ew")

        ttk.Button(form, text="Add Expense", command=self.add_expense).grid(
            row=1, column=4, padx=5, pady=5
        )

        self.tree = ttk.Treeview(self.root, columns=COLUMNS, show="headings", height=10)
        widths = {"Date": 110, "Category": 110, "Description": 260, "Amount": 110}
        for column in COLUMNS:
            self.tree.heading(column, text=column)
            self.tree.column(column, width=widths[column], anchor="w")
        self.tree.column("Amount", anchor="e")
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        bottom = ttk.Frame(self.root)
        bottom.pack(fill="x", padx=10, pady=5)

        self.summary = ttk.Label(bottom, text="", font=("Arial", 11, "bold"))
        self.summary.pack(side="left")

        ttk.Button(bottom, text="Show Charts", command=self.show_charts).pack(
            side="right"
        )
        ttk.Button(bottom, text="Reset All", command=self.reset_all).pack(
            side="right", padx=5
        )
        ttk.Button(bottom, text="Delete Selected", command=self.delete_selected).pack(
            side="right", padx=5
        )

    # ---------- actions ----------
    def set_budget(self):
        raw_value = self.budget_entry.get().strip()
        try:
            value = float(raw_value)
        except ValueError:
            messagebox.showerror("Invalid budget", "Enter a valid numeric budget.")
            return

        if not math.isfinite(value) or value < 0:
            messagebox.showerror(
                "Invalid budget", "The budget must be a finite number greater than or equal to 0."
            )
            return

        self.budget = value
        try:
            BUDGET_FILE.write_text(f"{self.budget:.2f}", encoding="utf-8")
        except OSError as exc:
            messagebox.showerror("Save error", f"Could not save the budget:\n{exc}")
            return

        self.refresh()

    def add_expense(self):
        date_text = self.date_e.get().strip()
        category = self.cat_e.get().strip()
        description = self.desc_e.get().strip()
        amount_text = self.amt_e.get().strip()

        try:
            expense_date = pd.to_datetime(date_text, format="%Y-%m-%d", errors="raise")
        except (ValueError, TypeError):
            messagebox.showerror(
                "Invalid date", "Enter a valid date in YYYY-MM-DD format."
            )
            return

        try:
            amount = float(amount_text)
        except ValueError:
            messagebox.showerror("Invalid amount", "Enter a valid numeric amount.")
            return

        if not math.isfinite(amount) or amount <= 0:
            messagebox.showerror("Invalid amount", "The expense amount must be greater than 0.")
            return

        if category not in CATEGORIES:
            messagebox.showerror("Invalid category", "Choose a category from the list.")
            return

        if not description:
            messagebox.showerror("Missing description", "Enter a short expense description.")
            return

        new_row = pd.DataFrame(
            [[expense_date, category, description, amount]], columns=COLUMNS
        )
        previous_data = self.df.copy()
        self.df = pd.concat([self.df, new_row], ignore_index=True)

        try:
            self.save_expenses()
        except OSError as exc:
            self.df = previous_data
            messagebox.showerror("Save error", f"Could not save the expense:\n{exc}")
            return

        self.desc_e.delete(0, tk.END)
        self.amt_e.delete(0, tk.END)
        self.refresh()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("No selection", "Select an expense in the table first.")
            return

        indexes = [int(item) for item in selected]
        previous_data = self.df.copy()
        self.df = self.df.drop(index=indexes).reset_index(drop=True)

        try:
            self.save_expenses()
        except OSError as exc:
            self.df = previous_data
            messagebox.showerror("Save error", f"Could not save the changes:\n{exc}")
            return

        self.refresh()

    def reset_all(self):
        if not messagebox.askyesno(
            "Reset All",
            "Delete all expenses and reset the monthly budget to 0.00? This cannot be undone.",
        ):
            return

        previous_data = self.df.copy()
        previous_budget = self.budget
        self.df = pd.DataFrame(columns=COLUMNS)
        self.budget = 0.0

        try:
            self.save_expenses()
            BUDGET_FILE.write_text("0.00", encoding="utf-8")
        except OSError as exc:
            self.df = previous_data
            self.budget = previous_budget
            messagebox.showerror("Reset error", f"Could not reset all data:\n{exc}")
            return

        self.budget_entry.delete(0, tk.END)
        self.budget_entry.insert(0, "0.00")
        self.refresh()

    def month_spent(self):
        if self.df.empty:
            return 0.0

        dates = pd.to_datetime(self.df["Date"], errors="coerce")
        today = pd.Timestamp.today()
        month = self.df.loc[
            (dates.dt.month == today.month) & (dates.dt.year == today.year), "Amount"
        ]
        return float(month.sum())

    def refresh(self):
        self.tree.delete(*self.tree.get_children())

        if not self.df.empty:
            ordered = self.df.sort_values("Date")
            for idx, row in ordered.iterrows():
                self.tree.insert(
                    "",
                    tk.END,
                    iid=str(idx),
                    values=(
                        pd.to_datetime(row["Date"]).strftime("%Y-%m-%d"),
                        row["Category"],
                        row["Description"],
                        f"{float(row['Amount']):.2f}",
                    ),
                )

        spent = self.month_spent()
        remaining = self.budget - spent
        self.summary.config(
            text=(
                f"Budget: {self.budget:.2f}   "
                f"Spent this month: {spent:.2f}   "
                f"Remaining: {remaining:.2f}"
            ),
            foreground="red" if remaining < 0 else "green",
        )

    def show_charts(self):
        if self.df.empty:
            messagebox.showinfo("No data", "Add at least one expense before viewing charts.")
            return

        data = self.df.copy()
        data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
        data["Amount"] = pd.to_numeric(data["Amount"], errors="coerce")
        data = data.dropna(subset=["Date", "Amount"])

        if data.empty:
            messagebox.showinfo("No data", "There are no valid expenses to plot.")
            return

        by_category = data.groupby("Category")["Amount"].sum()
        by_day = data.groupby(data["Date"].dt.date)["Amount"].sum()
        by_month = data.groupby(data["Date"].dt.to_period("M"))["Amount"].sum()

        spent = self.month_spent()
        remaining = self.budget - spent

        window = tk.Toplevel(self.root)
        window.title("Expense Charts")
        window.geometry("1000x800")

        figure = Figure(figsize=(10, 8))

        ax1 = figure.add_subplot(221)
        ax1.pie(by_category, labels=by_category.index, autopct="%1.1f%%")
        ax1.set_title("Expenses by Category")

        ax2 = figure.add_subplot(222)
        ax2.plot(by_day.index, by_day.values, marker="o")
        ax2.set_title("Daily Spending")
        ax2.set_ylabel("Amount")
        ax2.tick_params(axis="x", rotation=45)

        ax3 = figure.add_subplot(223)
        ax3.bar(by_month.index.astype(str), by_month.values)
        ax3.set_title("Monthly Spending")
        ax3.set_ylabel("Amount")
        ax3.tick_params(axis="x", rotation=45)

        ax4 = figure.add_subplot(224)
        ax4.bar(
            ["Budget", "Spent", "Remaining"],
            [self.budget, spent, max(remaining, 0)],
        )
        ax4.set_title("This Month: Budget vs Spent")
        ax4.set_ylabel("Amount")
        if remaining < 0:
            ax4.text(
                0.5,
                0.95,
                f"Over budget by {abs(remaining):.2f}",
                transform=ax4.transAxes,
                ha="center",
                va="top",
            )

        figure.tight_layout()
        canvas = FigureCanvasTkAgg(figure, master=window)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
