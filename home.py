import streamlit as st
import pandas as pd
import plotly.express as px
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

# Load the datasets
keywords_data = pd.read_csv("keywords.tsv", sep="\t")
faculty_data = pd.read_csv("faculty.tsv", sep="\t")


# Helper function to merge the datasets based on article_number
def merge_data(keywords_data, faculty_data):
    faculty_data["article_number"] = faculty_data["article_number"].str.split(", ")
    faculty_exploded = faculty_data.explode("article_number").dropna()
    faculty_exploded["article_number"] = faculty_exploded["article_number"].astype(int)

    merged_data = pd.merge(
        keywords_data, faculty_exploded, on="article_number", how="left"
    )
    return merged_data


merged_data = merge_data(keywords_data, faculty_data)

# Define the goal labels
goal_labels = {
    "goal1": "G1: No Poverty",
    "goal2": "G2: Zero Hunger",
    "goal3": "G3: Good Health",
    "goal4": "G4: Quality Education",
    "goal5": "G5: Gender Equality",
    "goal6": "G6: Clean Water",
    "goal7": "G7: Clean Energy",
    "goal8": "G8: Work & Economy",
    "goal9": "G9: Innovation & Infrastructure",
    "goal10": "G10: Reduced Inequalities",
    "goal11": "G11: Sustainable Cities",
    "goal12": "G12: Responsible Consumption",
    "goal13": "G13: Climate Action",
    "goal14": "G14: Life Below Water",
    "goal15": "G15: Life on Land",
    "goal16": "G16: Peace & Justice",
    "goal17": "G17: Partnerships",
}

# Create reverse mapping from label to column name
label_to_goal = {v: k for k, v in goal_labels.items()}

# Initialize session state variables
if "selected_departments" not in st.session_state:
    all_departments = merged_data["department"].unique().tolist()
    st.session_state.selected_departments = all_departments.copy()

if "selected_goals" not in st.session_state:
    st.session_state.selected_goals = list(
        goal_labels.values()
    )  # default to all labels

# Sidebar filters with collapsible sections
st.sidebar.header("Filter Options")

# Expander for Department Selection
with st.sidebar.expander("Select Department(s)"):
    all_departments = merged_data["department"].unique().tolist()

    def select_all_departments():
        st.session_state.selected_departments = all_departments.copy()

    def deselect_all_departments():
        st.session_state.selected_departments = []

    st.button("Select All Departments", on_click=select_all_departments)
    st.button("Deselect All Departments", on_click=deselect_all_departments)

    selected_departments = st.multiselect(
        "Choose Department(s)",
        options=all_departments,
        key="selected_departments",
    )

# Expander for Year Selection
years = st.sidebar.slider(
    "Select Publication Year Range",
    min_value=int(merged_data["publication_year"].min()),
    max_value=int(merged_data["publication_year"].max()),
    value=(
        int(merged_data["publication_year"].min()),
        int(merged_data["publication_year"].max()),
    ),
)

# Expander for Goal Selection
with st.sidebar.expander("Select Sustainability Goal(s)"):

    def select_all_goals():
        st.session_state.selected_goals = list(goal_labels.values())

    def deselect_all_goals():
        st.session_state.selected_goals = []

    st.button("Select All Goals", on_click=select_all_goals)
    st.button("Deselect All Goals", on_click=deselect_all_goals)

    selected_goals_labels = st.multiselect(
        "Choose Goals",
        options=list(goal_labels.values()),
        key="selected_goals",
    )

# Map selected goal labels back to column names
selected_goals = [label_to_goal[label] for label in selected_goals_labels]

# Apply filters
filtered_data = merged_data[
    (merged_data["department"].isin(selected_departments))
    & (merged_data["publication_year"].between(years[0], years[1]))
]

# Handle case when no goals are selected
if not selected_goals:
    st.error("Please select at least one Sustainability Goal.")
    st.stop()

# Tabs for different visualizations
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs(
    [
        "Article Goal Distribution",
        "Goal Coverage by Year",
        "Department Goal Focus",
        "Departmental Distribution",
        "Top Departments per Goal",
        "Proportion of Goals within Departments",
        "Departmental Focus Over Time",
        "Bubble Chart of Articles by Year and Goal",
        "Treemap of Articles by Department and Goal",
    ]
)

# Tab 1: Article Goal Distribution
with tab1:
    st.subheader("Article Goal Distribution")
    goal_distribution = filtered_data[selected_goals].sum().reset_index()
    goal_distribution.columns = ["Goal", "Total"]
    # Map 'Goal' column to labels
    goal_distribution["Goal"] = goal_distribution["Goal"].map(goal_labels)

    fig = px.bar(
        goal_distribution,
        x="Goal",
        y="Total",
        title="Distribution of Articles by Sustainability Goal",
    )
    st.plotly_chart(fig)

