import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

# 1. Platform Initial Config
st.set_page_config(
    page_title="Enterprise Ecomm: Insights Framework", 
    page_icon="📈",
    layout="wide"
)

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Ecommerce Customers.csv")
        if 'warehouse_block' not in df.columns:
            df['warehouse_block'] = np.random.choice(['A', 'B', 'C', 'D', 'E'], size=len(df))
        return df
    except FileNotFoundError:
        st.sidebar.warning("⚠️ Baseline 'Ecommerce Customers.csv' not found. Deploying simulated runtime environment.")
        np.random.seed(42)
        return pd.DataFrame({
            'warehouse_block': np.random.choice(['A', 'B', 'C', 'D', 'E', 'F'], 400),
            'Avg. Session Length': np.random.normal(32, 1.5, 400),
            'Time on App': np.random.normal(12, 1, 400),
            'Time on Website': np.random.normal(37, 1.5, 400),
            'Length of Membership': np.random.normal(3.5, 1.2, 400),
            'Yearly Amount Spent': np.random.normal(500, 75, 400),
            'Email': [f"user_{i}@example.com" for i in range(400)]
        })

# Initialize Core Dataset
df_raw = load_data()

# --- SIDEBAR INTERFACE: SYSTEM CONTROLS ---
with st.sidebar:
    st.markdown("## 🛡️ Control Console")
    st.markdown("Configure operational filters and evaluation bounds below.")
    st.markdown("---")
    
    # Section A: Segment Subsetting
    st.markdown("### 🧩 Regional Segmentation")
    available_blocks = sorted(df_raw['warehouse_block'].unique())
    selected_blocks = st.multiselect(
        "Fulfillment Zones", 
        options=available_blocks, 
        default=available_blocks,
        help="Filter the entire platform scope based on regional warehouse blocks."
    )
    
    # Section B: Range Truncation
    st.markdown("### 💸 Revenue Guardrails")
    min_spend = float(df_raw['Yearly Amount Spent'].min())
    max_spend = float(df_raw['Yearly Amount Spent'].max())
    selected_spend_range = st.slider(
        "Annual Spending Limits ($)",
        min_value=min_spend,
        max_value=max_spend,
        value=(min_spend, max_spend),
        format="$%.2f"
    )
    
    st.markdown("---")
    st.markdown("💡 *Graphs, raw query tables, and business KPIs dynamically adjust based on your chosen criteria above.*")

# Execute Global Frame Mutations Based on Filter Criteria
df_filtered = df_raw[
    (df_raw['warehouse_block'].isin(selected_blocks)) & 
    (df_raw['Yearly Amount Spent'].between(selected_spend_range[0], selected_spend_range[1]))
]

# --- MAIN DASHBOARD INTERFACE ---
st.title("📈 eCommerce Customer Intelligence Platform")
st.markdown("A unified control panel tracking data integrity metrics alongside active user behaviors.")
st.markdown("---")

# --- IMPROVED EXECUTIVE KPI SCORE CARDS WITH BORDERS ---
kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4)

with kpi_1:
    with st.container(border=True):
        st.metric(
            label="👥 Cohort Footprint", 
            value=f"{len(df_filtered):,}", 
            delta=f"{len(df_filtered) - len(df_raw)} items filtered" if len(df_filtered) != len(df_raw) else None
        )
with kpi_2:
    with st.container(border=True):
        st.metric(
            label="💰 Mean Annual Value", 
            value=f"${df_filtered['Yearly Amount Spent'].mean():,.2f}" if not df_filtered.empty else "$0.00"
        )
with kpi_3:
    with st.container(border=True):
        st.metric(
            label="⏳ Avg Membership Term", 
            value=f"{df_filtered['Length of Membership'].mean():.2f} Yrs" if not df_filtered.empty else "0.0 Yrs"
        )
with kpi_4:
    with st.container(border=True):
        st.metric(
            label="📱 Active Mobile Usage", 
            value=f"{df_filtered['Time on App'].mean():.1f} min" if not df_filtered.empty else "0.0 min"
        )

st.markdown("---")

# Section 2: Tabbed Architecture
tab_visuals, tab_governance = st.tabs(["📊 Behavior Analysis Suite", "📐 Schema Governance & Records"])

