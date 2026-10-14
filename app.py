"""
EcoSort - Smart Waste Segregation and Monitoring System
=======================================================
A beginner-friendly Streamlit app for the EcoThon hackathon practice problem.

HOW THIS FILE IS ORGANISED (read it top to bottom):
    1. SETTINGS      - names, categories, statuses, colours. Edit these first
                       when you want to reuse the project for a new problem.
    2. DATA LAYER    - small functions that read / write the CSV file.
    3. STYLING       - a little CSS for the green-and-white look.
    4. PAGES         - one function per page (Home, Submit, Dashboard, Reports).
    5. MAIN          - sidebar navigation that decides which page to show.

Run it with:   python -m streamlit run app.py
"""

import os
import shutil
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# =============================================================================
# 1. SETTINGS  (change these to adapt the project to another problem statement)
# =============================================================================

APP_TITLE = "EcoSort"
APP_SUBTITLE = "Smart Waste Segregation and Monitoring System"
APP_ICON = "♻️"

# The kinds of problems people can report.
CATEGORIES = [
    "Overflowing Bin",
    "Poor Segregation",
    "Illegal Dumping",
    "Missed Collection",
    "Hazardous Waste",
    "Damaged Bin",
    "Littering",
]

# The life-cycle of a report. The first one is used for new reports.
STATUSES = ["Pending", "Reviewed", "Resolved"]

PRIORITIES = ["Low", "Medium", "High"]

# Colours used in the charts (green-and-white theme).
GREEN_DARK = "#14532D"
GREEN = "#2E8B57"
GREEN_LIGHT = "#E8F5EC"
STATUS_COLORS = {
    "Pending": "#E0A030",   # amber: needs attention
    "Reviewed": "#7FBF8E",  # light green: in progress
    "Resolved": "#14532D",  # dark green: done
}

# Where files live. Path(__file__) makes this work on Windows, Mac and Linux
# no matter which folder you start the app from.
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SAMPLE_FILE = DATA_DIR / "sample_reports.csv"   # fictional demo data (never edited)
REPORTS_FILE = DATA_DIR / "reports.csv"         # your working copy (edited by the app)

# Column names of the CSV file.
COLUMNS = [
    "report_id", "date", "location", "category", "description",
    "priority", "status", "reporter", "source",
]

# The "source" column tells demo rows apart from rows people really submitted.
SOURCE_DEMO = "Demo"
SOURCE_USER = "Submitted"


# =============================================================================
# 2. DATA LAYER  (reading and writing the CSV file)
# =============================================================================

def ensure_data_file():
    """On first run, copy the demo data to reports.csv so the app has data."""
    DATA_DIR.mkdir(exist_ok=True)
    if not REPORTS_FILE.exists():
        if SAMPLE_FILE.exists():
            shutil.copyfile(SAMPLE_FILE, REPORTS_FILE)
        else:
            pd.DataFrame(columns=COLUMNS).to_csv(REPORTS_FILE, index=False)


def load_reports():
    """Read reports.csv into a pandas table (DataFrame)."""
    ensure_data_file()
    try:
        df = pd.read_csv(REPORTS_FILE, dtype=str).fillna("")
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=COLUMNS)

    # Make sure every expected column exists, even in a hand-edited file.
    for col in COLUMNS:
        if col not in df.columns:
            df[col] = ""

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df[COLUMNS]


def save_reports(df):
    """
    Write the table back to reports.csv.
    Returns True on success, False if the file could not be written
    (for example because it is open in Excel on Windows).
    """
    out = df.copy()
    out["date"] = out["date"].dt.strftime("%Y-%m-%d").fillna("")

    temp_file = REPORTS_FILE.with_suffix(".tmp")
    try:
        out.to_csv(temp_file, index=False)
        os.replace(temp_file, REPORTS_FILE)  # swap in the new file in one step
        return True
    except OSError as error:
        st.error(
            "Could not save the reports file. If `data/reports.csv` is open in "
            f"Excel, close it and try again.\n\nDetails: {error}"
        )
        return False


def next_report_id(df):
    """Create the next ID, e.g. ECO-0038 if the biggest existing one is ECO-0037."""
    numbers = pd.to_numeric(df["report_id"].str.extract(r"(\d+)")[0], errors="coerce")
    numbers = numbers.dropna()
    next_number = int(numbers.max()) + 1 if len(numbers) > 0 else 1
    return f"ECO-{next_number:04d}"