# Tab 2: Goal Coverage by Year
with tab2:
    st.subheader("Goal Coverage by Year")
    goal_year_data = (
        filtered_data.groupby("publication_year")[selected_goals].sum().reset_index()
    )
    goal_year_data_melted = pd.melt(
        goal_year_data,
        id_vars="publication_year",
        value_vars=selected_goals,
        var_name="Goal",
        value_name="Keyword Matches",
    )
    # Map 'Goal' column to labels
    goal_year_data_melted["Goal"] = goal_year_data_melted["Goal"].map(goal_labels)

    fig = px.line(
        goal_year_data_melted,
        x="publication_year",
        y="Keyword Matches",
        color="Goal",
        title="Goal Coverage Over Time",
    )
    st.plotly_chart(fig)

# Tab 3: Department Goal Focus
with tab3:
    st.subheader("Department Goal Focus")
    dept_goal_focus = (
        filtered_data.groupby("department")[selected_goals].sum().reset_index()
    )
    dept_goal_focus_melted = pd.melt(
        dept_goal_focus,
        id_vars="department",
        value_vars=selected_goals,
        var_name="Goal",
        value_name="Keyword Matches",
    )
    # Map 'Goal' column to labels
    dept_goal_focus_melted["Goal"] = dept_goal_focus_melted["Goal"].map(goal_labels)

    fig = px.bar(
        dept_goal_focus_melted,
        x="department",
        y="Keyword Matches",
        color="Goal",
        title="Department Focus on Sustainability Goals",
        barmode="stack",
    )
    st.plotly_chart(fig)

# Tab 4: Departmental Distribution of Articles
with tab4:
    st.subheader("Departmental Distribution of Articles")
    dept_article_distribution = filtered_data["department"].value_counts().reset_index()
    dept_article_distribution.columns = ["Department", "Total Articles"]

    fig = px.bar(
        dept_article_distribution,
        x="Department",
        y="Total Articles",
        title="Number of Articles by Department",
    )
    st.plotly_chart(fig)

# Tab 5: Top Departments per Goal
with tab5:
    st.subheader("Top Contributing Departments per Goal")

    # Compute total contributions per department per goal
    dept_goal_total = (
        filtered_data.groupby("department")[selected_goals].sum().reset_index()
    )
    dept_goal_melted = dept_goal_total.melt(
        id_vars="department",
        value_vars=selected_goals,
        var_name="Goal",
        value_name="Total",
    )
    # Map 'Goal' column to labels
    dept_goal_melted["Goal"] = dept_goal_melted["Goal"].map(goal_labels)

    # For each selected goal, plot the top departments
    for goal_label in selected_goals_labels:
        st.write(f"### {goal_label}")
        goal_data = dept_goal_melted[dept_goal_melted["Goal"] == goal_label]
        goal_data = goal_data.sort_values(by="Total", ascending=True)

        fig = px.bar(
            goal_data,
            x="Total",
            y="department",
            orientation="h",
            title=f"Top Departments for {goal_label}",
        )
        st.plotly_chart(fig)

# Tab 6: Proportion of Goals within Departments
with tab6:
    st.subheader("Proportion of Goals within Departments")

    # Compute total keyword matches per department per goal
    dept_goal_total = (
        filtered_data.groupby("department")[selected_goals].sum().reset_index()
    )
    dept_goal_total["Total"] = dept_goal_total[selected_goals].sum(axis=1)

    # Melt the data to get department, goal, keyword matches
    dept_goal_melted = dept_goal_total.melt(
        id_vars=["department", "Total"],
        value_vars=selected_goals,
        var_name="Goal",
        value_name="Keyword Matches",
    )
    # Map 'Goal' column to labels
    dept_goal_melted["Goal"] = dept_goal_melted["Goal"].map(goal_labels)

    # Compute proportion
    dept_goal_melted["Proportion"] = (
        dept_goal_melted["Keyword Matches"] / dept_goal_melted["Total"]
    )

    # Plot stacked bar chart showing proportions
    fig = px.bar(
        dept_goal_melted,
        x="department",
        y="Keyword Matches",
        color="Goal",
        title="Proportion of Goals within Departments",
        barmode="stack",
    )
    st.plotly_chart(fig)

    # Optionally, select a department to view pie chart
    st.write("### View Proportion of Goals in a Specific Department")
    department_options = dept_goal_total["department"].unique()
    selected_dept = st.selectbox("Select a Department", options=department_options)

    dept_data = dept_goal_total[dept_goal_total["department"] == selected_dept]
    dept_data_melted = dept_data.melt(
        id_vars=["department", "Total"],
        value_vars=selected_goals,
        var_name="Goal",
        value_name="Keyword Matches",
    )
    # Map 'Goal' column to labels
    dept_data_melted["Goal"] = dept_data_melted["Goal"].map(goal_labels)

    fig = px.pie(
        dept_data_melted,
        names="Goal",
        values="Keyword Matches",
        title=f"Proportion of Goals within {selected_dept}",
    )
    st.plotly_chart(fig)

