"""
EcoSort - Smart Waste Segregation and Monitoring System
=======================================================
A beginner-friendly Streamlit app for the EcoThon hackathon practice problem.
"""

import os
import shutil
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# =============================================================================
# 1. SETTINGS
# =============================================================================

APP_TITLE = "EcoSort"
APP_SUBTITLE = "Smart Waste Segregation and Monitoring System"
APP_ICON = "♻️"

CATEGORIES = [
    "Overflowing Bin",
    "Poor Segregation",
    "Illegal Dumping",
    "Missed Collection",
    "Hazardous Waste",
    "Damaged Bin",
    "Littering",
]

STATUSES = ["Pending", "Reviewed", "Resolved"]
PRIORITIES = ["Low", "Medium", "High"]

# Common campus/city landmarks with fixed GPS coordinates for accurate mapping
LOCATIONS = {
    "Hostel Block A": {"lat": 11.0168, "lon": 76.9558},
    "Main Canteen & Dining Hall": {"lat": 11.0185, "lon": 76.9580},
    "Academic Block 3": {"lat": 11.0150, "lon": 76.9530},
    "Central Library Gate": {"lat": 11.0192, "lon": 76.9515},
    "Sports Complex & Ground": {"lat": 11.0135, "lon": 76.9590},
    "Main Entrance / Gate 1": {"lat": 11.0210, "lon": 76.9540},
}

GREEN_DARK = "#14532D"
GREEN = "#2E8B57"
GREEN_LIGHT = "#E8F5EC"
STATUS_COLORS = {
    "Pending": "#E0A030",
    "Reviewed": "#7FBF8E",
    "Resolved": "#14532D",
}

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SAMPLE_FILE = DATA_DIR / "sample_reports.csv"
REPORTS_FILE = DATA_DIR / "reports.csv"

COLUMNS = [
    "report_id",
    "date",
    "location",
    "category",
    "description",
    "priority",
    "status",
    "reporter",
    "source",
    "lat",
    "lon",
    "image_name",
]

SOURCE_DEMO = "Demo"
SOURCE_USER = "Submitted"


# =============================================================================
# 2. DATA LAYER
# =============================================================================


def ensure_data_file():
  DATA_DIR.mkdir(exist_ok=True)
  if not REPORTS_FILE.exists():
    if SAMPLE_FILE.exists():
      shutil.copyfile(SAMPLE_FILE, REPORTS_FILE)
    else:
      pd.DataFrame(columns=COLUMNS).to_csv(REPORTS_FILE, index=False)


def load_reports():
  ensure_data_file()
  try:
    df = pd.read_csv(REPORTS_FILE, dtype=str).fillna("")
  except pd.errors.EmptyDataError:
    df = pd.DataFrame(columns=COLUMNS)

  for col in COLUMNS:
    if col not in df.columns:
      df[col] = ""

  df["date"] = pd.to_datetime(df["date"], errors="coerce")
  return df[COLUMNS]


def save_reports(df):
  out = df.copy()
  out["date"] = out["date"].dt.strftime("%Y-%m-%d").fillna("")
  temp_file = REPORTS_FILE.with_suffix(".tmp")
  try:
    out.to_csv(temp_file, index=False)
    os.replace(temp_file, REPORTS_FILE)
    return True
  except OSError as error:
    st.error(f"Could not save the reports file: {error}")
    return False


def next_report_id(df):
  numbers = pd.to_numeric(
      df["report_id"].str.extract(r"(\d+)")[0], errors="coerce"
  )
  numbers = numbers.dropna()
  next_number = int(numbers.max()) + 1 if len(numbers) > 0 else 1
  return f"ECO-{next_number:04d}"


def calculate_smart_priority(description, user_selected_priority):
  critical_keywords = [
      "overflowing",
      "hazardous",
      "drain",
      "medical",
      "toxic",
      "burst",
      "danger",
  ]
  desc_lower = description.lower()
  if any(keyword in desc_lower for keyword in critical_keywords):
    return "High"
  return user_selected_priority


def add_report(
    report_date, location, category, priority, description, reporter, image_name
):
  df = load_reports()
  new_id = next_report_id(df)
  final_priority = calculate_smart_priority(description, priority)

  coords = LOCATIONS.get(location, {"lat": 11.0168, "lon": 76.9558})

  new_row = pd.DataFrame([{
      "report_id": new_id,
      "date": pd.Timestamp(report_date),
      "location": location,
      "category": category,
      "description": description.strip(),
      "priority": final_priority,
      "status": STATUSES[0],
      "reporter": reporter.strip() or "Anonymous",
      "source": SOURCE_USER,
      "lat": coords["lat"],
      "lon": coords["lon"],
      "image_name": image_name,
  }])
  df = new_row if df.empty else pd.concat([df, new_row], ignore_index=True)
  return new_id if save_reports(df) else None


def update_status(report_id, new_status):
  df = load_reports()
  df.loc[df["report_id"] == report_id, "status"] = new_status
  return save_reports(df)


