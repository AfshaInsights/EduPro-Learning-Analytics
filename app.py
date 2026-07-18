import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# PAGE CONFIGURATION

st.set_page_config(
    page_title="EduPro Learning Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# LOAD DATASET

df = pd.read_csv("EduPro_Merged_Dataset.csv")

df["TransactionDate"] = pd.to_datetime(df["TransactionDate"])

# CREATE AGE GROUPS

age_bins = [0, 17, 25, 35, 45, 100]

age_labels = [
    "<18",
    "18-25",
    "26-35",
    "36-45",
    "45+"
]

df["AgeGroup"] = pd.cut(
    df["Age"],
    bins=age_bins,
    labels=age_labels
)

# SIDEBAR

st.sidebar.title("📊 Dashboard Filters")

gender = st.sidebar.multiselect(
    "Select Gender",
    options=sorted(df["Gender"].unique()),
    default=sorted(df["Gender"].unique())
)

age_group = st.sidebar.multiselect(
    "Select Age Group",
    options=sorted(df["AgeGroup"].dropna().astype(str).unique()),
    default=sorted(df["AgeGroup"].dropna().astype(str).unique())
)

course_category = st.sidebar.multiselect(
    "Select Course Category",
    options=sorted(df["CourseCategory"].unique()),
    default=sorted(df["CourseCategory"].unique())
)

course_level = st.sidebar.multiselect(
    "Select Course Level",
    options=sorted(df["CourseLevel"].unique()),
    default=sorted(df["CourseLevel"].unique())
)

# APPLY FILTERS

filtered_df = df[
    (df["Gender"].isin(gender)) &
    (df["AgeGroup"].astype(str).isin(age_group)) &
    (df["CourseCategory"].isin(course_category)) &
    (df["CourseLevel"].isin(course_level))
]

# HANDLE EMPTY FILTER RESULTS

if filtered_df.empty:

    st.warning("⚠️ No data available for the selected filters.")

    st.info("Please change one or more filters from the sidebar to view the dashboard.")

    st.stop()
# KPI CALCULATIONS

total_learners = filtered_df["UserID"].nunique()

total_courses = filtered_df["CourseID"].nunique()

total_enrollments = filtered_df.shape[0]

average_courses = (
    total_enrollments / total_learners
    if total_learners > 0 else 0
)

# DASHBOARD TITLE

st.title("📊 EduPro Learning Analytics Dashboard")

st.write("""
This dashboard presents learner demographics, enrollment statistics,
course popularity and business insights using the EduPro dataset.
""")

st.markdown("---")

# KPI CARDS

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "👨 Total Learners",
        f"{total_learners:,}"
    )

with col2:
    st.metric(
        "📚 Total Courses",
        f"{total_courses:,}"
    )

with col3:
    st.metric(
        "📝 Total Enrollments",
        f"{total_enrollments:,}"
    )

with col4:
    st.metric(
        "⭐ Avg Courses / Learner",
        f"{average_courses:.2f}"
    )

st.markdown("---")
# CHARTS

st.header("📈 Interactive Visual Analytics")

# Create two columns
chart1, chart2 = st.columns(2)

# Gender Distribution

with chart1:

    st.subheader("Gender Distribution")

    gender_count = (
        filtered_df["Gender"]
        .value_counts()
    )

    fig, ax = plt.subplots(figsize=(5,5))

    ax.pie(
        gender_count,
        labels=gender_count.index,
        autopct="%1.1f%%",
        startangle=90
    )

    ax.set_ylabel("")

    st.pyplot(fig)

# Age Group Distribution

with chart2:

    st.subheader("Age Group Distribution")

    age_count = (
        filtered_df["AgeGroup"]
        .value_counts()
        .sort_index()
    )

    fig, ax = plt.subplots(figsize=(6,5))

    ax.bar(
        age_count.index.astype(str),
        age_count.values
    )

    ax.set_xlabel("Age Group")

    ax.set_ylabel("Learners")

    st.pyplot(fig)

st.markdown("---")

# SECOND ROW OF CHARTS

chart3, chart4 = st.columns(2)

# Course Category Distribution

with chart3:

    st.subheader("Course Category Distribution")

    category_count = (
        filtered_df["CourseCategory"]
        .value_counts()
    )

    fig, ax = plt.subplots(figsize=(7,5))

    ax.barh(
        category_count.index,
        category_count.values
    )

    ax.set_xlabel("Enrollments")

    st.pyplot(fig)

# Monthly Enrollment Trend

with chart4:

    st.subheader("Monthly Enrollment Trend")

    temp_df = filtered_df.copy()

    temp_df["Month"] = (
        temp_df["TransactionDate"]
        .dt.to_period("M")
        .astype(str)
    )

    monthly = (
        temp_df
        .groupby("Month")
        .size()
        .reset_index(name="Enrollments")
    )

    fig, ax = plt.subplots(figsize=(7,5))

    ax.plot(
        monthly["Month"],
        monthly["Enrollments"],
        marker="o"
    )

    plt.xticks(rotation=45)

    ax.set_xlabel("Month")

    ax.set_ylabel("Enrollments")

    st.pyplot(fig)

st.markdown("---")

# TOP 10 MOST POPULAR COURSES

st.subheader("🏆 Top 10 Most Popular Courses")

top_courses = (
    filtered_df["CourseName"]
    .value_counts()
    .head(10)
)

fig, ax = plt.subplots(figsize=(10,5))

ax.barh(
    top_courses.index,
    top_courses.values
)

ax.set_xlabel("Enrollments")
ax.set_ylabel("Course Name")
ax.set_title("Top 10 Most Popular Courses")

plt.gca().invert_yaxis()

st.pyplot(fig)

st.markdown("---")

# COURSE CATEGORY VS COURSE LEVEL

st.subheader("🔥 Course Category vs Course Level")

heatmap_data = pd.crosstab(
    filtered_df["CourseCategory"],
    filtered_df["CourseLevel"]
)

fig, ax = plt.subplots(figsize=(10,6))

sns.heatmap(
    heatmap_data,
    annot=True,
    cmap="Blues",
    fmt="d",
    ax=ax
)

st.pyplot(fig)

st.markdown("---")

# FILTERED DATASET

st.subheader("Filtered Dataset")

st.dataframe(filtered_df)

st.markdown("---")

# DATASET INFORMATION

st.subheader("Dataset Information")

col1, col2 = st.columns(2)

with col1:
    st.info(f"Rows : {filtered_df.shape[0]}")

with col2:
    st.info(f"Columns : {filtered_df.shape[1]}")

# DOWNLOAD FILTERED DATASET

st.subheader("📥 Download Filtered Dataset")

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Dataset as CSV",
    data=csv,
    file_name="Filtered_EduPro_Data.csv",
    mime="text/csv"
)

# FOOTER

st.markdown("---")

st.markdown(
    """
    ### 📘 About This Dashboard

    This dashboard was developed as part of an Education Analytics project.

    It provides interactive insights into:
    - Learner demographics
    - Enrollment statistics
    - Course popularity
    - Learning trends
    - Business insights

    **Developed using:** Python, Pandas, Matplotlib, Seaborn and Streamlit.
    """
)