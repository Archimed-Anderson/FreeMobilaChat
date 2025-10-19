# Automated Data Analysis System - Integration Guide

## 📋 Overview

This guide explains how to integrate the **Universal Automated Analysis System** into your existing FreeMobilaChat Streamlit application.

---

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── __init__.py
│   ├── analyzers/
│   │   ├── __init__.py
│   │   ├── main.py                  # Main analysis entry point
│   │   ├── data_classifier.py       # Automatic data classification
│   │   ├── metric_selector.py       # Metric and viz selection
│   │   └── insight_generator.py     # Insight generation
│   ├── visualizers/
│   │   ├── __init__.py
│   │   ├── dashboard_builder.py     # Dashboard generation
│   │   └── chart_factory.py         # Plotly chart creation
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── file_handler.py          # Universal file reading
│   │   └── data_processor.py        # Data processing utilities
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_data_processor.py   # Unit tests
│   └── requirements_analysis.txt    # Additional dependencies
├── automated_analysis_demo.py       # Standalone demo app
└── streamlit_app.py                 # Your main app (integration here)
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd C:\Users\ander\Desktop\FreeMobilaChat\frontend
pip install plotly ydata-profiling scipy openpyxl
```

### 2. Run Standalone Demo

```bash
streamlit run automated_analysis_demo.py
```

This demonstrates the full system working independently.

---

## 🔧 Integration into FreeMobilaChat

### Option 1: Add as New Page

Create a new page file:

**`frontend/pages/4_📊_Data_Analysis.py`**

```python
import streamlit as st
import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analyzers.main import analyze_document
from src.visualizers.dashboard_builder import DashboardBuilder

st.set_page_config(page_title="Data Analysis", page_icon="📊", layout="wide")

st.title("📊 Analyse Automatique de Données")

# File upload
uploaded_file = st.file_uploader(
    "Upload Data File",
    type=['csv', 'xlsx', 'json'],
    help="Select a data file to analyze"
)

if uploaded_file and st.button("🚀 Analyze"):
    results = analyze_document(uploaded_file)
    if results:
        st.session_state.analysis_results = results
        
if 'analysis_results' in st.session_state:
    dashboard = DashboardBuilder(st.session_state.analysis_results)
    dashboard.generate()
```

### Option 2: Integrate into Existing Upload Flow

Modify **`frontend/streamlit_app.py`** to add analysis to CSV uploads:

```python
# Add imports at top
from src.analyzers.main import analyze_document
from src.visualizers.dashboard_builder import DashboardBuilder

# In your file upload section:
uploaded_file = st.file_uploader(...)

if uploaded_file:
    # Existing tweet validation
    validation = validate_tweet_file(df)
    
    # NEW: Add automated analysis option
    if st.checkbox("📊 Analyze with Auto-Analyzer"):
        with st.expander("Automated Analysis", expanded=True):
            results = analyze_document(uploaded_file)
            if results:
                dashboard = DashboardBuilder(results)
                dashboard.render_compact()  # Compact version
```

### Option 3: Add to Analysis Page

Modify **`frontend/pages/2_Analysis.py`**:

```python
# After existing analysis sections, add:
st.markdown("---")
st.markdown("### 🤖 Automated Data Analysis")

if st.button("Run Automated Analysis"):
    # Convert current tweet data to analysis
    results = analyze_document(uploaded_tweet_file)
    if results:
        dashboard = DashboardBuilder(results)
        dashboard.generate()
```

---

## 💡 Usage Examples

### Basic Usage

```python
from src.analyzers.main import analyze_document
from src.visualizers.dashboard_builder import DashboardBuilder

# Analyze file
results = analyze_document(uploaded_file)

# Create dashboard
dashboard = DashboardBuilder(results)
dashboard.generate()  # Full dashboard
# OR
dashboard.render_compact()  # Compact version
```

### Access Specific Results

```python
results = analyze_document(uploaded_file)

# Access different components
dataframe = results['dataframe']
quality_score = results['classification']['quality_score']
insights = results['insights']
column_types = results['classification']['column_types']
visualizations = results['priority_visualizations']

# Display specific insights
for insight in insights[:5]:
    st.info(insight)
```

### Create Custom Visualizations

```python
from src.visualizers.chart_factory import ChartFactory

# Initialize
chart_factory = ChartFactory(df, column_types)

# Create specific chart
chart_spec = {
    'type': 'histogram',
    'columns': ['numeric_column'],
    'title': 'Distribution Analysis'
}

fig = chart_factory.create_chart(chart_spec)
st.plotly_chart(fig, use_container_width=True)
```

---

## 🎨 Customization

### Modify Color Scheme

Edit **`src/visualizers/chart_factory.py`**:

```python
COLOR_SCHEME = {
    'primary': '#DC143C',      # Your brand color
    'secondary': '#FF6B6B',
    'accent': '#B91C3C',
    # ... add more colors
}
```

### Adjust Insight Generation

Edit **`src/analyzers/insight_generator.py`**:

```python
def _statistical_insights(self) -> List[str]:
    """Customize insight logic here"""
    insights = []
    
    # Add custom insight rules
    for col in numeric_cols:
        if custom_condition:
            insights.append(f"Custom insight: {col}")
    
    return insights
```

### Add Custom Chart Types

Edit **`src/visualizers/chart_factory.py`**:

```python
def create_chart(self, chart_spec: Dict[str, Any]) -> Optional[go.Figure]:
    chart_type = chart_spec['type']
    
    if chart_type == 'my_custom_chart':
        return self._create_my_custom_chart(...)
    # ... existing code