def add_report(report_date, location, category, priority, description, reporter):
    """Add one new report. Returns the new ID, or None if saving failed."""
    df = load_reports()
    new_id = next_report_id(df)
    new_row = pd.DataFrame([{
        "report_id": new_id,
        "date": pd.Timestamp(report_date),
        "location": location.strip(),
        "category": category,
        "description": description.strip(),
        "priority": priority,
        "status": STATUSES[0],          # new reports always start as "Pending"
        "reporter": reporter.strip() or "Anonymous",
        "source": SOURCE_USER,
    }])
    df = new_row if df.empty else pd.concat([df, new_row], ignore_index=True)
    return new_id if save_reports(df) else None


def update_status(report_id, new_status):
    """Change the status of one report. Returns True if it was saved."""
    df = load_reports()
    df.loc[df["report_id"] == report_id, "status"] = new_status
    return save_reports(df)


def reset_to_demo_data():
    """Throw away all changes and copy the demo data back. Returns True if done."""
    try:
        shutil.copyfile(SAMPLE_FILE, REPORTS_FILE)
        return True
    except OSError as error:
        st.error(f"Could not reset the data: {error}")
        return False


def filter_by_source(df, include_demo):
    """Optionally hide the demo rows (so you can see only real submissions)."""
    if include_demo:
        return df
    return df[df["source"] != SOURCE_DEMO]


# =============================================================================
# 3. STYLING  (a little CSS on top of the theme in .streamlit/config.toml)
# =============================================================================

CUSTOM_CSS = f"""
<style>
    .block-container {{ padding-top: 2rem; max-width: 1200px; }}

    .hero {{
        background: linear-gradient(120deg, {GREEN_DARK} 0%, {GREEN} 100%);
        color: white;
        padding: 2rem 2.2rem;
        border-radius: 14px;
        margin-bottom: 1.2rem;
    }}
    .hero h1 {{ color: white; margin: 0 0 .3rem 0; font-size: 2.2rem; }}
    .hero p  {{ color: #E8F5EC; margin: 0; font-size: 1.05rem; }}

    .demo-badge {{
        display: inline-block;
        background: #FFF4D6;
        color: #7A5A00;
        border: 1px solid #E0A030;
        border-radius: 999px;
        padding: 2px 12px;
        font-size: .8rem;
        font-weight: 600;
    }}

    .card {{
        background: {GREEN_LIGHT};
        border-left: 5px solid {GREEN};
        border-radius: 8px;
        padding: 1rem 1.2rem;
        height: 100%;
    }}
    .card h4 {{ margin-top: 0; color: {GREEN_DARK}; }}

    /* Dashboard metric boxes */
    [data-testid="stMetric"] {{
        background: white;
        border: 1px solid #CFE6D6;
        border-top: 4px solid {GREEN};
        border-radius: 10px;
        padding: .8rem 1rem;
    }}

    h2, h3 {{ color: {GREEN_DARK}; }}
</style>
"""


def show_hero(title, subtitle):
    """The big green banner at the top of every page."""
    st.markdown(
        f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def show_demo_notice(df):
    """Clear labels telling the user how much of the data is fictional."""
    demo_count = int((df["source"] == SOURCE_DEMO).sum())
    user_count = int((df["source"] == SOURCE_USER).sum())
    if demo_count > 0:
        st.markdown(
            f'<span class="demo-badge">DEMO DATA</span> &nbsp; Showing '
            f"{demo_count} fictional demo reports and {user_count} submitted by you.",
            unsafe_allow_html=True,
        )


def style_chart(fig):
    """Give every Plotly chart the same clean, white look."""
    fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=10, r=10, t=50, b=10),
        title_font=dict(size=16, color=GREEN_DARK),
    )
    return fig


# =============================================================================
# 4. PAGES
# =============================================================================

