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

# Initialize Baseline Dataset
df_raw = load_data()

# Dictionary to preserve configuration parameters for references
var_metadata = {
    "Avg. Session Length": "Average duration of live storefront platform sessions calibrated in minutes.",
    "Time on App": "Calculated continuous minutes tracked across mobile client device deployments.",
    "Time on Website": "Chronological tracking of standard desktop browser login sessions.",
    "Length of Membership": "Total calculated tenure years the client has maintained active premium status.",
    "Yearly Amount Spent": "Sum total merchant transactional values over a rolling 12-month window."
}

# --- INITIAL FILTER STATE COLLECTION ---
# We collect slider boundaries from the sidebar first to create the subset frame
numeric_filters = {}
selected_blocks = []

# --- SIDEBAR INTERFACE: DYNAMIC ATTRIBUTE FILTERS, INFO & LOCAL KPIS ---
with st.sidebar:
    st.markdown("## 🛡️ Variable Governance Console")
    st.markdown("Inspect metadata constraints, subset KPIs, and configure filters per column.")
    st.markdown("---")
    
    # 1. Categorical Dimension: Warehouse Block
    st.markdown("### 🧩 Categorical Fields")
    with st.expander("warehouse_block Configuration", expanded=True):
        st.caption("Physical regional hub cluster identifiers [A-F].")
        available_blocks = sorted(df_raw['warehouse_block'].unique())
        selected_blocks = st.multiselect(
            "Filter Fulfillment Zones", 
            options=available_blocks, 
            default=available_blocks
        )
    
    st.markdown("---")
    st.markdown("### 🔢 Numerical Feature Guardrails")
    
    # Render interactive controls and collect positions
    for col_name, info_text in var_metadata.items():
        with st.expander(f"⚙️ {col_name}", expanded=False):
            st.markdown(f"**Data Info:** *{info_text}*")
            
            min_val = float(df_raw[col_name].min())
            max_val = float(df_raw[col_name].max())
            
            numeric_filters[col_name] = st.slider(
                "Filter Value Boundaries",
                min_value=min_val,
                max_value=max_val,
                value=(min_val, max_val),
                key=f"slider_{col_name}",
                format="%.1f"
            )

# Execute Global Multi-Variable Mutation to obtain active subset
df_filtered = df_raw.copy()
df_filtered = df_filtered[df_filtered['warehouse_block'].isin(selected_blocks)]
for col_name, bounds in numeric_filters.items():
    df_filtered = df_filtered[df_filtered[col_name].between(bounds[0], bounds[1])]

has_data = not df_filtered.empty

# --- SIDEBAR LOCAL KPI INJECTION LOOP ---
# Re-entering the sidebar context to inject the dynamic subset metrics under the sliders
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📊 Local Variable Sub-Metrics")
    st.caption("Real-time summary indicators for current filtered variables:")
    
    for col_name in var_metadata.keys():
        if has_data:
            sub_mean = df_filtered[col_name].mean()
            sub_delta = sub_mean - df_raw[col_name].mean()
            
            # Formatting decisions depending on currency formatting needs
            if "Spent" in col_name:
                st.metric(label=f"Filtered Mean {col_name}", value=f"${sub_mean:,.2f}", delta=f"${sub_delta:+.2f} vs global pool")
            else:
                st.metric(label=f"Filtered Mean {col_name}", value=f"{sub_mean:.2f}", delta=f"{sub_delta:+.2f} vs global pool")
        else:
            st.metric(label=f"Filtered Mean {col_name}", value="N/A")


# --- MAIN DASHBOARD INTERFACE ---
st.title("📈 eCommerce Customer Intelligence Platform")
st.markdown("A unified control panel tracking data integrity metrics alongside active user behaviors.")
st.markdown("---")

# --- EXPANDED METRIC SCORE CARDS FOR EACH VARIABLE ---
st.markdown("### 📋 Cohort Performance Cards")
kpi_row1 = st.columns(3)
kpi_row2 = st.columns(3)

# Row 1: Primary Target KPIs
with kpi_row1[0]:
    with st.container(border=True):
        st.metric(
            label="👥 Filtered Cohort Size", 
            value=f"{len(df_filtered):,}", 
            delta=f"{len(df_filtered) - len(df_raw)} records vs total" if len(df_filtered) != len(df_raw) else None
        )
with kpi_row1[1]:
    with st.container(border=True):
        current_spend = df_filtered['Yearly Amount Spent'].mean() if has_data else 0
        base_spend = df_raw['Yearly Amount Spent'].mean()
        st.metric(
            label="💰 Avg. Yearly Amount Spent", 
            value=f"${current_spend:,.2f}",
            delta=f"${current_spend - base_spend:+.2f} vs baseline" if len(df_filtered) != len(df_raw) else None
        )
with kpi_row1[2]:
    with st.container(border=True):
        current_member = df_filtered['Length of Membership'].mean() if has_data else 0
        base_member = df_raw['Length of Membership'].mean()
        st.metric(
            label="⏳ Avg. Length of Membership", 
            value=f"{current_member:.2f} Yrs",
            delta=f"{current_member - base_member:+.2f} Yrs vs baseline" if len(df_filtered) != len(df_raw) else None
        )

# Row 2: Behavioral Usage KPIs
with kpi_row2[0]:
    with st.container(border=True):
        current_sess = df_filtered['Avg. Session Length'].mean() if has_data else 0
        base_sess = df_raw['Avg. Session Length'].mean()
        st.metric(
            label="💻 Avg. Session Length", 
            value=f"{current_sess:.1f} min",
            delta=f"{current_sess - base_sess:+.1f} min vs baseline" if len(df_filtered) != len(df_raw) else None
        )
with kpi_row2[1]:
    with st.container(border=True):
        current_app = df_filtered['Time on App'].mean() if has_data else 0
        base_app = df_raw['Time on App'].mean()
        st.metric(
            label="📱 Avg. Time on App", 
            value=f"{current_app:.1f} min",
            delta=f"{current_app - base_app:+.1f} min vs baseline" if len(df_filtered) != len(df_raw) else None
        )
with kpi_row2[2]:
    with st.container(border=True):
        current_web = df_filtered['Time on Website'].mean() if has_data else 0
        base_web = df_raw['Time on Website'].mean()
        st.metric(
            label="🌐 Avg. Time on Website", 
            value=f"{current_web:.1f} min",
            delta=f"{current_web - base_web:+.1f} min vs baseline" if len(df_filtered) != len(df_raw) else None
        )

st.markdown("---")

# Section 2: Tabbed Visualization Architecture 
tab_visuals, tab_governance = st.tabs(["📊 Behavior Analysis Suite", "📐 Schema Governance & Records"])

with tab_visuals:
    if df_filtered.empty:
        st.error("❌ **Operational Exception:** No active customer accounts match the selected parameter bounds. Adjust your variable filters to render data views.")
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
            points = scatter_base.mark_circle(size=75, opacity=0.6).encode(
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