```

---

## 🧪 Testing

### Run Unit Tests

```bash
cd frontend
pytest src/tests/ -v
```

### Test with Sample Data

```python
import pandas as pd
from src.analyzers.main import analyze_document
from io import BytesIO

# Create test data
df = pd.DataFrame({
    'sales': [100, 200, 150, 300, 250],
    'category': ['A', 'B', 'A', 'C', 'B'],
    'date': pd.date_range('2024-01-01', periods=5)
})

# Save to BytesIO (simulates uploaded file)
buffer = BytesIO()
df.to_csv(buffer, index=False)
buffer.seek(0)

# Create mock uploaded file
class MockFile:
    def __init__(self, name, content):
        self.name = name
        self.size = len(content.getvalue())
        self.type = 'text/csv'
        self._content = content
    
    def read(self):
        return self._content.getvalue()
    
    def seek(self, pos):
        self._content.seek(pos)

mock_file = MockFile('test.csv', buffer)

# Analyze
results = analyze_document(mock_file)
print(f"Quality Score: {results['classification']['quality_score']}")
```

---

## 📊 Features Reference

### Supported File Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| CSV | .csv, .txt | Auto-encoding detection |
| Excel | .xlsx, .xls | Multiple sheets supported |
| JSON | .json | Array or object format |

### Detected Column Types

| Type | Description | Example |
|------|-------------|---------|
| `numeric` | Continuous numbers | Sales, prices, metrics |
| `categorical` | Discrete categories | Product types, regions |
| `temporal` | Dates/times | Order dates, timestamps |
| `text` | Free-form text | Comments, descriptions |
| `boolean` | Binary values | Yes/No, True/False |
| `identifier` | Unique IDs | Customer IDs, SKUs |

### Generated Insights

- Dataset overview (rows, columns, memory)
- Data quality assessment
- Statistical anomalies (outliers, skewness)
- Correlation discoveries
- Missing value warnings
- Duplicate detection
- Column-specific observations

### Available Visualizations

| Chart Type | Use Case |
|------------|----------|
| Histogram | Numeric distributions |
| Box Plot | Outlier detection |
| Bar Chart | Categorical frequencies |
| Pie Chart | Category proportions |
| Scatter Plot | Bivariate relationships |
| Correlation Heatmap | Multivariate analysis |
| Line Chart | Temporal trends |

---

## 🔒 Best Practices

### 1. Caching

The main `analyze_document()` function uses `@st.cache_data` for performance.

**Clear cache if needed:**
```python
analyze_document.clear()
```

### 2. Large Files

For files > 100 MB:
- Limit rows displayed
- Use sampling for analysis
- Enable pagination

```python
if len(df) > 100000:
    st.warning("Large dataset detected. Analyzing first 50,000 rows.")
    df = df.head(50000)
```

### 3. Error Handling

Always wrap in try-except:

```python
try:
    results = analyze_document(uploaded_file)
    if results:
        dashboard = DashboardBuilder(results)
        dashboard.generate()
    else:
        st.error("Analysis failed")
except Exception as e:
    st.error(f"Error: {str(e)}")
    logger.error(f"Analysis error", exc_info=True)
```

### 4. Performance Optimization

- Use `render_compact()` for faster loading
- Limit visualizations to top 5-8
- Sample large datasets
- Enable lazy loading

---

## 🐛 Troubleshooting

### Issue: Import Errors

**Solution:**
```bash
# Ensure src is in Python path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
```

### Issue: Memory Issues with Large Files

**Solution:**
```python
# Sample before analysis
if df.shape[0] > 10000:
    df = df.sample(n=10000, random_state=42)
```

### Issue: Slow Performance

**Solutions:**
1. Use caching (`@st.cache_data`)
2. Limit visualizations
3. Use `render_compact()` instead of `generate()`
4. Disable expensive analysis steps

### Issue: Charts Not Displaying

**Check:**
1. Plotly installed: `pip install plotly`
2. Data types correct
3. No null values in numeric columns
4. Sufficient data points (>2)

---

## 📚 API Reference

### Main Functions

#### `analyze_document(uploaded_file)`

**Parameters:**
- `uploaded_file`: Streamlit UploadedFile object

**Returns:**
```python
{
    'file_info': dict,
    'file_validation': dict,
    'dataframe': pd.DataFrame,
    'classification': dict,
    'metric_recommendations': dict,
    'priority_visualizations': list,
    'insights': list,
    'summary': str
}
```

#### `DashboardBuilder.generate()`

Renders full dashboard with:
- Executive summary
- Key insights
- All visualizations
- Data quality section
- Data explorer

#### `DashboardBuilder.render_compact()`

Renders compact version with:
- Quick metrics
- Top 3 insights
- 1 key visualization

---

## 🎯 Next Steps

1. **Install dependencies**: `pip install -r src/requirements_analysis.txt`
2. **Test standalone app**: `streamlit run automated_analysis_demo.py`
3. **Integrate into your app**: Choose one of the integration options
4. **Customize**: Modify colors, insights, charts as needed
5. **Deploy**: Test with real data from FreeMobilaChat

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Review unit tests for examples
3. Examine `automated_analysis_demo.py` for working implementation
4. Check logs for detailed error messages

---

**Created for FreeMobilaChat** - Universal Automated Data Analysis System v1.0.0
