"""
AI Legislation Dashboard with Federal Preemption Analysis
Explore U.S. state-level AI legislation (2023-2025) with focus on
December 2025 Executive Order preemption risk.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ============================================================================
# CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="State AI Legislation Dashboard with Federal Preemption Analysis",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Color schemes
RISK_COLORS = {
    'High Risk': '#e74c3c',
    'Moderate Risk': '#f39c12',
    'Low Risk': '#27ae60',
    'Pending - High Exposure': '#fadbd8',
    'Pending - Some Exposure': '#fdebd0',
    'Pending - Low Exposure': '#d5f5e3'
}

STATUS_COLORS = {
    'Passed': '#2ecc71',
    'Failed': '#e74c3c',
    'Vetoed': '#9b59b6',
    'Introduced': '#3498db',
    'Engrossed': '#f39c12',
    'Enrolled': '#1abc9c'
}

# Subject area colors
SUBJECT_COLORS = {
    'Healthcare': '#e74c3c',
    'Education': '#3498db',
    'Employment': '#9b59b6',
    'Elections': '#f39c12',
    'Children': '#1abc9c',
    'Deepfakes': '#e67e22',
    'Government': '#2c3e50',
    'Privacy': '#16a085',
    'Criminal': '#c0392b',
    'Financial': '#27ae60',
    'Vehicles': '#7f8c8d',
    'AI Governance': '#8e44ad',
    'AI Policy/Task Forces': '#2980b9',
    'Consumer Protection': '#d35400',
    'Digital Content/IP': '#c0392b',
    'Cybersecurity': '#1abc9c',
    'Infrastructure': '#34495e',
    'Housing': '#e67e22',
    'Legal/Judicial': '#7f8c8d',
    'Social Media': '#3498db',
    'Adult Content': '#95a5a6',
    'Weapons/Defense': '#2c3e50',
    'Licensing': '#16a085',
    'Insurance': '#27ae60',
    'Blockchain/Crypto': '#9b59b6',
    'Telecommunications': '#3498db',
    'General/Other': '#bdc3c7'
}

PROTECTED_COLOR = '#3498db'
TARGETED_COLOR = '#e74c3c'

# Subject areas list (ordered by typical bill count)
SUBJECT_AREAS = [
    'Healthcare', 'Government', 'Education', 'AI Governance', 'AI Policy/Task Forces',
    'Employment', 'Criminal', 'Elections', 'Digital Content/IP', 'Financial',
    'Children', 'Privacy', 'Cybersecurity', 'Consumer Protection', 'Infrastructure',
    'Deepfakes', 'Licensing', 'Legal/Judicial', 'Housing', 'Social Media',
    'Adult Content', 'Weapons/Defense', 'Insurance', 'Vehicles', 'Blockchain/Crypto',
    'Telecommunications', 'General/Other'
]

# ============================================================================
# DATA LOADING
# ============================================================================

@st.cache_data(ttl=60)  # Cache for 60 seconds to pick up data changes
def load_data():
    """Load and preprocess the legislation data."""
    df = pd.read_csv('data/ai_legislation_with_eo_risk.csv')

    # Convert date column
    df['Last Action Date'] = pd.to_datetime(df['Last Action Date'], errors='coerce')

    # Ensure numeric columns are numeric
    numeric_cols = ['Status', 'Year', 'EO_Risk_Count', 'State_Total_Risk_Points',
                    'EO_Targeted_Nondiscrimination', 'EO_Targeted_Notice',
                    'EO_Targeted_Assessments', 'EO_Protected_ChildSafety',
                    'EO_Protected_GovProcurement', 'EO_Protected_Infrastructure',
                    'EO_Has_Protection', 'EO_State_Named']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # Parse Subject_Areas for filtering
    df['Subject_Areas'] = df['Subject_Areas'].fillna('')

    return df


def get_subject_area_stats(df):
    """Calculate statistics by subject area."""
    import re
    stats = []
    passed_df = df[df['Status'] == 4]

    for subj in SUBJECT_AREAS:
        # Escape special regex characters and use word boundary matching
        escaped_subj = re.escape(subj)
        mask = df['Subject_Areas'].str.contains(escaped_subj, case=False, na=False, regex=True)
        passed_mask = passed_df['Subject_Areas'].str.contains(escaped_subj, case=False, na=False, regex=True)

        subj_df = df[mask]
        subj_passed = passed_df[passed_mask]

        if len(subj_df) > 0:
            stats.append({
                'Subject Area': subj,
                'Total Bills': len(subj_df),
                'Passed Bills': len(subj_passed),
                'Passage Rate': len(subj_passed) / len(subj_df) * 100 if len(subj_df) > 0 else 0,
                'High Risk': len(subj_passed[subj_passed['EO_Risk_Level'] == 'High Risk']),
                'Moderate Risk': len(subj_passed[subj_passed['EO_Risk_Level'] == 'Moderate Risk']),
                'Low Risk': len(subj_passed[subj_passed['EO_Risk_Level'] == 'Low Risk']),
                'Total Risk Points': subj_passed['EO_Risk_Count'].sum(),
                'Protected Bills': subj_passed['EO_Has_Protection'].sum()
            })

    return pd.DataFrame(stats)


# ============================================================================
# SIDEBAR FILTERS
# ============================================================================

def apply_filters(df):
    """Apply sidebar filters to the dataframe."""

    # Logo at top of sidebar
    st.sidebar.image("vaill_logo.png", width=200)
    st.sidebar.markdown("---")

    # About section with explanations
    with st.sidebar.expander("About This Dashboard", expanded=False):
        st.markdown("""
        **What is this dashboard?**

        This dashboard tracks U.S. state-level AI legislation from 2022-2025 and analyzes which laws may be at risk from the December 2025 Executive Order on federal AI preemption.

        ---

        **Subject Areas**

        Bills are classified into 27 subject areas:

        *Core Policy Domains:*
        - **Healthcare**: Medical decisions, diagnostics, insurance
        - **Education**: Schools, learning tools, curriculum
        - **Employment**: Hiring, workplace, labor
        - **Elections**: Voting, campaigns, political ads
        - **Criminal**: Law enforcement, justice system
        - **Financial**: Banking, lending, credit
        - **Children**: Child safety, minors' data
        - **Privacy**: Data protection, consumer rights
        - **Government**: Public sector AI, procurement

        *AI-Specific:*
        - **AI Governance**: Accountability, transparency, safety
        - **AI Policy/Task Forces**: Commissions, studies, research
        - **Deepfakes**: Synthetic media, AI-generated content
        - **Digital Content/IP**: Likeness, publicity rights

        *Infrastructure & Tech:*
        - **Cybersecurity**: Data breaches, IT security
        - **Infrastructure**: Data centers, utilities
        - **Telecommunications**: Robocalls, broadband

        *Other Sectors:*
        - **Consumer Protection**: Deceptive practices
        - **Housing**: Rental algorithms, real estate
        - **Legal/Judicial**: Courts, litigation
        - **Insurance**, **Vehicles**, **Social Media**, etc.
        - **General/Other**: Resolutions, misc.

        ---

        **Understanding Risk Levels**

        Risk is determined by whether a bill contains provisions the EO targets:

        *For Passed Bills:*
        - **High Risk**: 2+ targeted provisions
        - **Moderate Risk**: 1 targeted provision
        - **Low Risk**: No targeted provisions

        *For Pending Bills:*
        - **High Exposure**: 2+ targeted provisions
        - **Some Exposure**: 1 targeted provision
        - **Low Exposure**: No targeted provisions

        ---

        **What Makes a Bill "Targeted"?**

        The EO criticizes state laws requiring:
        - **Nondiscrimination**: AI systems must not discriminate
        - **General Notice**: Disclose when AI is used
        - **Assessments**: Impact assessments or audits

        ---

        **What Bills Are "Protected"?**

        The EO carves out protections for laws about:
        - **Child Safety**: Protecting minors
        - **Government Procurement**: State/local AI purchases
        - **Infrastructure**: Data centers, broadband
        """)

    st.sidebar.markdown("---")

    st.sidebar.header("Filters")

    # Subject area filter (moved to top for emphasis)
    selected_subjects = st.sidebar.multiselect(
        "Subject Area",
        options=SUBJECT_AREAS,
        default=[],
        placeholder="All subject areas"
    )

    # State filter
    states = sorted(df['State_Name'].unique())
    selected_states = st.sidebar.multiselect(
        "State",
        options=states,
        default=[],
        placeholder="All states"
    )

    # Year filter
    years = sorted(df['Year'].unique())
    selected_years = st.sidebar.multiselect(
        "Year",
        options=years,
        default=[],
        placeholder="All years"
    )

    # Status filter
    statuses = df['Status_Label'].unique()
    selected_statuses = st.sidebar.multiselect(
        "Status",
        options=statuses,
        default=[],
        placeholder="All statuses"
    )

    # EO Risk Level filter
    risk_levels = df['EO_Risk_Level'].dropna().unique()
    selected_risk_levels = st.sidebar.multiselect(
        "EO Risk Level",
        options=risk_levels,
        default=[],
        placeholder="All risk levels"
    )

    st.sidebar.markdown("---")

    # EO-specific filters
    show_targeted = st.sidebar.checkbox("Show only targeted bills", value=False)
    show_protected = st.sidebar.checkbox("Show only protected bills", value=False)

    # General/Other filter with explanation
    exclude_low_risk_other = st.sidebar.checkbox(
        "Exclude low-risk General/Other bills",
        value=False,
        help="Remove bills categorized as General/Other with Low Risk from the analysis. These are often resolutions, commendations, or bills that mention AI incidentally."
    )

    st.sidebar.markdown("---")

    # Search filter
    search_term = st.sidebar.text_input("Search bill titles", "")

    # Reset button
    if st.sidebar.button("Reset Filters", type="secondary"):
        st.rerun()

    # Apply filters
    filtered_df = df.copy()

    if selected_subjects:
        mask = filtered_df['Subject_Areas'].apply(
            lambda x: any(s in str(x) for s in selected_subjects) if pd.notna(x) else False
        )
        filtered_df = filtered_df[mask]

    if selected_states:
        filtered_df = filtered_df[filtered_df['State_Name'].isin(selected_states)]

    if selected_years:
        filtered_df = filtered_df[filtered_df['Year'].isin(selected_years)]

    if selected_statuses:
        filtered_df = filtered_df[filtered_df['Status_Label'].isin(selected_statuses)]

    if selected_risk_levels:
        filtered_df = filtered_df[filtered_df['EO_Risk_Level'].isin(selected_risk_levels)]

    if show_targeted:
        filtered_df = filtered_df[filtered_df['EO_Risk_Count'] > 0]

    if show_protected:
        filtered_df = filtered_df[filtered_df['EO_Has_Protection'] == 1]

    if exclude_low_risk_other:
        # Exclude bills that are ONLY in General/Other AND are Low Risk (passed) or Low Exposure (pending)
        low_risk_other_mask = (
            (filtered_df['Subject_Areas'] == 'General/Other') &
            (filtered_df['EO_Risk_Level'].isin(['Low Risk', 'Pending - Low Exposure']))
        )
        filtered_df = filtered_df[~low_risk_other_mask]

    if search_term:
        filtered_df = filtered_df[
            filtered_df['Title'].str.contains(search_term, case=False, na=False)
        ]

    return filtered_df

# ============================================================================
# TAB 1: OVERVIEW
# ============================================================================

def render_overview_tab(df, full_df):
    """Render the Overview tab with key metrics and map."""

    # Executive Order info box - prominent placement
    st.info("""
    **About the December 2025 Executive Order**

    On December 11, 2025, the Trump administration signed Executive Order "Eliminating State Law Obstruction of National Artificial Intelligence Policy."
    This order represents a significant federal effort to limit state-level AI regulation. Key provisions include:

    - **AI Litigation Task Force**: A new body to challenge state laws in court
    - **Commerce Department Review**: Must identify "onerous" state AI laws within 90 days
    - **Federal Funding Leverage**: Threatens to withhold broadband funding from non-compliant states
    - **Colorado Named**: Explicitly cites Colorado's SB205 as an example of problematic legislation

    [Read the full Executive Order](https://www.whitehouse.gov/presidential-actions/2025/12/eliminating-state-law-obstruction-of-national-artificial-intelligence-policy/)
    """)

    # Brief intro
    st.markdown("""
    This dashboard tracks **{:,}** AI-related bills across U.S. states, organized by **subject area**.
    Use the sidebar filters to explore specific topics, states, or risk levels.
    The **Federal Preemption Risk** tab analyzes which subject areas face the greatest risk from the Executive Order.
    """.format(len(full_df)))

    st.markdown("---")

    # Key metrics row
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Bills", len(df))

    with col2:
        passed = len(df[df['Status'] == 4])
        total = len(df)
        rate = (passed / total * 100) if total > 0 else 0
        st.metric("Passage Rate", f"{rate:.1f}%")

    with col3:
        if len(df) > 0 and len(df['State_Name'].dropna()) > 0:
            most_active = df['State_Name'].value_counts().idxmax()
            count = df['State_Name'].value_counts().max()
            st.metric("Most Active State", most_active, f"{count} bills")
        else:
            st.metric("Most Active State", "N/A", "No data")

    with col4:
        high_risk = len(df[(df['Status'] == 4) & (df['EO_Risk_Level'] == 'High Risk')])
        st.metric("Bills at High Risk", high_risk, help="Passed bills with High Risk level")

    with col5:
        protected = len(df[(df['Status'] == 4) & (df['EO_Has_Protection'] == 1)])
        st.metric("Bills with Protection", protected, help="Passed bills in protected categories")

    st.markdown("---")

    # Subject Area Overview
    st.subheader("Bills by Subject Area")

    subject_stats = get_subject_area_stats(df)

    if len(subject_stats) > 0:
        subject_stats = subject_stats.sort_values('Total Bills', ascending=True)

        col1, col2 = st.columns([2, 1])

        with col1:
            fig = px.bar(
                subject_stats,
                x='Total Bills',
                y='Subject Area',
                orientation='h',
                title='Legislative Activity by Subject Area',
                color='Subject Area',
                color_discrete_map=SUBJECT_COLORS
            )
            fig.update_layout(showlegend=False, yaxis_title="", height=450)
            st.plotly_chart(fig, use_container_width=True, key="overview_subject_bar")

        with col2:
            # Quick stats table
            st.markdown("**Quick Stats**")
            quick_stats = subject_stats[['Subject Area', 'Total Bills', 'Passed Bills', 'Total Risk Points']].copy()
            quick_stats = quick_stats.sort_values('Total Bills', ascending=False)
            st.dataframe(quick_stats, hide_index=True, use_container_width=True, height=400)
    else:
        st.info("No bills match the current filter criteria.")

    st.markdown("---")

    # Map section
    if len(df) > 0:
        col_map, col_toggle = st.columns([4, 1])

        with col_toggle:
            map_mode = st.radio(
                "Color map by:",
                ["Total Bills", "Risk Score"],
                index=0
            )

        with col_map:
            if map_mode == "Total Bills":
                state_data = df.groupby('State').size().reset_index(name='Count')
                fig = px.choropleth(
                    state_data,
                    locations='State',
                    locationmode='USA-states',
                    color='Count',
                    scope='usa',
                    color_continuous_scale='Blues',
                    title='Bills by State'
                )
            else:
                # Risk score map (passed bills only)
                passed_for_map = df[df['Status'] == 4]
                if len(passed_for_map) > 0:
                    state_risk = passed_for_map.groupby('State').agg({
                        'State_Total_Risk_Points': 'first'
                    }).reset_index()
                    state_risk.columns = ['State', 'Risk_Score']
                    fig = px.choropleth(
                        state_risk,
                        locations='State',
                        locationmode='USA-states',
                        color='Risk_Score',
                        scope='usa',
                        color_continuous_scale='Reds',
                        title='State AI Law Risk Exposure (Passed Bills)'
                    )
                else:
                    # Fallback to empty map
                    fig = px.choropleth(
                        locations=[],
                        locationmode='USA-states',
                        scope='usa',
                        title='No passed bills for selected filters'
                    )

            fig.update_layout(
                geo=dict(bgcolor='rgba(0,0,0,0)'),
                margin=dict(l=0, r=0, t=40, b=0),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True, key="overview_map")

# ============================================================================
# TAB 2: SUBJECT AREAS (NEW - replaces old position)
# ============================================================================

def render_subject_areas_tab(df):
    """Render the Subject Areas analysis tab."""

    st.markdown("""
    **Subject areas** represent the primary policy domain each bill addresses. Understanding how AI legislation
    is distributed across subject areas helps identify where states are focusing their regulatory efforts
    and which domains face the greatest preemption risk.
    """)

    # Explainer about General/Other category
    with st.expander("About the General/Other Category", expanded=False):
        st.markdown("""
        **Why is General/Other so large?**

        The General/Other category contains **427 bills** that don't fit neatly into specific policy domains. This includes:

        - **Resolutions and commendations** (e.g., recognizing AI research centers, honoring tech leaders)
        - **Omnibus bills** that mention AI among many other topics
        - **Definitional bills** that establish legal definitions without specific regulations
        - **Study and reporting requirements** that don't create substantive AI rules
        - **Bills with incidental AI mentions** (e.g., general technology appropriations)

        **Why does this matter for risk analysis?**

        Most General/Other bills (92 of 127 passed) are **Low Risk** because they don't contain the regulatory provisions
        the Executive Order targets. Including them can dilute the risk picture.

        **Recommendation:** Use the sidebar filter "Exclude low-risk General/Other bills" to focus your analysis
        on substantive AI regulatory legislation.
        """)

    st.markdown("---")

    # Subject area selector
    selected_subject = st.selectbox(
        "Select a subject area to explore:",
        options=['All Subject Areas'] + SUBJECT_AREAS
    )

    if selected_subject == 'All Subject Areas':
        render_all_subjects_view(df)
    else:
        render_single_subject_view(df, selected_subject)


def render_all_subjects_view(df):
    """Render overview of all subject areas."""

    subject_stats = get_subject_area_stats(df)

    # Check if we have any data
    if len(subject_stats) == 0:
        st.info("No bills match the current filter criteria.")
        return

    # Risk by subject area
    st.subheader("Risk Analysis by Subject Area")

    col1, col2 = st.columns(2)

    with col1:
        # Stacked bar of risk levels
        risk_data = subject_stats[['Subject Area', 'High Risk', 'Moderate Risk', 'Low Risk']].melt(
            id_vars=['Subject Area'],
            var_name='Risk Level',
            value_name='Count'
        )

        fig = px.bar(
            risk_data,
            x='Subject Area',
            y='Count',
            color='Risk Level',
            title='Risk Distribution by Subject Area (Passed Bills)',
            color_discrete_map={
                'High Risk': RISK_COLORS['High Risk'],
                'Moderate Risk': RISK_COLORS['Moderate Risk'],
                'Low Risk': RISK_COLORS['Low Risk']
            },
            barmode='stack'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True, key="subj_risk_dist")

    with col2:
        # Risk points comparison
        subject_stats_sorted = subject_stats.sort_values('Total Risk Points', ascending=True)

        fig = px.bar(
            subject_stats_sorted,
            x='Total Risk Points',
            y='Subject Area',
            orientation='h',
            title='Total Risk Points by Subject Area',
            color='Total Risk Points',
            color_continuous_scale='Reds'
        )
        fig.update_layout(yaxis_title="", showlegend=False)
        st.plotly_chart(fig, use_container_width=True, key="subj_risk_points")

    st.markdown("---")

    # Subject area comparison table
    st.subheader("Subject Area Comparison")

    display_stats = subject_stats.copy()
    display_stats['Passage Rate'] = display_stats['Passage Rate'].round(1).astype(str) + '%'
    display_stats = display_stats.sort_values('Total Bills', ascending=False)

    st.dataframe(
        display_stats[['Subject Area', 'Total Bills', 'Passed Bills', 'Passage Rate',
                       'High Risk', 'Moderate Risk', 'Low Risk', 'Total Risk Points', 'Protected Bills']],
        hide_index=True,
        use_container_width=True
    )

    st.markdown("---")

    # Year-over-year trends
    st.subheader("Subject Area Trends Over Time")

    subject_yearly = []
    for _, row in df.iterrows():
        subjects = str(row['Subject_Areas']).split(';')
        for s in subjects:
            s = s.strip()
            if s:  # Accept any non-empty subject
                subject_yearly.append({'Year': row['Year'], 'Subject': s})

    if subject_yearly:
        subject_df = pd.DataFrame(subject_yearly)
        # Get top subjects for cleaner visualization
        top_subjects = subject_df['Subject'].value_counts().head(12).index
        subject_df_filtered = subject_df[subject_df['Subject'].isin(top_subjects)]
        subject_counts = subject_df_filtered.groupby(['Year', 'Subject']).size().reset_index(name='Count')

        fig = px.line(
            subject_counts,
            x='Year',
            y='Count',
            color='Subject',
            title='Top Subject Areas Over Time',
            markers=True,
            color_discrete_map=SUBJECT_COLORS
        )
        fig.update_xaxes(tickmode='linear', tick0=subject_counts['Year'].min(), dtick=1, tickformat='d')
        st.plotly_chart(fig, use_container_width=True, key="subj_trends_line")


def render_single_subject_view(df, subject):
    """Render detailed view for a single subject area."""
    import re

    # Filter to this subject (escape special chars for regex)
    escaped_subject = re.escape(subject)
    mask = df['Subject_Areas'].str.contains(escaped_subject, case=False, na=False, regex=True)
    subj_df = df[mask]
    passed_df = subj_df[subj_df['Status'] == 4]

    # Check for empty data
    if len(subj_df) == 0:
        st.info(f"No {subject} bills match the current filter criteria.")
        return

    # Header metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(f"Total {subject} Bills", len(subj_df))
    with col2:
        st.metric("Passed", len(passed_df))
    with col3:
        high_risk = len(passed_df[passed_df['EO_Risk_Level'] == 'High Risk'])
        st.metric("High Risk", high_risk)
    with col4:
        risk_pts = passed_df['EO_Risk_Count'].sum()
        st.metric("Total Risk Points", risk_pts)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        # State breakdown
        st.subheader(f"{subject} Bills by State")
        state_counts = subj_df.groupby('State_Name').size().reset_index(name='Count')
        if len(state_counts) > 0:
            state_counts = state_counts.sort_values('Count', ascending=True).tail(15)

            fig = px.bar(
                state_counts,
                x='Count',
                y='State_Name',
                orientation='h',
                color_discrete_sequence=[SUBJECT_COLORS.get(subject, '#3498db')]
            )
            fig.update_layout(yaxis_title="", height=400)
            st.plotly_chart(fig, use_container_width=True, key="single_subj_state_bar")
        else:
            st.info("No state data available.")

    with col2:
        # Risk distribution
        st.subheader(f"{subject} Risk Distribution")
        if len(passed_df) > 0:
            risk_counts = passed_df['EO_Risk_Level'].value_counts().reset_index()
            risk_counts.columns = ['Risk Level', 'Count']

            fig = px.pie(
                risk_counts,
                values='Count',
                names='Risk Level',
                color='Risk Level',
                color_discrete_map=RISK_COLORS,
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True, key="single_subj_risk_pie")
        else:
            st.info("No passed bills in this subject area.")

    st.markdown("---")

    # Bills table
    st.subheader(f"{subject} Bills")
    st.dataframe(
        subj_df[['State', 'Bill Number', 'Title', 'Status_Label', 'Year', 'EO_Risk_Level', 'View']],
        column_config={
            "View": st.column_config.LinkColumn("View Bill", display_text="View")
        },
        hide_index=True,
        use_container_width=True,
        height=400
    )


# ============================================================================
# TAB 3: TRENDS
# ============================================================================

def render_trends_tab(df):
    """Render the Trends Over Time tab."""

    col1, col2 = st.columns(2)

    with col1:
        # Bills by year
        yearly = df.groupby('Year').size().reset_index(name='Count')
        if len(yearly) > 0:
            fig = px.bar(
                yearly,
                x='Year',
                y='Count',
                title='Bills by Year',
                color_discrete_sequence=['#3498db']
            )
            fig.update_layout(xaxis_title="Year", yaxis_title="Number of Bills")
            fig.update_xaxes(tickmode='linear', tick0=yearly['Year'].min(), dtick=1, tickformat='d')
            st.plotly_chart(fig, use_container_width=True, key="trends_bills_by_year")
        else:
            st.info("No data for selected filters.")

    with col2:
        # Status distribution by year
        status_yearly = df.groupby(['Year', 'Status_Label']).size().reset_index(name='Count')
        if len(status_yearly) > 0:
            fig = px.bar(
                status_yearly,
                x='Year',
                y='Count',
                color='Status_Label',
                title='Status Distribution by Year',
                color_discrete_map=STATUS_COLORS,
                barmode='stack'
            )
            fig.update_xaxes(tickmode='linear', tick0=status_yearly['Year'].min(), dtick=1, tickformat='d')
            st.plotly_chart(fig, use_container_width=True, key="trends_status_by_year")
        else:
            st.info("No data for selected filters.")

    st.markdown("---")

    col3, col4 = st.columns(2)

    with col3:
        # Subject area trends
        subject_yearly = []
        for _, row in df.iterrows():
            subjects = str(row['Subject_Areas']).split(';')
            for s in subjects:
                s = s.strip()
                if s:  # Accept any non-empty subject
                    subject_yearly.append({'Year': row['Year'], 'Subject': s})

        if subject_yearly:
            subject_df = pd.DataFrame(subject_yearly)
            top_subjects = subject_df['Subject'].value_counts().head(8).index
            subject_df = subject_df[subject_df['Subject'].isin(top_subjects)]
            subject_counts = subject_df.groupby(['Year', 'Subject']).size().reset_index(name='Count')

            if len(subject_counts) > 0:
                fig = px.line(
                    subject_counts,
                    x='Year',
                    y='Count',
                    color='Subject',
                    title='Top Subject Areas Over Time',
                    markers=True,
                    color_discrete_map=SUBJECT_COLORS
                )
                fig.update_xaxes(tickmode='linear', tick0=subject_counts['Year'].min(), dtick=1, tickformat='d')
                st.plotly_chart(fig, use_container_width=True, key="trends_subject_over_time")
            else:
                st.info("No subject area data for selected filters.")
        else:
            st.info("No subject area data for selected filters.")

    with col4:
        # Risk trends by year
        risk_yearly = df[df['Status'] == 4].groupby('Year').agg({
            'EO_Risk_Count': 'sum'
        }).reset_index()
        risk_yearly.columns = ['Year', 'Total Risk Points']

        if len(risk_yearly) > 0:
            fig = px.line(
                risk_yearly,
                x='Year',
                y='Total Risk Points',
                title='Total Risk Points by Year (Passed Bills)',
                markers=True,
                color_discrete_sequence=['#e74c3c']
            )
            fig.update_xaxes(tickmode='linear', tick0=risk_yearly['Year'].min(), dtick=1, tickformat='d')
            st.plotly_chart(fig, use_container_width=True, key="trends_risk_by_year")
        else:
            st.info("No passed bills for selected filters.")

# ============================================================================
# TAB 4: STATE COMPARISON
# ============================================================================

def render_state_comparison_tab(df):
    """Render the State Comparison tab."""

    states = sorted(df['State_Name'].unique())
    selected_states = st.multiselect(
        "Select states to compare:",
        options=states,
        default=states[:5] if len(states) >= 5 else states,
        max_selections=10
    )

    if not selected_states:
        st.warning("Please select at least one state to compare.")
        return

    compare_df = df[df['State_Name'].isin(selected_states)]

    col1, col2 = st.columns(2)

    with col1:
        # Total bills comparison
        state_totals = compare_df.groupby('State_Name').size().reset_index(name='Total Bills')
        state_totals = state_totals.sort_values('Total Bills', ascending=True)

        fig = px.bar(
            state_totals,
            x='Total Bills',
            y='State_Name',
            orientation='h',
            title='Total Bills by State',
            color_discrete_sequence=['#3498db']
        )
        fig.update_layout(yaxis_title="")
        st.plotly_chart(fig, use_container_width=True, key="state_comp_bills")

    with col2:
        # Risk score comparison
        state_risk = compare_df[compare_df['Status'] == 4].groupby('State_Name').agg({
            'EO_Risk_Count': 'sum'
        }).reset_index()
        state_risk.columns = ['State_Name', 'Risk Score']
        state_risk = state_risk.sort_values('Risk Score', ascending=True)

        # Highlight Colorado
        colors = ['#e74c3c' if s == 'Colorado' else '#f39c12' for s in state_risk['State_Name']]

        fig = px.bar(
            state_risk,
            x='Risk Score',
            y='State_Name',
            orientation='h',
            title='EO Risk Score by State (Passed Bills)'
        )
        fig.update_traces(marker_color=colors)
        fig.update_layout(yaxis_title="")
        st.plotly_chart(fig, use_container_width=True, key="state_comp_risk")

    st.markdown("---")

    # Subject area breakdown by state
    st.subheader("Subject Area Focus by State")

    import re
    subject_state_data = []
    for state in selected_states:
        state_df = compare_df[compare_df['State_Name'] == state]
        for subj in SUBJECT_AREAS:
            escaped_subj = re.escape(subj)
            mask = state_df['Subject_Areas'].str.contains(escaped_subj, case=False, na=False, regex=True)
            count = mask.sum()
            if count > 0:
                subject_state_data.append({
                    'State': state,
                    'Subject Area': subj,
                    'Count': count
                })

    if subject_state_data:
        subject_state_df = pd.DataFrame(subject_state_data)

        fig = px.bar(
            subject_state_df,
            x='State',
            y='Count',
            color='Subject Area',
            title='Subject Area Distribution by State',
            color_discrete_map=SUBJECT_COLORS,
            barmode='stack'
        )
        st.plotly_chart(fig, use_container_width=True, key="state_comp_subj")

# ============================================================================
# TAB 5: FEDERAL PREEMPTION RISK
# ============================================================================

def render_eo_risk_tab(df):
    """Render the Federal Preemption Risk tab."""

    # Explanatory header
    st.info("""
    **About the December 2025 Executive Order**

    On December 11, 2025, the Trump administration signed Executive Order "Eliminating State Law Obstruction of National Artificial Intelligence Policy."
    This order represents a significant federal effort to limit state-level AI regulation. Key provisions include:

    - **AI Litigation Task Force**: A new body to challenge state laws in court
    - **Commerce Department Review**: Must identify "onerous" state AI laws within 90 days
    - **Federal Funding Leverage**: Threatens to withhold broadband funding from non-compliant states
    - **Colorado Named**: Explicitly cites Colorado's SB205 as an example of problematic legislation

    [Read the full Executive Order](https://www.whitehouse.gov/presidential-actions/2025/12/eliminating-state-law-obstruction-of-national-artificial-intelligence-policy/)
    """)

    # Detailed explanation expander
    with st.expander("How Risk Scores Are Calculated", expanded=False):
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("""
            **Targeted Provisions (Increase Risk)**

            The EO specifically criticizes state laws requiring:

            | Provision | Description | Risk Points |
            |----------|-------------|-------------|
            | **Nondiscrimination** | Laws requiring AI systems to not discriminate based on protected characteristics | +1 |
            | **General Notice** | Requirements to disclose when AI is being used in decision-making | +1 |
            | **Assessments** | Mandated impact assessments, audits, or documentation requirements | +1 |

            *A bill's risk count = number of targeted provisions it contains (0-3)*
            """)

        with col_b:
            st.markdown("""
            **Protected Subject Areas (Carve-Outs)**

            The EO explicitly protects certain types of state laws:

            | Protection | Description |
            |----------|-------------|
            | **Child Safety** | Laws protecting minors from AI-generated content, deepfakes, or online harms |
            | **Government Procurement** | Rules governing how state/local governments purchase AI systems |
            | **Infrastructure** | Data center regulations, broadband requirements, energy grid rules |

            *Bills in protected areas are less likely to face federal challenge*
            """)

        st.markdown("""
        ---
        **Risk Level Classification**

        | For Passed Bills | For Pending Bills | Criteria |
        |------------------|-------------------|----------|
        | **High Risk** | **Pending - High Exposure** | 2 or more targeted provisions |
        | **Moderate Risk** | **Pending - Some Exposure** | Exactly 1 targeted provision |
        | **Low Risk** | **Pending - Low Exposure** | No targeted provisions |
        """)

    st.markdown("---")

    # Risk by Subject Area (NEW FOCUS)
    st.subheader("Risk Analysis by Subject Area")

    st.markdown("""
    Which subject areas face the greatest federal preemption risk? The chart below shows how risk is distributed
    across different policy domains.
    """)

    subject_stats = get_subject_area_stats(df)

    # Check for empty data
    if len(subject_stats) == 0:
        st.info("No bills match the current filter criteria.")
        return

    col1, col2 = st.columns(2)

    with col1:
        # Subject areas ranked by risk
        subject_risk = subject_stats[['Subject Area', 'Total Risk Points', 'High Risk', 'Moderate Risk']].copy()
        subject_risk['At-Risk Bills'] = subject_risk['High Risk'] + subject_risk['Moderate Risk']
        subject_risk = subject_risk.sort_values('Total Risk Points', ascending=True)

        fig = go.Figure(go.Bar(
            x=subject_risk['Total Risk Points'],
            y=subject_risk['Subject Area'],
            orientation='h',
            marker_color=[SUBJECT_COLORS.get(s, '#95a5a6') for s in subject_risk['Subject Area']],
            text=subject_risk['Total Risk Points'],
            textposition='outside'
        ))
        fig.update_layout(
            title='Subject Areas by Total Risk Points',
            xaxis_title='Risk Points',
            yaxis_title='',
            height=450
        )
        st.plotly_chart(fig, use_container_width=True, key="eo_subj_risk_bar")

    with col2:
        # Risk concentration
        st.markdown("### Risk Concentration")

        # Calculate percentage of at-risk bills
        subject_risk_pct = subject_stats.copy()
        subject_risk_pct['At-Risk %'] = (
            (subject_risk_pct['High Risk'] + subject_risk_pct['Moderate Risk']) /
            subject_risk_pct['Passed Bills'].replace(0, 1) * 100
        ).round(1)
        subject_risk_pct = subject_risk_pct.sort_values('At-Risk %', ascending=False)

        st.markdown("**Percentage of passed bills at risk by subject:**")
        for _, row in subject_risk_pct.iterrows():
            if row['Passed Bills'] > 0:
                pct = row['At-Risk %']
                bar_color = '#e74c3c' if pct > 50 else '#f39c12' if pct > 25 else '#27ae60'
                st.markdown(f"**{row['Subject Area']}**: {pct:.0f}% ({row['High Risk'] + row['Moderate Risk']}/{row['Passed Bills']} bills)")

    st.markdown("---")

    # Key Insights
    st.subheader("Key Insights")

    col1, col2, col3 = st.columns(3)

    # Find highest risk subject
    highest_risk_subj = subject_stats.loc[subject_stats['Total Risk Points'].idxmax()]
    most_bills_subj = subject_stats.loc[subject_stats['Total Bills'].idxmax()]

    with col1:
        st.metric(
            "Highest Risk Subject Area",
            highest_risk_subj['Subject Area'],
            f"{int(highest_risk_subj['Total Risk Points'])} risk points"
        )

    with col2:
        st.metric(
            "Most Active Subject Area",
            most_bills_subj['Subject Area'],
            f"{int(most_bills_subj['Total Bills'])} total bills"
        )

    with col3:
        total_high_risk = subject_stats['High Risk'].sum()
        st.metric(
            "Total High-Risk Bills",
            int(total_high_risk),
            "across all subjects"
        )

    st.markdown("---")

    # State Risk Ranking
    st.subheader("State Risk Ranking")

    passed_df = df[df['Status'] == 4]

    col1, col2 = st.columns([2, 1])

    with col1:
        state_risk = passed_df.groupby(['State', 'State_Name']).agg({
            'State_Total_Risk_Points': 'first'
        }).reset_index()
        state_risk = state_risk.sort_values('State_Total_Risk_Points', ascending=True)
        state_risk = state_risk[state_risk['State_Total_Risk_Points'] > 0]

        if len(state_risk) > 0:
            colors = ['#e74c3c' if s == 'CO' else '#f39c12' for s in state_risk['State']]

            fig = go.Figure(go.Bar(
                x=state_risk['State_Total_Risk_Points'],
                y=state_risk['State_Name'],
                orientation='h',
                marker_color=colors,
                text=state_risk['State_Total_Risk_Points'],
                textposition='outside'
            ))

            if 'CO' in state_risk['State'].values:
                co_data = state_risk[state_risk['State'] == 'CO']
                fig.add_annotation(
                    x=co_data['State_Total_Risk_Points'].values[0],
                    y=co_data['State_Name'].values[0],
                    text=" Named in EO",
                    showarrow=True,
                    arrowhead=2,
                    ax=50,
                    ay=0
                )

            fig.update_layout(
                title='State Risk Points (Passed Bills Only)',
                xaxis_title='Total Risk Points',
                yaxis_title='',
                height=max(400, len(state_risk) * 25)
            )
            st.plotly_chart(fig, use_container_width=True, key="eo_state_risk_bar")

    with col2:
        risk_dist = passed_df['EO_Risk_Level'].value_counts().reset_index()
        risk_dist.columns = ['Risk Level', 'Count']

        fig = px.pie(
            risk_dist,
            values='Count',
            names='Risk Level',
            color='Risk Level',
            color_discrete_map=RISK_COLORS,
            hole=0.4,
            title='Overall Risk Distribution'
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True, key="eo_risk_pie")

    st.markdown("---")

    # High-Risk Bills Table
    st.subheader("High-Risk Bills by Subject Area")

    # Add subject area filter for the table
    table_subject = st.selectbox(
        "Filter by subject area:",
        options=['All'] + SUBJECT_AREAS
    )

    high_risk_bills = df[df['EO_Risk_Level'] == 'High Risk'].copy()

    if table_subject != 'All':
        high_risk_bills = high_risk_bills[
            high_risk_bills['Subject_Areas'].str.contains(table_subject, case=False, na=False)
        ]

    if len(high_risk_bills) > 0:
        st.dataframe(
            high_risk_bills[['State', 'Bill Number', 'Title', 'Subject_Areas', 'Status_Label', 'View']],
            column_config={
                "View": st.column_config.LinkColumn("View Bill", display_text="View"),
                "Subject_Areas": st.column_config.TextColumn("Subject Areas")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("No high-risk bills match the selected filter.")

    st.markdown("---")

    # Colorado Spotlight
    st.subheader("Colorado Spotlight")

    with st.expander("Colorado is explicitly named in the Executive Order", expanded=False):
        co_bills = df[df['State'] == 'CO']
        co_passed = co_bills[co_bills['Status'] == 4]

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Colorado Bills", len(co_bills))
        with col2:
            st.metric("Passed Bills", len(co_passed))
        with col3:
            co_risk = co_passed['EO_Risk_Count'].sum()
            st.metric("Total Risk Points", co_risk)

        # Subject breakdown for Colorado
        st.markdown("### Colorado Bills by Subject Area")
        import re
        co_subjects = []
        for subj in SUBJECT_AREAS:
            escaped_subj = re.escape(subj)
            mask = co_passed['Subject_Areas'].str.contains(escaped_subj, case=False, na=False, regex=True)
            count = mask.sum()
            risk = co_passed[mask]['EO_Risk_Count'].sum()
            if count > 0:
                co_subjects.append({'Subject': subj, 'Bills': count, 'Risk Points': risk})

        if co_subjects:
            co_subj_df = pd.DataFrame(co_subjects)
            st.dataframe(co_subj_df, hide_index=True, use_container_width=True)

    st.markdown("---")

    # Timeline
    st.subheader("Executive Order Timeline")

    # Create a cleaner timeline display
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 15px; background-color: #fadbd8; border-radius: 10px; border-left: 5px solid #e74c3c;">
            <h4 style="color: #e74c3c; margin: 0;">Dec 11, 2025</h4>
            <p style="margin: 5px 0 0 0; font-weight: bold;">EO Signed</p>
            <p style="margin: 0; font-size: 0.85em; color: #666;">Executive Order issued</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 15px; background-color: #fdebd0; border-radius: 10px; border-left: 5px solid #f39c12;">
            <h4 style="color: #f39c12; margin: 0;">Jan 10, 2026</h4>
            <p style="margin: 5px 0 0 0; font-weight: bold;">Task Force Deadline</p>
            <p style="margin: 0; font-size: 0.85em; color: #666;">30 days to establish</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 15px; background-color: #d4efdf; border-radius: 10px; border-left: 5px solid #27ae60;">
            <h4 style="color: #27ae60; margin: 0;">Mar 11, 2026</h4>
            <p style="margin: 5px 0 0 0; font-weight: bold;">Commerce Review</p>
            <p style="margin: 0; font-size: 0.85em; color: #666;">90 days to identify laws</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================================
# TAB 6: POLICY CATEGORIES (Secondary)
# ============================================================================

def render_categories_tab(df):
    """Render the Policy Categories tab (secondary view)."""

    st.markdown("""
    **Policy categories** describe the *regulatory mechanism* each bill uses, while **subject areas** describe
    the *policy domain* it addresses. A Healthcare bill (subject) might use Nondiscrimination requirements (category).

    This tab provides a secondary view focused on the regulatory approaches states are using.
    """)

    col_legend1, col_legend2, col_legend3 = st.columns(3)
    with col_legend1:
        st.markdown("🔴 **Targeted by EO** - Regulatory approaches the Executive Order criticizes")
    with col_legend2:
        st.markdown("🔵 **Protected** - Approaches with explicit carve-outs")
    with col_legend3:
        st.markdown("⚪ **Neutral** - Other regulatory approaches")

    st.markdown("---")

    # Parse all categories
    all_categories = []
    for cats in df['Categories'].dropna():
        if cats:
            for c in str(cats).split(','):
                c = c.strip()
                if c:
                    all_categories.append(c)

    if not all_categories:
        st.warning("No category data available.")
        return

    cat_counts = pd.Series(all_categories).value_counts().reset_index()
    cat_counts.columns = ['Category', 'Count']

    targeted_categories = ['Nondiscrimination', 'General notice', 'Assessments']
    protected_categories = ['child', 'government', 'procurement', 'infrastructure', 'data center']

    def get_category_type(cat):
        cat_lower = cat.lower()
        if cat in targeted_categories:
            return 'Targeted by EO'
        for p in protected_categories:
            if p in cat_lower:
                return 'Protected'
        return 'Neutral'

    cat_counts['Type'] = cat_counts['Category'].apply(get_category_type)

    col1, col2 = st.columns(2)

    with col1:
        cat_counts_top = cat_counts.head(20).sort_values('Count', ascending=True)

        color_map = {
            'Targeted by EO': TARGETED_COLOR,
            'Protected': PROTECTED_COLOR,
            'Neutral': '#95a5a6'
        }

        fig = px.bar(
            cat_counts_top,
            x='Count',
            y='Category',
            orientation='h',
            title='Policy Category Frequency',
            color='Type',
            color_discrete_map=color_map
        )
        fig.update_layout(yaxis_title="", height=600)
        st.plotly_chart(fig, use_container_width=True, key="cat_freq_bar")

    with col2:
        type_counts = cat_counts.groupby('Type')['Count'].sum().reset_index()

        fig = px.pie(
            type_counts,
            values='Count',
            names='Type',
            title='Category Classification',
            color='Type',
            color_discrete_map=color_map
        )
        st.plotly_chart(fig, use_container_width=True, key="cat_type_pie")

        st.markdown("""
        **Targeted categories** are the regulatory mechanisms the EO specifically criticizes.
        Bills using these approaches face higher preemption risk regardless of their subject area.
        """)

# ============================================================================
# TAB 7: BILL EXPLORER
# ============================================================================

def render_bill_explorer_tab(df):
    """Render the Bill Explorer tab with full search and export."""

    st.subheader("Bill Explorer")

    # Initialize session state for explorer filters
    if 'explorer_search' not in st.session_state:
        st.session_state.explorer_search = ""
    if 'explorer_subject' not in st.session_state:
        st.session_state.explorer_subject = 'All'
    if 'explorer_risk' not in st.session_state:
        st.session_state.explorer_risk = 'All'

    # Filters row with session state keys
    col1, col2, col3 = st.columns(3)

    with col1:
        search = st.text_input(
            "Search titles:",
            value=st.session_state.explorer_search,
            placeholder="Enter keywords...",
            key="explorer_search_input"
        )
        st.session_state.explorer_search = search

    with col2:
        subject_options = ['All'] + SUBJECT_AREAS
        explorer_subject = st.selectbox(
            "Subject area:",
            options=subject_options,
            index=subject_options.index(st.session_state.explorer_subject) if st.session_state.explorer_subject in subject_options else 0,
            key="explorer_subject_select"
        )
        st.session_state.explorer_subject = explorer_subject

    with col3:
        risk_options = ['All', 'High Risk', 'Moderate Risk', 'Low Risk',
                     'Pending - High Exposure', 'Pending - Some Exposure', 'Pending - Low Exposure']
        explorer_risk = st.selectbox(
            "Risk level:",
            options=risk_options,
            index=risk_options.index(st.session_state.explorer_risk) if st.session_state.explorer_risk in risk_options else 0,
            key="explorer_risk_select"
        )
        st.session_state.explorer_risk = explorer_risk

    display_df = df.copy()

    if search:
        display_df = display_df[
            display_df['Title'].str.contains(search, case=False, na=False)
        ]

    if explorer_subject != 'All':
        display_df = display_df[
            display_df['Subject_Areas'].str.contains(explorer_subject, case=False, na=False)
        ]

    if explorer_risk != 'All':
        display_df = display_df[display_df['EO_Risk_Level'] == explorer_risk]

    st.write(f"Showing {len(display_df)} bills")

    display_cols = ['State', 'Bill Number', 'Title', 'Subject_Areas', 'Status_Label', 'Year',
                    'EO_Risk_Level', 'View']

    st.dataframe(
        display_df[display_cols],
        column_config={
            "View": st.column_config.LinkColumn("View Bill", display_text="View"),
            "EO_Risk_Level": st.column_config.TextColumn("Risk Level"),
            "Status_Label": st.column_config.TextColumn("Status"),
            "Subject_Areas": st.column_config.TextColumn("Subject Areas")
        },
        hide_index=True,
        use_container_width=True,
        height=600
    )

    st.markdown("---")

    col1, col2 = st.columns([1, 4])
    with col1:
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="Export to CSV",
            data=csv,
            file_name="filtered_ai_legislation.csv",
            mime="text/csv"
        )

    with col2:
        st.caption("Download the currently filtered dataset as CSV")

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point."""

    # Header
    st.title("State AI Legislation Dashboard with Federal Preemption Analysis")
    st.markdown("*Exploring U.S. State-Level AI Legislation and Executive Order Risk*")

    # Load data
    df = load_data()

    # Apply sidebar filters
    filtered_df = apply_filters(df)

    # Show filter summary
    if len(filtered_df) < len(df):
        st.caption(f"Showing {len(filtered_df)} of {len(df)} bills based on filters")

    # Create tabs (reordered with Subject Areas prominent)
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Overview",
        "Subject Areas",
        "Federal Preemption Risk",
        "Trends",
        "State Comparison",
        "Bill Explorer",
        "Policy Categories"
    ])

    with tab1:
        render_overview_tab(filtered_df, df)

    with tab2:
        render_subject_areas_tab(filtered_df)

    with tab3:
        render_eo_risk_tab(filtered_df)

    with tab4:
        render_trends_tab(filtered_df)

    with tab5:
        render_state_comparison_tab(filtered_df)

    with tab6:
        render_bill_explorer_tab(filtered_df)

    with tab7:
        render_categories_tab(filtered_df)

    # Footer
    st.markdown("---")
    st.caption("Data source: LegiScan | Analysis includes December 2025 Executive Order risk assessment")
    st.warning("""
    **Prototype Disclaimer:** This dashboard is a research prototype and may contain errors, omissions, or inaccuracies
    in bill classifications, risk assessments, or subject area categorizations. Data should be independently verified
    before use in policy analysis or decision-making. Last updated: December 2025.
    """)

if __name__ == "__main__":
    main()
