# EcoSort - Smart Waste Segregation and Monitoring System

A beginner-friendly **Streamlit + Pandas + Plotly** project for the EcoThon hackathon practice problem.
People report waste problems, and a dashboard shows what is happening and what is still unresolved.

> **All reports that come with this project are fictional demo data.** They are labelled `Demo` in the app.

## Features

- Green-and-white website with sidebar navigation
- Home page explaining the problem and the solution
- Form to submit a waste report
- Dashboard: total, pending, reviewed and resolved metrics
- Interactive charts: issue categories, statuses, report trend (daily/weekly), top locations
- Searchable report table with status, category and priority filters
- CSV download of the filtered table
- Update a report's status (Pending -> Reviewed -> Resolved)
- Reports are saved to `data/reports.csv`, so they are still there after restarting the app

## Project structure

```
ecosort/
├── app.py                  <- the whole app (settings at the top)
├── requirements.txt        <- Python libraries to install
├── README.md               <- this file
├── .streamlit/
│   └── config.toml         <- green-and-white theme colours
└── data/
    ├── sample_reports.csv  <- 37 fictional demo reports (never changed by the app)
    └── reports.csv         <- created on first run; your working copy
```

## Setup on Windows (VS Code)

You need **Python 3.9 or newer** (check with `python --version`). Get it from https://www.python.org/downloads/ and tick **"Add Python to PATH"** during install.

1. Unzip the project and open the `ecosort` folder in VS Code (**File -> Open Folder**).
2. Open the VS Code terminal: **Terminal -> New Terminal** (it should be PowerShell).
3. Create a virtual environment:
   ```powershell
   python -m venv .venv
   ```
4. Activate it:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
   If PowerShell says scripts are disabled, run this once and try again:
   ```powershell
   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
   ```
   (Or use Command Prompt and run `.venv\Scripts\activate.bat` instead.)
5. Install the libraries:
   ```powershell
   pip install -r requirements.txt
   ```
6. Run the app:
   ```powershell
   python -m streamlit run app.py
   ```
7. Your browser opens at http://localhost:8501. To stop the app, press `Ctrl + C` in the terminal.

Tip: in VS Code press `Ctrl + Shift + P`, choose **Python: Select Interpreter** and pick the one inside `.venv`.

On Mac/Linux, activate with `source .venv/bin/activate` instead; everything else is the same.

## How to use the app

| Page | What you can do |
|---|---|
| Home | Read about the problem and solution |
| Submit Report | Fill in the form. New reports start as **Pending** |
| Dashboard | See the metrics and charts |
| Reports | Search, filter, download CSV, and change a report's status |

Sidebar extras: **Include demo data** hides the fictional rows so you can see only your own reports.
**Reset data** restores the original demo data (it deletes your submissions).

## How data is stored

- On first run, `data/sample_reports.csv` is copied to `data/reports.csv`.
- The app only ever changes `reports.csv`. The sample file stays as a clean backup.
- You can also reset by deleting `data/reports.csv` and restarting the app.
- Close `reports.csv` in Excel before saving from the app, or Windows may block the write.

## Adapting this project to a different problem statement

Most changes happen in the **SETTINGS** section at the top of `app.py`:

1. `APP_TITLE`, `APP_SUBTITLE`, `APP_ICON` - the name shown everywhere.
2. `CATEGORIES`, `STATUSES`, `PRIORITIES` - the dropdown options. Example for a campus-safety app:
   `CATEGORIES = ["Broken Light", "Unsafe Area", "Harassment", "Theft"]`.
3. `GREEN`, `GREEN_DARK`, `STATUS_COLORS` and `.streamlit/config.toml` - the colours.
4. Replace the text in `page_home()` with your own problem and solution.
5. Replace `data/sample_reports.csv` with your own fictional data. Keep the same columns
   (or update `COLUMNS` in `app.py`), and make sure every `category` and `status` value matches your lists.
6. Delete `data/reports.csv` so the app copies your new sample file.

To add a new form field: add a widget in `page_submit()`, add the column name to `COLUMNS`,
and pass it to `add_report()`.

## Troubleshooting

| Problem | Fix |
|---|---|
| `'streamlit' is not recognized` | Use `python -m streamlit run app.py` and make sure the virtual environment is activated |
| `No module named streamlit` | Run `pip install -r requirements.txt` with the virtual environment activated |
| Table or charts look off after upgrading | Run `pip install --upgrade streamlit plotly` |
| "Could not save the reports file" | Close `data/reports.csv` if it is open in Excel |
| Port 8501 already in use | `python -m streamlit run app.py --server.port 8502` |

## Tech stack

Python, Streamlit (web app), Pandas (data), Plotly (charts), CSV file (storage).