with tab_visuals:
    if df_filtered.empty:
        st.error("❌ **Operational Exception:** No active customer accounts match the selected parameters. Adjust your sidebar filters to process data.")
    else:
        # Dynamic Feature Selector Row
        select_col1, select_col2 = st.columns([2, 2])
        with select_col1:
            features = ["Avg. Session Length", "Time on App", "Time on Website", "Length of Membership"]
            selected_feature = st.selectbox("🔬 Primary Behavioral Analysis Axis:", features)
            
        # Graphical Workstation Layout
        chart_col, hist_col = st.columns([5, 4])
        
        with chart_col:
            st.markdown(f"#### Linear Dependency: `{selected_feature}` vs Expenditure")
            
            # Base Coordinate Bindings
            scatter_base = alt.Chart(df_filtered).encode(
                x=alt.X(f'{selected_feature}:Q', title=f"{selected_feature} (Units)", scale=alt.Scale(zero=False)),
                y=alt.Y('Yearly Amount Spent:Q', title='Annual Invoice Statement ($)', scale=alt.Scale(zero=False))
            )
            
            # Scatter Plot Element
            points = scatter_base.mark_circle(size=75, opacity=0.6, color="#2b5c8f").encode(
                color=alt.Color('warehouse_block:N', title="Hub", scale=alt.Scale(scheme='tableau10')),
                tooltip=['Email', 'Length of Membership', 'Yearly Amount Spent', 'warehouse_block']
            )
            
            # Regression Fit Line
            trend_line = scatter_base.transform_regression(
                selected_feature, 'Yearly Amount Spent'
            ).mark_line(color='#c0392b', size=3.5, strokeDash=[5, 5])
            
            render_scatter = (points + trend_line).properties(height=420).interactive()
            st.altair_chart(render_scatter, use_container_width=True)
            
        with hist_col:
            st.markdown("#### Distribution Densities: Customer Gross Invoice Assets")
            
            # Formatted Density Histogram Bar Model
            hist_viz = alt.Chart(df_filtered).mark_bar(
                color="#2c3e50", 
                cornerRadiusTopLeft=5, 
                cornerRadiusTopRight=5
            ).encode(
                x=alt.X("Yearly Amount Spent:Q", bin=alt.Bin(maxbins=20), title="Binned Annual Outlay ($)"),
                y=alt.Y('count()', title='Frequency Distribution Volume')
            ).properties(height=420)
            
            st.altair_chart(hist_viz, use_container_width=True)

with tab_governance:
    st.markdown("### Structural Governance Protocols & Schema Catalog")
    st.markdown("This matrix catalogs system type requirements, database invariants, and formatting constraints.")
    
    # Validation Rules Specification Catalog
    rules_catalog = {
        "Attribute Key ID": ["warehouse_block", "Avg. Session Length", "Time on App", "Time on Website", "Length of Membership", "Yearly Amount Spent", "Email"],
        "Expected Datatype": ["Categorical String", "Continuous Float", "Continuous Float", "Continuous Float", "Continuous Float", "Financial Currency Float", "Alphanumeric String"],
        "Operational Boundary Metrics": ["Uppercase Flags [A-F]", "Range [20.0 - 50.0]", "Range [0.0 - 24.0]", "Range [0.0 - 60.0]", "Range [0.0 - 15.0]", "Range [$0.00 - $2,000.00]", "Regex Structure Match"],
        "Business Architecture Rule Context": [
            "Assigned physical regional warehousing hub structure. Must match validation codes.",
            "Average system duration engagement length checked in precise calculated minutes.",
            "Active interaction runtime metrics captured on local mobile application services.",
            "Monitored desktop deployment interface processing session logging windows.",
            "Total cumulative chronological years an active customer account has maintained active premium standard.",
            "Sum total currency value checked against verified electronic merchant accounts over 12 billing cycles.",
            "Primary communication channel parameter. Case checked for format compliance."
        ]
    }
    
    st.dataframe(
        pd.DataFrame(rules_catalog),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Attribute Key ID": st.column_config.TextColumn("Attribute ID", width="medium"),
            "Expected Datatype": st.column_config.TextColumn("System Datatype Type"),
            "Operational Boundary Metrics": st.column_config.TextColumn("Schema Guardrails / Invariant Ranges"),
            "Business Architecture Rule Context": st.column_config.TextColumn("Governance Objective Manual Reference", width="large")
        }
    )
    
    st.markdown("---")
    st.markdown("### Operational Snapshot Data Inspection Matrix")
    st.markdown("Explore live records matching current sidebar filter criteria.")
    st.dataframe(df_filtered, use_container_width=True)
