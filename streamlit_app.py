import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import re

# ==========================================
# 1. ARCHITECTURAL ENGINE: DATA REGISTRY & DQM
# ==========================================
class DataRegistry:
    """Manages the dimensional framework, constraints registry, and validation engines."""
    
    # Target schema list of all expected domain columns
    COLUMNS = [
        'warehouse_block', 'Avg. Session Length', 'Time on App', 
        'Time on Website', 'Length of Membership', 'Yearly Amount Spent', 'Email'
    ]
    
    @staticmethod
    def get_dimension_matrix() -> pd.DataFrame:
        """Returns the structural measurement metadata registry."""
        return pd.DataFrame({
            "Attribute Name": DataRegistry.COLUMNS,
            "Physical Dimension": [
                "Spatial / Geographic Categorization", "Temporal (Duration)", 
                "Temporal (Duration)", "Temporal (Duration)", "Temporal (Duration)", 
                "Monetary (Currency Value)", "Unique Identifier (Alphanumeric Address)"
            ],
            "Unit of Measure (UOM)": [
                "Discrete Factor (Alpha Code)", "Minutes (min)", "Hours (hrs)", 
                "Hours (hrs)", "Years (yrs)", "United States Dollar ($ USD)", "String Token"
            ],
            "Completeness Target": ["100% Non-Null"] * len(DataRegistry.COLUMNS)
        })

    @staticmethod
    def run_dqm_assessment(data: pd.DataFrame) -> dict:
        """Executes targeted profiling checks for completeness and value ranges."""
        constraints = {
            'warehouse_block': {'allowed': ['A', 'B', 'C', 'D', 'E', 'F']},
            'Avg. Session Length': {'min': 20.0, 'max': 50.0},
            'Time on App': {'min': 0.0, 'max': 24.0},
            'Time on Website': {'min': 0.0, 'max': 60.0},
            'Length of Membership': {'min': 0.0, 'max': 15.0},
            'Yearly Amount Spent': {'min': 0.0, 'max': 2000.0}
        }
        email_regex = r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
        
        results = {}
        for col in DataRegistry.COLUMNS:
            if col not in data.columns:
                continue
                
            # 1. Evaluate Data Completeness
            null_count = int(data[col].isna().sum())
            
            # 2. Evaluate Range & Format Violations
            violation_count = 0
            valid_rows = data[data[col].notna()]
            
            if col == 'warehouse_block':
                violation_count = int((~valid_rows[col].isin(constraints[col]['allowed'])).sum())
            elif col == 'Email':
                violation_count = int((~valid_rows[col].astype(str).str.match(email_regex, na=False)).sum())
            elif col in constraints:
                limits = constraints[col]
                violation_count = int(((valid_rows[col] < limits['min']) | (valid_rows[col] > limits['max'])).sum())
                
            if null_count > 0 or violation_count > 0:
                results[col] = {"missing": null_count, "violations": violation_count}
                
        return results


