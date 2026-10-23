# SpendWise – Personal Expense Tracker

SpendWise is a Python desktop application for recording personal expenses, managing a monthly budget, and viewing spending patterns through charts.

## Features

- Set and save a monthly budget.
- Add expenses with a date, category, description, and amount.
- View recorded expenses in a table.
- See the current month's spending and remaining budget.
- Delete selected expense records.
- Reset all expenses and the saved budget after confirmation.
- View four charts:
  - **Expenses by Category** — pie chart
  - **Daily Spending** — line chart
  - **Monthly Spending** — bar chart
  - **Budget vs Spent** — comparison chart for the current month
- Save expense records and the budget locally so they can be loaded when the app starts.

## Technologies Used

- **Python** — application logic
- **Tkinter** — graphical user interface
- **pandas** — expense data handling
- **NumPy** — numeric calculations and data handling
- **Matplotlib** — charts

## Requirements

- Python 3.9 or later recommended
- `numpy`
- `pandas`
- `matplotlib`
- Tkinter, usually included with standard Python on Windows

## Installation

1. Install Python from [python.org](https://www.python.org/downloads/).
2. Open a terminal in the project folder.
3. Install the required packages:

   ```bash
   python -m pip install numpy pandas matplotlib
   ```

## Run the Application

Save the main program as `expense_tracker_gui.py` and run:

```bash
python expense_tracker_gui.py
```

The SpendWise window will open.

## How to Use

1. Enter your monthly budget and click **Set Budget**.
2. Enter the expense date in `YYYY-MM-DD` format.
3. Select a category: Food, Travel, Bills, Shopping, or Other.
4. Enter a description and a positive amount.
5. Click **Add Expense**.
6. Review the table and the monthly budget summary.
7. Select a row and click **Delete Selected** to remove an expense.
8. Click **Show Charts** to view spending charts.
9. Click **Reset All** to delete all expenses and reset the budget to `0.00`. This action requires confirmation and cannot be undone.

## Data Storage

SpendWise stores data in two local files in the same folder as the Python script:

- `expenses.csv` — expense dates, categories, descriptions, and amounts.
- `budget.txt` — saved monthly budget.

Keep these files if you want to retain your records. Avoid uploading real personal expense data to a public GitHub repository.

## Project Structure

```text
SpendWise-Personal-Expense-Tracker/
├── expense_tracker_gui.py
├── README.md
├── expenses.csv       # created when expense records are saved
└── budget.txt         # created when a budget is saved
```

The CSV and budget files are created as the app saves data; they may not exist in a fresh clone.

## Validation and Limitations

- Budget values must be finite numbers greater than or equal to zero.
- Expense amounts must be finite numbers greater than zero.
- Expense dates must use the `YYYY-MM-DD` format.
- The budget summary calculates spending for the current calendar month.
- Daily and monthly charts can include all saved expense records.
- Resetting the app deletes saved expenses and resets the budget.

## Possible Future Improvements

- Filter expenses by date range or category.
- Export monthly reports.
- Add search and edit features for existing expenses.
- Improve the interface with a modern theme.

## License

No license is included yet. Add a `LICENSE` file if you want to define how others may use, modify, and distribute this project.
