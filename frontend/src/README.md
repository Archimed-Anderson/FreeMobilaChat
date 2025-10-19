# 📊 Universal Automated Data Analysis System

**Production-ready module for automatic data analysis and visualization in Streamlit**

Version: 1.0.0  
Created for: FreeMobilaChat Platform  
Author: FreeMobilaChat Development Team

---

## 🎯 Overview

This is a **complete, modular, production-ready system** that automatically analyzes any data file (CSV, Excel, JSON) and generates an intelligent, interactive dashboard—without requiring any knowledge of column names or data structure.

### Key Features

✅ **Universal File Support** - CSV, Excel, JSON  
✅ **Automatic Type Detection** - Numeric, categorical, temporal, text, boolean, identifier  
✅ **Smart Visualizations** - Plotly charts selected based on data types  
✅ **Insight Generation** - Automatic discovery of patterns, anomalies, correlations  
✅ **Data Quality Assessment** - Comprehensive quality scoring (0-100)  
✅ **Zero Configuration** - Works out-of-the-box with any tabular data  
✅ **Streamlit Integration** - Seamless integration with existing apps  
✅ **Production Ready** - Type hints, documentation, error handling, caching  

---

## 🏗️ Architecture

```
src/
├── analyzers/              # Data analysis and classification
│   ├── main.py            # Main entry point: analyze_document()
│   ├── data_classifier.py # Automatic column type classification
│   ├── metric_selector.py # Metric and visualization selection
│   └── insight_generator.py # Insight generation engine
│
├── visualizers/           # Dashboard and chart generation
│   ├── dashboard_builder.py # Complete dashboard builder
│   └── chart_factory.py  # Plotly chart factory
│
├── utils/                 # Core utilities
│   ├── file_handler.py    # Universal file reading
│   └── data_processor.py  # Data processing and statistics
│
└── tests/                 # Unit tests
    └── test_data_processor.py
```

---

## 🚀 Quick Start

### 1. Basic Usage

```python
import streamlit as st
from src.analyzers.main import analyze_document
from src.visualizers.dashboard_builder import DashboardBuilder

# Upload file
uploaded_file = st.file_uploader("Upload data", type=['csv', 'xlsx', 'json'])

if uploaded_file:
    # Analyze (automatic, cached)
    results = analyze_document(uploaded_file)
    
    if results:
        # Generate dashboard
        dashboard = DashboardBuilder(results)
        dashboard.generate()  # Full interactive dashboard
```

### 2. Run Standalone Demo

```bash
streamlit run automated_analysis_demo.py
```

### 3. Install Dependencies

```bash
pip install plotly ydata-profiling scipy openpyxl
```

---

## 📋 Core Components

### 1. File Handler (`utils/file_handler.py`)

**Purpose:** Universal file reading with encoding detection

**Features:**
- Reads CSV, Excel, JSON automatically
- Multiple encoding attempts (UTF-8, Latin-1, etc.)
- File validation and metadata extraction
- Error handling with user-friendly messages

**Usage:**
```python
from src.utils.file_handler import FileHandler

df = FileHandler.read_file(uploaded_file)
validation = FileHandler.validate_dataframe(df)
file_info = FileHandler.get_file_info(uploaded_file)
```

### 2. Data Processor (`utils/data_processor.py`)

**Purpose:** Data classification, statistics, quality assessment

**Features:**
- Automatic column type inference (6 types)
- Statistical profiling (mean, median, outliers, etc.)
- Correlation detection
- Data quality scoring

**Usage:**
```python
from src.utils.data_processor import DataProcessor

# Infer types
column_types = DataProcessor.infer_column_types(df)
# {'sales': 'numeric', 'category': 'categorical', 'date': 'temporal'}

# Get statistics
stats = DataProcessor.get_column_stats(df, column_types)

# Detect correlations
correlations = DataProcessor.detect_correlations(df)

# Calculate quality
quality_score = DataProcessor.calculate_data_quality_score(df, stats)
```

### 3. Data Classifier (`analyzers/data_classifier.py`)

**Purpose:** Comprehensive data classification and profiling

**Features:**
- Orchestrates type inference and statistics
- Generates dataset summary
- Groups columns by type

**Usage:**
```python
from src.analyzers.data_classifier import DataClassifier

classifier = DataClassifier(df)
results = classifier.classify()
# Returns: column_types, column_stats, correlations, quality_score, dataset_summary
```

### 4. Metric Selector (`analyzers/metric_selector.py`)

**Purpose:** Selects appropriate metrics and visualizations