# ==========================================
# 2. PRESENTATION LAYER: STREAMLIT UI CONTROLLER
# ==========================================
class DataQualityDashboard:
    """Handles the UI parsing, rendering hooks, and visualization generation."""
    
    def __init__(self):
        st.set_page_config(page_title="Ecommerce Analytics & Integrity", layout="wide")
        st.title("Ecommerce Customer Insights & Quality Management")
        st.markdown("Interactive visualization architecture backed by programmatic class constraints.")

    @st.cache_data
    def load_dataset(_self) -> pd.DataFrame:
        """Retrieves external or fallback diagnostic mock data frames."""
        try:
            df = pd.read_csv("Ecommerce Customers.csv")
            if 'warehouse_block' not in df.columns:
                df['warehouse_block'] = np.random.choice(['A', 'B', 'C', 'D', 'E'], size=len(df))
            return df
        except FileNotFoundError:
            st.sidebar.warning("⚠️ CSV Resource dropped. Injecting programmatic fallback sample data.")
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

    def render_metadata_blocks(self):
        """Builds out presentation layouts for the dimensional registry mappings."""
        st.markdown("---")
        with st.expander("📊 Measurement Registry & Dimensional Completeness Specs", expanded=True):
            st.dataframe(
                DataRegistry.get_dimension_matrix(),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Attribute Name": st.column_config.TextColumn("Registered Attribute", width="medium"),
                    "Physical Dimension": st.column_config.TextColumn("Dimension Matrix Zone"),
                    "Unit of Measure (UOM)": st.column_config.TextColumn("UOM Specification Standard"),
                    "Completeness Target": st.column_config.TextColumn("Completeness Rule SLA")
                }
            )

    def render_dqm_summary(self, data: pd.DataFrame):
        """Evaluates pipeline data health and populates metrics widgets."""
        st.markdown("### 🛠️ Real-time Data Quality Management (DQM) Validation")
        
        dqm_log = DataRegistry.run_dqm_assessment(data)
        total_missing = sum(item['missing'] for item in dqm_log.values())
        total_violations = sum(item['violations'] for item in dqm_log.values())
        total_anomalies = total_missing + total_violations
        
        # Display operational status indicators
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Dataset Length Profile", f"{len(data)} rows")
        col2.metric("Pipeline Quality Status", f"{'✅ Clean' if total_anomalies == 0 else '❌ Action Required'}")
        col3.metric("Completeness Dropouts", f"{total_missing} null fields")
        col4.metric("Constraint Violations", f"{total_violations} instances")

        if total_anomalies > 0:
            with st.expander("🚨 Detailed Schema Anomaly Log", expanded=True):
                log_df = pd.DataFrame([
                    {
                        "Attribute Field": col,
                        "Missing Values": metrics['missing'],
                        "Out-Of-Bounds Violations": metrics['violations'],
                        "DQM Risk Factor": f"{((metrics['missing'] + metrics['violations']) / len(data)) * 100:.1f}%"
                    }
                    for col, metrics in dqm_log.items()
                ])
                st.table(log_df)
        else:
            st.success("🎉 **Registry Policy Alignment Checked:** Complete data coverage confirmed across all dimensions.")

    def render_analytics(self, data: pd.DataFrame):
        """Builds multi-layered analytical chart engines via interactive Altair blocks."""
        st.markdown("---")
        features = ["Avg. Session Length", "Time on App", "Time on Website", "Length of Membership"]
        selected_feature = st.sidebar.selectbox("Analytical Cross-Pivot Target Variable:", features)
        
        st.subheader(f"Correlation Profiling: {selected_feature} vs. Spending Matrix")
        
        base = alt.Chart(data).encode(
            x=alt.X(f'{selected_feature}:Q', scale=alt.Scale(zero=False)),
            y=alt.Y('Yearly Amount Spent:Q', title='Yearly Expenditure ($ USD)')
        )
        
        points = base.mark_circle(size=60, opacity=0.5, color="#1f77b4").encode(
            tooltip=['Email', 'Length of Membership', 'Yearly Amount Spent']
        )
        trend = base.transform_regression(selected_feature, 'Yearly Amount Spent').mark_line(color='red', size=3)
        
        st.altair_chart((points + trend).properties(height=400).interactive(), use_container_width=True)

        # Spend distribution profile component
        st.subheader("Distribution Volume: Yearly Expenditure Profile")
        hist = alt.Chart(data).mark_bar().encode(
            x=alt.X("Yearly Amount Spent:Q", bin=alt.Bin(maxbins=30), title="Annual Settlement Range ($)"),
            y=alt.Y('count()', title="Aggregate Client Target Count"),
            color=alt.value("#4c78a8")
        ).properties(height=250)
        
        st.altair_chart(hist, use_container_width=True)


# ==========================================
# 3. RUNTIME INITIALIZATION BLOCK
# ==========================================
if __name__ == "__main__":
    # Instantiate layout controllers
    dashboard = DataQualityDashboard()
    
    # Process transactional calculations
    working_df = dashboard.load_dataset()
    
    # Append user visual interfaces
    dashboard.render_metadata_blocks()
    dashboard.render_dqm_summary(working_df)
    dashboard.render_analytics(working_df)
    
    with st.expander("🔍 System Explorer: Inspect Working Cache"):
        st.dataframe(working_df, use_container_width=True)