def page_home():
    show_hero(f"{APP_ICON} {APP_TITLE}", APP_SUBTITLE)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            <div class="card">
            <h4>The problem</h4>
            Waste is often mixed together at the source, bins overflow before they
            are emptied, and nobody has a clear picture of where the biggest
            problems are. Complaints get lost in phone calls and messages, so the
            same issues keep coming back.
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="card">
            <h4>Our solution</h4>
            EcoSort gives everyone one simple place to report waste problems. The
            team can then see all reports on a live dashboard, find the worst
            locations and categories, and track every report from
            <b>Pending</b> to <b>Resolved</b>.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("How it works")
    step1, step2, step3 = st.columns(3)
    step1.markdown("**Step 1: Report**  \nAnyone submits a report from the *Submit Report* page.")
    step2.markdown("**Step 2: Monitor**  \nThe *Dashboard* shows totals, categories and trends.")
    step3.markdown("**Step 3: Resolve**  \nThe team updates the status on the *Reports* page.")

    st.subheader("Live snapshot")
    df = load_reports()
    total = len(df)
    pending = int((df["status"] == "Pending").sum())
    st.write(f"There are currently **{total}** reports in the system, **{pending}** of them still pending.")

    st.info(
        "**Demo data notice:** The reports that come with this project are "
        "fictional and only for practice. Reports you submit are labelled "
        "'Submitted' and are saved in `data/reports.csv`."
    )


def page_submit():
    show_hero("Submit a report", "Spotted a waste problem? Tell us where and what.")

    # clear_on_submit empties the form after a successful submission.
    with st.form("report_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            reporter = st.text_input("Your name (optional)")
            location = st.text_input("Location *", placeholder="e.g. Hostel Block A, ground floor")
            report_date = st.date_input("Date *", value=date.today(), max_value=date.today())
        with col2:
            category = st.selectbox("Issue category *", CATEGORIES)
            priority = st.select_slider("Priority", options=PRIORITIES, value="Medium")

        description = st.text_area(
            "Describe the problem *",
            placeholder="What did you see? How bad is it?",
            height=130,
        )
        submitted = st.form_submit_button("Submit report", type="primary")

    if submitted:
        # Simple checks so we do not save empty reports.
        if len(location.strip()) < 3:
            st.error("Please enter a location (at least 3 characters).")
        elif len(description.strip()) < 10:
            st.error("Please describe the problem (at least 10 characters).")
        else:
            new_id = add_report(report_date, location, category, priority, description, reporter)
            if new_id:
                st.success(f"Report submitted. Your report ID is **{new_id}**. Its status is Pending.")
                st.balloons()


def page_dashboard(include_demo):
    show_hero("Dashboard", "A live overview of all waste reports.")

    df_all = load_reports()
    df = filter_by_source(df_all, include_demo)
    show_demo_notice(df)

    if df.empty:
        st.info("No reports to show yet. Submit one from the *Submit Report* page.")
        return

    # --- Metric boxes ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total reports", len(df))
    m2.metric("Pending", int((df["status"] == "Pending").sum()))
    m3.metric("Reviewed", int((df["status"] == "Reviewed").sum()))
    m4.metric("Resolved", int((df["status"] == "Resolved").sum()))

    st.write("")  # small vertical gap

    # --- Row 1: categories and statuses ---
    left, right = st.columns(2)

    with left:
        by_category = df["category"].value_counts().reset_index()
        by_category.columns = ["Category", "Reports"]
        by_category = by_category.sort_values("Reports")  # biggest bar on top
        fig = px.bar(
            by_category, x="Reports", y="Category", orientation="h",
            title="Reports by issue category",
            color_discrete_sequence=[GREEN],
        )
        st.plotly_chart(style_chart(fig))

    with right:
        by_status = df["status"].value_counts().reset_index()
        by_status.columns = ["Status", "Reports"]
        fig = px.pie(
            by_status, names="Status", values="Reports", hole=0.5,
            title="Reports by status",
            color="Status", color_discrete_map=STATUS_COLORS,
        )
        st.plotly_chart(style_chart(fig))

    # --- Row 2: trend and locations ---
    left, right = st.columns(2)

    with left:
        view = st.radio("Trend view", ["Daily", "Weekly"], horizontal=True)
        dated = df.dropna(subset=["date"]).set_index("date")
        rule = "D" if view == "Daily" else "W"
        trend = dated.resample(rule).size().reset_index(name="Reports")
        trend.columns = ["Date", "Reports"]
        fig = px.line(
            trend, x="Date", y="Reports", markers=True,
            title=f"{view} report trend",
            color_discrete_sequence=[GREEN],
        )
        st.plotly_chart(style_chart(fig))

    with right:
        st.write("")  # keeps the chart level with the trend chart
        st.write("")
        by_location = df["location"].value_counts().head(8).reset_index()
        by_location.columns = ["Location", "Reports"]
        by_location = by_location.sort_values("Reports")
        fig = px.bar(
            by_location, x="Reports", y="Location", orientation="h",
            title="Top locations",
            color_discrete_sequence=[GREEN_DARK],
        )
        st.plotly_chart(style_chart(fig))


def page_reports(include_demo):
    show_hero("Reports", "Search, filter, download and update reports.")

    df_all = load_reports()
    df = filter_by_source(df_all, include_demo)
    show_demo_notice(df)

    if df.empty:
        st.info("No reports to show yet.")
        return

    # --- Filters ---
    st.subheader("Find reports")
    search = st.text_input("Search", placeholder="Search by ID, location, description, category or reporter")
    f1, f2, f3 = st.columns(3)
    status_filter = f1.multiselect("Status", STATUSES, default=STATUSES)
    category_filter = f2.multiselect("Category", CATEGORIES, default=CATEGORIES)
    priority_filter = f3.multiselect("Priority", PRIORITIES, default=PRIORITIES)

    filtered = df[
        df["status"].isin(status_filter)
        & df["category"].isin(category_filter)
        & df["priority"].isin(priority_filter)
    ]

    if search.strip():
        match = pd.Series(False, index=filtered.index)
        for column in ["report_id", "location", "description", "category", "reporter"]:
            match = match | filtered[column].str.contains(search.strip(), case=False, regex=False, na=False)
        filtered = filtered[match]

    filtered = filtered.sort_values("date", ascending=False)

    # --- Table + download ---
    st.write(f"Showing **{len(filtered)}** of {len(df)} reports")
    st.dataframe(
        filtered,
        hide_index=True,
        column_config={
            "report_id": "ID",
            "date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
            "location": "Location",
            "category": "Category",
            "description": "Description",
            "priority": "Priority",
            "status": "Status",
            "reporter": "Reporter",
            "source": "Source",
        },
    )

    # utf-8-sig makes Excel on Windows open the file correctly.
    csv_bytes = filtered.assign(date=filtered["date"].dt.strftime("%Y-%m-%d")).to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Download filtered reports (CSV)",
        data=csv_bytes,
        file_name="ecosort_reports.csv",
        mime="text/csv",
    )

    # --- Update status ---
    st.subheader("Update a report's status")
    if filtered.empty:
        st.caption("No reports match the filters above.")
        return

    options = filtered["report_id"].tolist()
    labels = {
        row.report_id: f"{row.report_id} | {row.category} | {row.location} | now: {row.status}"
        for row in filtered.itertuples()
    }
    u1, u2, u3 = st.columns([3, 1.2, 1])
    chosen_id = u1.selectbox("Report", options, format_func=lambda rid: labels[rid])
    current_status = filtered.loc[filtered["report_id"] == chosen_id, "status"].iloc[0]
    new_status = u2.selectbox(
        "New status", STATUSES,
        index=STATUSES.index(current_status) if current_status in STATUSES else 0,
    )
    u3.write("")
    u3.write("")
    if u3.button("Update status", type="primary"):
        if update_status(chosen_id, new_status):
            st.success(f"{chosen_id} is now {new_status}.")
            st.rerun()  # reload so the table shows the change