# Tab 7: Departmental Focus Over Time
with tab7:
    st.subheader("Departmental Focus Over Time")

    # Select department
    departments = filtered_data["department"].unique()
    selected_dept = st.selectbox(
        "Select a Department", options=departments, key="dept_focus_over_time"
    )

    # Filter data for the selected department
    dept_data = filtered_data[filtered_data["department"] == selected_dept]

    # Group data by publication_year and sum keyword matches per goal
    dept_goal_year = (
        dept_data.groupby("publication_year")[selected_goals].sum().reset_index()
    )

    # Melt data for plotting
    dept_goal_year_melted = dept_goal_year.melt(
        id_vars="publication_year",
        value_vars=selected_goals,
        var_name="Goal",
        value_name="Keyword Matches",
    )
    # Map 'Goal' column to labels
    dept_goal_year_melted["Goal"] = dept_goal_year_melted["Goal"].map(goal_labels)

    # Plot stacked area chart
    fig = px.area(
        dept_goal_year_melted,
        x="publication_year",
        y="Keyword Matches",
        color="Goal",
        title=f"Departmental Focus Over Time for {selected_dept}",
    )
    st.plotly_chart(fig)

# Tab 8: Bubble Chart of Articles by Year and Goal
with tab8:
    st.subheader("Bubble Chart of Articles by Year and Goal")

    # Create boolean columns indicating whether the article has matches for each goal
    for goal in selected_goals:
        bool_col = f"{goal}_bool"
        filtered_data[bool_col] = filtered_data[goal] > 0

    # Melt the data
    goal_bool_cols = [f"{goal}_bool" for goal in selected_goals]
    melted = filtered_data.melt(
        id_vars=["publication_year"],
        value_vars=goal_bool_cols,
        var_name="Goal",
        value_name="Has_Match",
    )

    # Clean up Goal names
    melted["Goal"] = melted["Goal"].str.replace("_bool", "")
    # Map 'Goal' column to labels
    melted["Goal"] = melted["Goal"].map(goal_labels)

    # Filter only articles that have matches
    melted = melted[melted["Has_Match"] == True]

    # Group by publication_year and Goal, count number of articles
    bubble_data = (
        melted.groupby(["publication_year", "Goal"])
        .size()
        .reset_index(name="Num_Articles")
    )

    # Plot bubble chart
    fig = px.scatter(
        bubble_data,
        x="publication_year",
        y="Goal",
        size="Num_Articles",
        title="Bubble Chart of Articles by Year and Goal",
        size_max=60,
    )
    st.plotly_chart(fig)

# Tab 9: Treemap of Articles by Department and Goal
with tab9:
    st.subheader("Treemap of Articles by Department and Goal")

    # Create boolean columns indicating whether the article has matches for each goal
    for goal in selected_goals:
        bool_col = f"{goal}_bool"
        filtered_data[bool_col] = filtered_data[goal] > 0

    # Melt the data to have one row per article per goal
    goal_bool_cols = [f"{goal}_bool" for goal in selected_goals]
    melted = filtered_data.melt(
        id_vars=["article_number", "department"],
        value_vars=goal_bool_cols,
        var_name="Goal",
        value_name="Has_Match",
    )

    # Clean up Goal names
    melted["Goal"] = melted["Goal"].str.replace("_bool", "")
    # Map 'Goal' column to labels
    melted["Goal"] = melted["Goal"].map(goal_labels)

    # Filter only articles that have matches
    melted = melted[melted["Has_Match"] == True]

    # Group by department and Goal, count number of articles
    treemap_data = (
        melted.groupby(["department", "Goal"]).size().reset_index(name="Num_Articles")
    )

    # Plot treemap
    fig = px.treemap(
        treemap_data,
        path=["department", "Goal"],
        values="Num_Articles",
        title="Treemap of Articles by Department and Goal",
    )
    st.plotly_chart(fig)

# Allow user to download filtered dataset
st.sidebar.download_button(
    "Download Filtered Data as CSV",
    data=filtered_data.to_csv(index=False),
    file_name="filtered_data.csv",
)