def reset_to_demo_data():
  try:
    shutil.copyfile(SAMPLE_FILE, REPORTS_FILE)
    return True
  except OSError as error:
    st.error(f"Could not reset the data: {error}")
    return False


def filter_by_source(df, include_demo):
  if include_demo:
    return df
  return df[df["source"] != SOURCE_DEMO]


# =============================================================================
# 3. STYLING
# =============================================================================

CUSTOM_CSS = f"""
<style>
    .block-container {{ padding-top: 2rem; max-width: 1200px; }}
    .hero {{
        background: linear-gradient(120deg, {GREEN_DARK} 0%, {GREEN} 100%);
        color: white; padding: 2rem 2.2rem; border-radius: 14px; margin-bottom: 1.2rem;
    }}
    .hero h1 {{ color: white; margin: 0 0 .3rem 0; font-size: 2.2rem; }}
    .hero p  {{ color: #E8F5EC; margin: 0; font-size: 1.05rem; }}
    .demo-badge {{
        display: inline-block; background: #FFF4D6; color: #7A5A00;
        border: 1px solid #E0A030; border-radius: 999px; padding: 2px 12px;
        font-size: .8rem; font-weight: 600;
    }}
    .card {{
        background: {GREEN_LIGHT}; border-left: 5px solid {GREEN};
        border-radius: 8px; padding: 1rem 1.2rem; height: 100%; color: #1E293B !important;
    }}
    .card h4 {{ margin-top: 0; color: {GREEN_DARK} !important; }}
    .card p {{ color: #1E293B !important; }}
    [data-testid="stMetric"] {{
        background: white; border: 1px solid #CFE6D6; border-top: 4px solid {GREEN};
        border-radius: 10px; padding: .8rem 1rem;
    }}
    h2, h3 {{ color: {GREEN_DARK}; }}
</style>
"""


def show_hero(title, subtitle):
  st.markdown(
      f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>',
      unsafe_allow_html=True,
  )


def show_demo_notice(df):
  demo_count = int((df["source"] == SOURCE_DEMO).sum())
  user_count = int((df["source"] == SOURCE_USER).sum())
  if demo_count > 0:
    st.markdown(
        f'<span class="demo-badge">DEMO DATA</span> &nbsp; Showing'
        f" {demo_count} fictional demo reports and {user_count} submitted by"
        " you.",
        unsafe_allow_html=True,
    )