**Features:**
- Recommends univariate, bivariate, multivariate analyses
- Prioritizes visualizations by importance
- Suggests statistical tests

**Usage:**
```python
from src.analyzers.metric_selector import MetricSelector

selector = MetricSelector(column_types, column_stats)
metrics = selector.select_metrics()
priority_viz = selector.get_priority_visualizations(max_charts=10)
```

### 5. Insight Generator (`analyzers/insight_generator.py`)

**Purpose:** Generates human-readable insights

**Features:**
- Dataset overview insights
- Data quality warnings
- Statistical observations (outliers, skewness)
- Correlation highlights
- Anomaly detection

**Usage:**
```python
from src.analyzers.insight_generator import InsightGenerator

generator = InsightGenerator(df, classification_results)
insights = generator.generate_insights()
summary = generator.get_summary()

# Display
for insight in insights:
    st.info(insight)
```

### 6. Chart Factory (`visualizers/chart_factory.py`)

**Purpose:** Creates Plotly visualizations

**Supported Charts:**
- Histogram (numeric distributions)
- Box plot (outlier detection)
- Bar chart (categorical frequencies)
- Pie chart (proportions)
- Scatter plot (bivariate relationships)
- Correlation heatmap (multivariate)
- Line chart (temporal trends)

**Usage:**
```python
from src.visualizers.chart_factory import ChartFactory

factory = ChartFactory(df, column_types)

# Create specific chart
chart_spec = {
    'type': 'histogram',
    'columns': ['sales'],
    'title': 'Sales Distribution'
}
fig = factory.create_chart(chart_spec)
st.plotly_chart(fig)
```

### 7. Dashboard Builder (`visualizers/dashboard_builder.py`)

**Purpose:** Complete dashboard generation

**Sections:**
- Executive summary with KPIs
- Key insights panel
- Interactive visualizations (8-10 charts)
- Data quality assessment
- Raw data explorer with filters

**Usage:**
```python
from src.visualizers.dashboard_builder import DashboardBuilder

dashboard = DashboardBuilder(analysis_results)

# Full dashboard
dashboard.generate()

# OR compact version (faster)
dashboard.render_compact()
```

### 8. Main Analyzer (`analyzers/main.py`)

**Purpose:** Orchestrates the entire analysis pipeline

**Workflow:**
1. Read file → 2. Classify data → 3. Select metrics → 4. Generate insights → 5. Return results

**Usage:**
```python
from src.analyzers.main import analyze_document

results = analyze_document(uploaded_file)
# Automatically cached with Streamlit
```

**Results Structure:**
```python
{
    'file_info': {
        'name': str,
        'size_mb': float,
        'extension': str
    },
    'dataframe': pd.DataFrame,
    'classification': {
        'column_types': dict,
        'column_stats': dict,
        'correlations': list,
        'quality_score': float,
        'dataset_summary': dict
    },
    'metric_recommendations': dict,
    'priority_visualizations': list,
    'insights': list,
    'summary': str
}
```

---

## 🎨 Customization Guide

### Change Colors

Edit `src/visualizers/chart_factory.py`:

```python
COLOR_SCHEME = {
    'primary': '#YOUR_COLOR',
    'secondary': '#YOUR_COLOR',
    # ...
}
```

### Add Custom Insight Rules

Edit `src/analyzers/insight_generator.py`:

```python
def _custom_insights(self) -> List[str]:
    insights = []
    # Add your custom logic
    if custom_condition:
        insights.append("Your custom insight")
    return insights
```

### Create New Chart Types

Edit `src/visualizers/chart_factory.py`:

```python
def create_chart(self, chart_spec):
    if chart_type == 'my_chart':
        return self._create_my_chart(...)
    # ...
    
def _create_my_chart(self, ...):
    # Implement your chart
    return fig
```

### Modify Quality Scoring

Edit `src/utils/data_processor.py`:

```python
def calculate_data_quality_score(df, stats):
    # Adjust weights
    quality_score = (
        completeness_score * 0.5 +  # Change from 0.4
        uniqueness_score * 0.3 +
        consistency_score * 0.2
    )
    return quality_score
```

---

## 🧪 Testing

### Run Tests

```bash
cd frontend
pytest src/tests/ -v
```

### Test Coverage

```bash
pytest src/tests/ --cov=src --cov-report=html
```

### Example Test

```python
def test_numeric_detection():
    df = pd.DataFrame({'numbers': [1, 2, 3, 4, 5]})
    types = DataProcessor.infer_column_types(df)
    assert types['numbers'] == 'numeric'
```

