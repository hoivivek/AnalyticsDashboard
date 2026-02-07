import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import requests

# Page config (must be first)
st.set_page_config(
    page_title="Analytics Dashboard",
    page_icon=":material/dashboard:",
    layout="wide"
)

# Initialize session state
st.session_state.setdefault("df", None)
st.session_state.setdefault("data_source", None)
st.session_state.setdefault("uploaded_filename", None)


@st.cache_data(show_spinner=False)
def load_csv(file) -> pd.DataFrame:
    """Load CSV file with caching."""
    return pd.read_csv(file)


@st.cache_data(show_spinner=False)
def load_snowflake_data(query: str) -> pd.DataFrame:
    """Load data from Snowflake with caching."""
    try:
        from snowflake.snowpark import Session
        session = Session.builder.configs(
            st.secrets["connections"]["snowflake"]
        ).create()
        df = session.sql(query).to_pandas()
        return df
    except Exception as e:
        st.error(f"Snowflake connection error: {e}")
        return None


@st.cache_data(show_spinner=False, ttl=3600)
def fetch_api_data(endpoint: str) -> pd.DataFrame:
    """Fetch data from API with caching (1 hour TTL)."""
    try:
        response = requests.get(endpoint, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Handle different response formats
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            # Try common data keys
            for key in ['data', 'results', 'items', 'records']:
                if key in data:
                    return pd.DataFrame(data[key])
            return pd.DataFrame([data])
        return pd.DataFrame()
    except requests.exceptions.Timeout:
        st.error("API request timed out. Please try again.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"API error: {e}")
        return None


def validate_dataframe(df: pd.DataFrame) -> bool:
    """Validate that DataFrame is suitable for visualization."""
    if df is None or df.empty:
        st.error(":material/error: No data loaded", icon=":material/error:")
        return False
    
    if len(df) < 1:
        st.error(":material/error: Dataset is empty", icon=":material/error:")
        return False
    
    return True


def get_numeric_columns(df: pd.DataFrame) -> list:
    """Get list of numeric columns from DataFrame."""
    return df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()


def get_categorical_columns(df: pd.DataFrame) -> list:
    """Get list of categorical columns from DataFrame."""
    return df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()


# Sidebar - Data Source Selection
with st.sidebar:
    st.header(":material/database: Data Source")
    
    data_source_type = st.radio(
        "Select data source:",
        ["CSV Upload", "Snowflake", "API"],
        key="data_source_type"
    )
    
    st.divider()
    
    # CSV Upload
    if data_source_type == "CSV Upload":
        uploaded_file = st.file_uploader(
            "Upload CSV file",
            type=["csv"],
            help="Upload a CSV file for visualization"
        )
        
        if uploaded_file is not None:
            with st.spinner("Loading data..."):
                df = load_csv(uploaded_file)
                if df is not None:
                    st.session_state.df = df
                    st.session_state.data_source = "CSV"
                    st.session_state.uploaded_filename = uploaded_file.name
                    st.success(f":material/check_circle: Loaded {len(df)} rows")
    
    # Snowflake
    elif data_source_type == "Snowflake":
        st.info("Configure Snowflake credentials in `.streamlit/secrets.toml`")
        
        query = st.text_area(
            "SQL Query",
            value="SELECT * FROM MY_TABLE LIMIT 1000",
            height=100,
            help="Enter your SQL query"
        )
        
        if st.button(":material/play_arrow: Execute Query", use_container_width=True):
            with st.spinner("Executing query..."):
                df = load_snowflake_data(query)
                if df is not None:
                    st.session_state.df = df
                    st.session_state.data_source = "Snowflake"
                    st.success(f":material/check_circle: Loaded {len(df)} rows")
    
    # API
    elif data_source_type == "API":
        st.info("Provide a REST API endpoint that returns JSON")
        
        api_endpoint = st.text_input(
            "API Endpoint",
            value="https://api.example.com/data",
            help="Enter the full URL of the API endpoint"
        )
        
        if st.button(":material/refresh: Fetch Data", use_container_width=True):
            with st.spinner("Fetching data..."):
                df = fetch_api_data(api_endpoint)
                if df is not None:
                    st.session_state.df = df
                    st.session_state.data_source = "API"
                    st.success(f":material/check_circle: Loaded {len(df)} rows")
    
    st.divider()
    
    # Data info
    if st.session_state.df is not None:
        st.subheader(":material/info: Dataset Info")
        st.metric("Rows", len(st.session_state.df))
        st.metric("Columns", len(st.session_state.df.columns))
        
        if st.session_state.uploaded_filename:
            st.caption(f"File: {st.session_state.uploaded_filename}")


# Main content
st.title(":material/dashboard: Analytics Dashboard")

df = st.session_state.df

if df is None:
    st.info(":material/arrow_back: Please select a data source from the sidebar to get started")
    
    # Example data formats
    with st.expander("Example Data Formats"):
        st.subheader("CSV Example")
        st.code("""date,category,value,count
2024-01-01,A,100,5
2024-01-02,B,150,8
2024-01-03,A,120,6""")
        
        st.subheader("API Response Example")
        st.code("""{
  "data": [
    {"date": "2024-01-01", "category": "A", "value": 100},
    {"date": "2024-01-02", "category": "B", "value": 150}
  ]
}""")
    
    st.stop()

# Validate data
if not validate_dataframe(df):
    st.stop()

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs([
    ":material/table_chart: Data",
    ":material/bar_chart: Charts",
    ":material/analytics: Statistics",
    ":material/download: Export"
])

with tab1:
    st.subheader(":material/table_chart: Data Preview")
    
    # Column configuration for better display
    st.dataframe(
        df,
        height=400,
        use_container_width=True
    )
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Rows", len(df))
    with col2:
        st.metric("Total Columns", len(df.columns))
    with col3:
        numeric_cols = get_numeric_columns(df)
        st.metric("Numeric Columns", len(numeric_cols))
    with col4:
        categorical_cols = get_categorical_columns(df)
        st.metric("Categorical Columns", len(categorical_cols))

with tab2:
    st.subheader(":material/bar_chart: Visualizations")
    
    numeric_cols = get_numeric_columns(df)
    categorical_cols = get_categorical_columns(df)
    all_cols = df.columns.tolist()
    
    if len(numeric_cols) == 0:
        st.warning("No numeric columns found for visualization")
        st.stop()
    
    # Chart type selection
    col1, col2 = st.columns([1, 3])
    
    with col1:
        chart_type = st.selectbox(
            "Chart Type",
            ["Bar Chart", "Line Chart", "Scatter Plot", "Box Plot", "Histogram"]
        )
    
    with col2:
        # Dynamic options based on chart type
        if chart_type in ["Bar Chart", "Line Chart"]:
            col_x = st.selectbox("X-axis", all_cols, key="x_axis")
            col_y = st.selectbox("Y-axis", numeric_cols, key="y_axis")
            col_color = st.selectbox("Color by (optional)", [None] + categorical_cols, key="color_by")
            
        elif chart_type == "Scatter Plot":
            col_x = st.selectbox("X-axis", numeric_cols, key="scatter_x")
            col_y = st.selectbox("Y-axis", numeric_cols, key="scatter_y")
            col_color = st.selectbox("Color by (optional)", [None] + categorical_cols, key="scatter_color")
            
        elif chart_type == "Box Plot":
            col_y = st.selectbox("Values", numeric_cols, key="box_y")
            col_x = st.selectbox("Group by (optional)", [None] + categorical_cols, key="box_x")
            col_color = None
            
        elif chart_type == "Histogram":
            col_x = st.selectbox("Column", numeric_cols, key="hist_x")
            col_color = st.selectbox("Color by (optional)", [None] + categorical_cols, key="hist_color")
    
    # Generate chart
    try:
        if chart_type == "Bar Chart":
            fig = px.bar(df, x=col_x, y=col_y, color=col_color)
            
        elif chart_type == "Line Chart":
            fig = px.line(df, x=col_x, y=col_y, color=col_color, markers=True)
            
        elif chart_type == "Scatter Plot":
            fig = px.scatter(df, x=col_x, y=col_y, color=col_color)
            
        elif chart_type == "Box Plot":
            fig = px.box(df, x=col_x, y=col_y)
            
        elif chart_type == "Histogram":
            fig = px.histogram(df, x=col_x, color=col_color)
        
        # Update layout
        fig.update_layout(
            margin=dict(t=40, l=0, r=0, b=0),
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error generating chart: {e}")

with tab3:
    st.subheader(":material/analytics: Statistical Summary")
    
    numeric_cols = get_numeric_columns(df)
    
    if len(numeric_cols) > 0:
        # Summary statistics
        st.write("**Descriptive Statistics**")
        st.dataframe(df[numeric_cols].describe(), use_container_width=True)
        
        st.divider()
        
        # Correlation matrix
        if len(numeric_cols) > 1:
            st.write("**Correlation Matrix**")
            corr_matrix = df[numeric_cols].corr()
            
            fig = px.imshow(
                corr_matrix,
                text_auto=True,
                aspect="auto",
                color_continuous_scale="RdBu_r",
                zmin=-1,
                zmax=1
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No numeric columns available for statistical analysis")
    
    # Missing values
    st.divider()
    st.write("**Missing Values**")
    missing = df.isnull().sum()
    missing_df = pd.DataFrame({
        'Column': missing.index,
        'Missing Count': missing.values,
        'Percentage': (missing.values / len(df) * 100).round(2)
    })
    missing_df = missing_df[missing_df['Missing Count'] > 0]
    
    if len(missing_df) > 0:
        st.dataframe(missing_df, use_container_width=True)
    else:
        st.success(":material/check_circle: No missing values found!")

with tab4:
    st.subheader(":material/download: Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV export
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv = df.to_csv(index=False)
        
        st.download_button(
            label=":material/download: Download as CSV",
            data=csv,
            file_name=f"dashboard_export_{timestamp}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # Excel export
        import io
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Data', index=False)
            if len(get_numeric_columns(df)) > 0:
                df[get_numeric_columns(df)].describe().to_excel(writer, sheet_name='Statistics')
        
        st.download_button(
            label=":material/download: Download as Excel",
            data=output.getvalue(),
            file_name=f"dashboard_export_{timestamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    st.divider()
    
    # Export options
    with st.expander("Export Options"):
        st.write("**Filter data before export:**")
        
        if len(get_categorical_columns(df)) > 0:
            filter_col = st.selectbox("Filter by column", get_categorical_columns(df))
            unique_values = df[filter_col].unique().tolist()
            selected_values = st.multiselect(f"Select {filter_col} values", unique_values)
            
            if selected_values:
                filtered_df = df[df[filter_col].isin(selected_values)]
                st.metric("Filtered Rows", len(filtered_df))
                
                csv_filtered = filtered_df.to_csv(index=False)
                st.download_button(
                    label=":material/download: Download Filtered CSV",
                    data=csv_filtered,
                    file_name=f"dashboard_filtered_{timestamp}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

# Footer
st.divider()
st.caption(f"Dashboard powered by Streamlit | Data source: {st.session_state.data_source}")