def style_chart(fig):
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
            <p>Waste is often mixed together at the source, bins overflow before they
            are emptied, and nobody has a clear picture of where problems lie.</p>
            </div>
            """,
        unsafe_allow_html=True,
    )
  with col2:
    st.markdown(
        """
            <div class="card">
            <h4>Our solution</h4>
            <p>EcoSort brings smart tracking, automated triage, and live municipal dashboards
            together to resolve waste issues instantly.</p>
            </div>
            """,
        unsafe_allow_html=True,
    )

  st.subheader("Live snapshot")
  df = load_reports()
  total = len(df)
  pending = int((df["status"] == "Pending").sum())
  st.write(
      f"There are currently **{total}** reports in the system, **{pending}** of"
      " them still pending."
  )


def page_submit():
  show_hero("Submit a report", "Spotted a waste problem? Tell us where and what.")

  with st.form("report_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
      reporter = st.text_input("Your name (optional)")
      location = st.selectbox(
          "Location Landmark *", options=list(LOCATIONS.keys())
      )
      report_date = st.date_input(
          "Date *", value=date.today(), max_value=date.today()
      )
    with col2:
      category = st.selectbox("Issue category *", CATEGORIES)
      priority = st.select_slider(
          "Priority", options=PRIORITIES, value="Medium"
      )

    description = st.text_area(
        "Describe the problem *",
        placeholder=(
            "What did you see? Mention keywords like 'overflowing' or"
            " 'hazardous' for auto-triage."
        ),
        height=130,
    )

    uploaded_file = st.file_uploader(
        "Attach photo verification (optional)", type=["jpg", "png", "jpeg"]
    )
    image_name = uploaded_file.name if uploaded_file else ""

    if uploaded_file:
      st.image(
          uploaded_file, caption="Preview of attached issue", width=200
      )

    submitted = st.form_submit_button("Submit report", type="primary")

  if submitted:
    if len(description.strip()) < 10:
      st.error("Please describe the problem (at least 10 characters).")
    else:
      new_id = add_report(
          report_date,
          location,
          category,
          priority,
          description,
          reporter,
          image_name,
      )
      if new_id:
        st.toast(
            "Report successfully logged and routed to municipal team!",
            icon="🚨",
        )
        st.success(
            f"Report submitted successfully! Ticket ID: **{new_id}**. Priority"
            " auto-evaluated."
        )
        st.balloons()


def page_dashboard(include_demo):
  show_hero("Dashboard", "A live overview of all waste reports.")
  df_all = load_reports()
  df = filter_by_source(df_all, include_demo)
  show_demo_notice(df)

  if df.empty:
    st.info("No reports to show yet.")
    return

  m1, m2, m3, m4 = st.columns(4)
  m1.metric("Total reports", len(df))
  m2.metric("Pending", int((df["status"] == "Pending").sum()))
  m3.metric("Reviewed", int((df["status"] == "Reviewed").sum()))
  m4.metric("Resolved", int((df["status"] == "Resolved").sum()))

  st.write("")
  left, right = st.columns(2)
  with left:
    by_category = df["category"].value_counts().reset_index()
    by_category.columns = ["Category", "Reports"]
    fig = px.bar(
        by_category,
        x="Reports",
        y="Category",
        orientation="h",
        title="Reports by category",
        color_discrete_sequence=[GREEN],
    )
    st.plotly_chart(style_chart(fig))

  with right:
    by_status = df["status"].value_counts().reset_index()
    by_status.columns = ["Status", "Reports"]
    fig = px.pie(
        by_status,
        names="Status",
        values="Reports",
        hole=0.5,
        title="Reports by status",
        color="Status",
        color_discrete_map=STATUS_COLORS,
    )
    st.plotly_chart(style_chart(fig))

  st.subheader("📍 Live Waste Incident Map")
  if "lat" in df.columns and "lon" in df.columns:
    map_df = df.copy()
    map_df["lat"] = pd.to_numeric(map_df["lat"], errors="coerce")
    map_df["lon"] = pd.to_numeric(map_df["lon"], errors="coerce")
    map_data = map_df.dropna(subset=["lat", "lon"])
    if not map_data.empty:
      st.map(map_data, latitude="lat", longitude="lon", size=30, color="#22c55e")


def page_reports(include_demo):
  show_hero("Reports Management", "Search, filter, download and triage reports.")
  df_all = load_reports()
  df = filter_by_source(df_all, include_demo)
  show_demo_notice(df)

  if df.empty:
    st.info("No reports to show yet.")
    return

  search = st.text_input("Search records")
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
    for col in ["report_id", "location", "description", "category"]:
      match = match | filtered[col].str.contains(
          search.strip(), case=False, na=False
      )
    filtered = filtered[match]

  st.dataframe(
      filtered,
      hide_index=True,
      column_config={
          "lat": None,
          "lon": None,
          "image_name": "Attached Photo",
      },
  )

  csv_bytes = (
      filtered.assign(date=filtered["date"].dt.strftime("%Y-%m-%d"))
      .to_csv(index=False)
      .encode("utf-8-sig")
  )
  st.download_button(
      "📥 Download filtered reports (CSV)",
      data=csv_bytes,
      file_name="ecosort_reports.csv",
      mime="text/csv",
  )

  st.subheader("Update a report's status")
  if not filtered.empty:
    options = filtered["report_id"].tolist()
    labels = {
        r.report_id: f"{r.report_id} | {r.category} | status: {r.status}"
        for r in filtered.itertuples()
    }
    u1, u2, u3 = st.columns([3, 1.2, 1])
    chosen_id = u1.selectbox(
        "Report ID", options, format_func=lambda rid: labels[rid]
    )
    current_status = filtered.loc[
        filtered["report_id"] == chosen_id, "status"
    ].iloc[0]
    new_status = u2.selectbox(
        "New status",
        STATUSES,
        index=(
            STATUSES.index(current_status) if current_status in STATUSES else 0
        ),
    )
    if u3.button("Update status", type="primary"):
      if update_status(chosen_id, new_status):
        st.toast(
            f"Successfully updated status for ticket {chosen_id}!", icon="✅"
        )
        st.success(f"Updated {chosen_id} to {new_status}!")
        st.rerun()


# =============================================================================
# 5. MAIN
# =============================================================================


def main():
  st.set_page_config(
      page_title=f"{APP_TITLE} | {APP_SUBTITLE}",
      page_icon=APP_ICON,
      layout="wide",
  )
  st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

  st.sidebar.title(f"{APP_ICON} {APP_TITLE}")
  st.sidebar.caption(APP_SUBTITLE)

  role = st.sidebar.selectbox("Select Role", ["Citizen", "Administrator"])

  if role == "Citizen":
    page = st.sidebar.radio("Go to", ["Home", "Submit Report"])
  else:
    page = st.sidebar.radio(
        "Go to", ["Home", "Submit Report", "Dashboard", "Reports"]
    )

  st.sidebar.divider()
  include_demo = st.sidebar.checkbox("Include demo data", value=True)

  with st.sidebar.expander("Reset data"):
    confirm = st.checkbox("Yes, I want to reset")
    if st.button("Reset to demo data", disabled=not confirm):
      if reset_to_demo_data():
        st.success("Data reset.")
        st.rerun()

  if page == "Home":
    page_home()
  elif page == "Submit Report":
    page_submit()
  elif page == "Dashboard":
    page_dashboard(include_demo)
  else:
    page_reports(include_demo)


if __name__ == "__main__":
  main()