---

## 📊 Column Type Detection

| Type | Detection Criteria | Examples |
|------|-------------------|----------|
| **numeric** | Continuous numbers, >20 unique values | sales, price, quantity |
| **categorical** | Strings/numbers, ≤50 unique values | color, size, category |
| **temporal** | Dates, datetimes | order_date, timestamp |
| **text** | Long strings (>100 chars avg) | description, comments |
| **boolean** | True/False, 0/1, Yes/No | is_active, completed |
| **identifier** | High uniqueness (>95%) | customer_id, SKU |

---

## 🔍 Generated Insights Examples

```
📊 Aperçu des données: 1,234 lignes et 15 colonnes (2.5 MB)
🔢 Variables numériques: 8 colonnes disponibles pour l'analyse quantitative
⚠️ Bonne qualité des données (82/100) - quelques améliorations possibles
📈 sales: Distribution positivement asymétrique (moyenne=1250.50, médiane=980.00)
⚠️ price: 45 valeurs aberrantes détectées (3.6%)
🔗 Forte corrélation positive: quantity et revenue sont fortement corrélés (r=0.92)
```

---

## ⚡ Performance Optimization

### 1. Caching

```python
@st.cache_data  # Already applied to analyze_document()
def analyze_document(uploaded_file):
    # Analysis cached automatically
    pass
```

### 2. Large Files

```python
# Sample before analysis
if len(df) > 100000:
    df = df.sample(n=50000, random_state=42)
```

### 3. Limit Visualizations

```python
priority_viz = selector.get_priority_visualizations(max_charts=5)
```

### 4. Use Compact Dashboard

```python
dashboard.render_compact()  # Faster than generate()
```

---

## 🐛 Troubleshooting

**Import Errors:**
```python
import sys, os
sys.path.append(os.path.dirname(__file__))
```

**Memory Issues:**
```python
df = df.sample(frac=0.1)  # Use 10% sample
```

**Slow Performance:**
- Use caching
- Limit rows/charts
- Use `render_compact()`

**Charts Not Showing:**
- Check Plotly installed
- Verify numeric columns exist
- Remove null values

---

## 📚 API Reference

### Main Functions

```python
analyze_document(uploaded_file) -> Dict
DashboardBuilder(results).generate() -> None
DashboardBuilder(results).render_compact() -> None
ChartFactory(df, types).create_chart(spec) -> Figure
DataProcessor.infer_column_types(df) -> Dict
DataProcessor.get_column_stats(df, types) -> Dict
DataProcessor.detect_correlations(df) -> List
InsightGenerator(df, results).generate_insights() -> List
```

---

## 🎓 Best Practices

1. **Always cache**: Use `@st.cache_data` for expensive operations
2. **Handle errors**: Wrap in try-except blocks
3. **Validate input**: Check file format and size
4. **Limit display**: Don't show >1000 rows
5. **Sample large data**: Use sampling for >100K rows
6. **Clear cache**: `analyze_document.clear()` when needed
7. **Log errors**: Use `logging` for debugging
8. **Type hints**: Maintain type annotations
9. **Document code**: Add docstrings to functions
10. **Test thoroughly**: Write unit tests for new features

---

## 📦 Dependencies

**Core:**
- streamlit >= 1.28.0
- pandas >= 2.1.0
- numpy >= 1.25.0
- plotly >= 5.17.0

**Optional:**
- ydata-profiling >= 4.5.0
- scipy >= 1.11.0
- openpyxl >= 3.1.0

---

## 🚀 Deployment

### Local Development

```bash
streamlit run automated_analysis_demo.py
```

### Production (Streamlit Cloud)

1. Push to GitHub
2. Connect to Streamlit Cloud
3. Add dependencies to `requirements.txt`
4. Deploy

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "automated_analysis_demo.py"]
```

---

## 📝 License

Created for FreeMobilaChat Platform  
© 2025 FreeMobilaChat Development Team

---

## 🤝 Contributing

To contribute:
1. Fork repository
2. Create feature branch
3. Add tests
4. Submit pull request

---

## 📞 Support

For questions or issues:
1. Check integration guide: `AUTOMATED_ANALYSIS_INTEGRATION_GUIDE.md`
2. Review examples: `automated_analysis_demo.py`
3. Run tests: `pytest src/tests/ -v`
4. Check logs for errors

---

**🎉 Ready to use! Start with `automated_analysis_demo.py` or integrate into your app following the integration guide.**
