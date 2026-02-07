# Analytics Dashboard

**Interactive Streamlit dashboard that visualizes data from CSV uploads, Snowflake databases, or REST APIs.**

## Features

- **Multiple Data Sources**: Load data from CSV files, Snowflake queries, or REST APIs
- **Interactive Visualizations**: Create bar charts, line charts, scatter plots, box plots, and histograms
- **Statistical Analysis**: View descriptive statistics, correlation matrices, and missing value reports
- **Data Export**: Download data as CSV or Excel with optional filtering
- **Real-time Updates**: Cached data loading for optimal performance

## Run Locally

```bash
# Clone the repo
git clone [repo-url]
cd [app-folder]

# Install dependencies
pip install -r requirements.txt

# Add secrets (if using Snowflake)
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml with your Snowflake credentials

# Run
streamlit run app.py
```

## Deploy to Streamlit Community Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Add secrets in the dashboard (Settings → Secrets) if using Snowflake
5. Deploy!

## Usage Guide

### CSV Upload
1. Select "CSV Upload" from the sidebar
2. Upload your CSV file
3. View and visualize your data in the tabs

### Snowflake Connection
1. Configure your Snowflake credentials in `.streamlit/secrets.toml`
2. Select "Snowflake" from the sidebar
3. Enter your SQL query
4. Click "Execute Query"

### API Data
1. Select "API" from the sidebar
2. Enter your REST API endpoint (must return JSON)
3. Click "Fetch Data"

### Supported API Formats
The dashboard handles various JSON response formats:
- Array of objects: `[{...}, {...}]`
- Object with data key: `{"data": [{...}]}`
- Object with results key: `{"results": [{...}]}`

## Example Data

### CSV Format
```csv
date,category,value,count
2024-01-01,A,100,5
2024-01-02,B,150,8
2024-01-03,A,120,6
```

### API Response Format
```json
{
  "data": [
    {"date": "2024-01-01", "category": "A", "value": 100},
    {"date": "2024-01-02", "category": "B", "value": 150}
  ]
}
```

## Configuration

### Snowflake Setup
Create `.streamlit/secrets.toml`:
```toml
[connections.snowflake]
account = "your_account"
user = "your_user"
password = "your_password"
role = "your_role"
warehouse = "COMPUTE_WH"
database = "MY_DB"
schema = "MY_SCHEMA"
```

## Features in Detail

### Data Tab
- Full data preview with scrollable table
- Quick statistics (row count, column count, data types)

### Charts Tab
- 5 chart types: Bar, Line, Scatter, Box Plot, Histogram
- Dynamic axis and color selection
- Interactive Plotly charts with zoom and pan

### Statistics Tab
- Descriptive statistics for numeric columns
- Correlation matrix heatmap
- Missing value analysis

### Export Tab
- Download as CSV or Excel
- Optional data filtering before export
- Timestamps in filenames for versioning

---

Built with [Streamlit](https://streamlit.io)