# =============================================================================
# 5. MAIN  (sidebar navigation)
# =============================================================================

def main():
    # set_page_config must be the first Streamlit command.
    st.set_page_config(page_title=f"{APP_TITLE} | {APP_SUBTITLE}", page_icon=APP_ICON, layout="wide")
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    st.sidebar.title(f"{APP_ICON} {APP_TITLE}")
    st.sidebar.caption(APP_SUBTITLE)

    page = st.sidebar.radio(
        "Go to",
        ["Home", "Submit Report", "Dashboard", "Reports"],
    )

    st.sidebar.divider()
    include_demo = st.sidebar.checkbox("Include demo data", value=True)

    with st.sidebar.expander("Reset data"):
        st.caption("Deletes your submitted reports and status changes, and restores the demo data.")
        confirm = st.checkbox("Yes, I want to reset")
        if st.button("Reset to demo data", disabled=not confirm):
            if reset_to_demo_data():
                st.success("Data reset.")
                st.rerun()

    st.sidebar.divider()
    st.sidebar.caption("EcoThon practice project. Demo reports are fictional.")

    if page == "Home":
        page_home()
    elif page == "Submit Report":
        page_submit()
    elif page == "Dashboard":
        page_dashboard(include_demo)
    else:
        page_reports(include_demo)


# Streamlit runs this file as "__main__", so main() is called on every rerun.
if __name__ == "__main__":
    main()
