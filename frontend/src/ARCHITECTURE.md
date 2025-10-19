# System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         STREAMLIT APPLICATION                            │
│                      (FreeMobilaChat Frontend)                           │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
         ┌───────────────────────────────────────────────────┐
         │         📂 File Upload Component                   │
         │    (CSV / Excel / JSON)                           │
         └───────────────────────┬───────────────────────────┘
                                 │
                                 ▼
         ┌───────────────────────────────────────────────────┐
         │      📊 analyze_document()                        │
         │      (src/analyzers/main.py)                      │
         │                                                    │
         │  Entry Point - Orchestrates Analysis Pipeline     │
         └───────────────────────┬───────────────────────────┘
                                 │
         ┌───────────────────────┴─────────────────────────────┐
         │                                                      │
         ▼                                                      ▼
┌────────────────────┐                           ┌────────────────────────┐
│  📖 File Handler   │                           │  🔍 Data Classifier    │
│  (utils/)          │                           │  (analyzers/)          │
│                    │                           │                        │
│ • Read CSV         │                           │ • Infer column types   │
│ • Read Excel       │────────Provides──────────▶│ • Calculate statistics │
│ • Read JSON        │       DataFrame           │ • Detect correlations  │
│ • Validate data    │                           │ • Quality scoring      │
└────────────────────┘                           └──────────┬─────────────┘
                                                            │
                    ┌───────────────────────────────────────┤
                    │                                       │
                    ▼                                       ▼
    ┌───────────────────────────┐          ┌──────────────────────────────┐
    │  📈 Metric Selector       │          │  💡 Insight Generator        │
    │  (analyzers/)             │          │  (analyzers/)                │
    │                           │          │                              │
    │ • Select analyses         │          │ • Generate insights          │
    │ • Prioritize visualizations│         │ • Detect anomalies          │
    │ • Recommend metrics       │          │ • Create summaries           │
    └─────────┬─────────────────┘          └────────────┬─────────────────┘
              │                                         │
              └──────────────────┬──────────────────────┘
                                 │
                                 ▼
                  ┌──────────────────────────────────────────┐
                  │    📦 Analysis Results Dictionary         │
                  │                                           │
                  │  • file_info                             │
                  │  • dataframe                             │
                  │  • classification                        │
                  │  • insights                              │
                  │  • visualizations                        │
                  └────────────────┬─────────────────────────┘
                                   │
                                   ▼
               ┌────────────────────────────────────────────────┐
               │    🎨 Dashboard Builder                         │
               │    (visualizers/dashboard_builder.py)           │
               │                                                 │
               │  • Executive summary                            │
               │  • Key insights panel                           │
               │  • Interactive visualizations                   │
               │  • Data quality section                         │
               │  • Data explorer                                │
               └────────────────┬───────────────────────────────┘
                                │
                                ├─────────────────────────┐
                                │                         │
                                ▼                         ▼
              ┌──────────────────────────┐   ┌───────────────────────────┐
              │  📊 Chart Factory        │   │  🎯 Quality Metrics       │
              │  (visualizers/)          │   │                           │
              │                          │   │ • Completeness chart      │
              │ • Histogram              │   │ • Column statistics       │
              │ • Box plot               │   │ • Quality scores          │
              │ • Bar chart              │   │                           │
              │ • Pie chart              │   └───────────────────────────┘
              │ • Scatter plot           │
              │ • Correlation heatmap    │
              │ • Line chart             │
              └──────────┬───────────────┘
                         │
                         ▼
        ┌────────────────────────────────────────┐
        │   📈 Interactive Plotly Charts         │
        │   (Rendered in Streamlit)              │
        └────────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────────┐
        │   👤 USER INTERFACE                    │
        │                                        │
        │  • Visual insights                     │
        │  • Interactive exploration             │
        │  • Data quality feedback               │
        │  • Export capabilities                 │
        └────────────────────────────────────────┘
```

---

## Data Flow

```
1. USER uploads file (CSV/Excel/JSON)
                    ↓
2. FileHandler reads and validates file
                    ↓
3. DataClassifier analyzes data structure
   • Infers column types (6 types)
   • Calculates statistics
   • Detects correlations
   • Scores quality (0-100)
                    ↓
4. MetricSelector chooses appropriate analyses
   • Univariate (single column)
   • Bivariate (two columns)
   • Multivariate (many columns)
                    ↓
5. InsightGenerator creates natural language insights
   • Data quality warnings
   • Statistical observations
   • Correlation highlights
   • Anomaly detection
                    ↓
6. DashboardBuilder creates Streamlit dashboard
   • Uses ChartFactory for visualizations
   • Renders insights and metrics
   • Provides data explorer
                    ↓
7. USER interacts with dashboard
   • Views insights
   • Explores charts
   • Filters data
   • Downloads results
```

---

## Component Dependencies

```
analyzers/main.py
    ├── depends on: utils/file_handler.py
    ├── depends on: analyzers/data_classifier.py
    ├── depends on: analyzers/metric_selector.py
    └── depends on: analyzers/insight_generator.py

visualizers/dashboard_builder.py
    └── depends on: visualizers/chart_factory.py

data_classifier.py
    └── depends on: utils/data_processor.py

chart_factory.py
    └── depends on: plotly (external)

data_processor.py
    └── depends on: pandas, numpy, scipy (external)
```

---

## Caching Strategy

```
@st.cache_data
analyze_document(uploaded_file)
    ↓
Cache Key: File content hash
Cache Duration: Session
Cache Benefits:
    • Instant re-analysis on rerun
    • No redundant processing
    • Faster user experience
```

---

## Error Handling Flow

```
Try:
    1. Read file → FileHandler
       ↓ (catch encoding errors)
    2. Validate structure → FileHandler
       ↓ (catch empty data)
    3. Classify data → DataClassifier
       ↓ (catch type errors)
    4. Generate insights → InsightGenerator
       ↓ (catch calculation errors)
    5. Build dashboard → DashboardBuilder
       ↓ (catch rendering errors)
Except:
    • Log error details
    • Show user-friendly message
    • Graceful degradation
    • Continue with partial results
```

---

## Performance Optimization

```
Large File Detection
    ↓
If rows > 100,000:
    ├── Sample to 50,000 rows
    ├── Show warning to user
    └── Continue with sample
    
If memory > 500 MB:
    ├── Use chunked processing
    ├── Limit visualizations
    └── Enable lazy loading
    
Always:
    ├── Use @st.cache_data
    ├── Vectorized pandas operations
    └── Efficient numpy calculations
```

---

## Integration Points

```
FreeMobilaChat App
    ├── Option 1: New Page
    │   └── pages/4_Data_Analysis.py
    │       └── Full automated analysis
    │
    ├── Option 2: Sidebar Widget
    │   └── streamlit_app.py (sidebar)
    │       └── Compact analysis panel
    │
    └── Option 3: Analysis Extension
        └── pages/2_Analysis.py
            └── Additional analysis section
```

---

## Module Interaction Example

```python
# User uploads file
uploaded_file = st.file_uploader(...)

# Main analyzer orchestrates
results = analyze_document(uploaded_file)
    │
    ├──> FileHandler.read_file()
    │    └──> Returns DataFrame
    │
    ├──> DataClassifier(df).classify()
    │    └──> Returns classification results
    │
    ├──> MetricSelector(types, stats).select_metrics()
    │    └──> Returns recommended analyses
    │
    └──> InsightGenerator(df, results).generate_insights()
         └──> Returns list of insights

# Dashboard builder renders
dashboard = DashboardBuilder(results)
dashboard.generate()
    │
    ├──> ChartFactory(df, types).create_chart(spec)
    │    └──> Returns Plotly Figure
    │
    └──> st.plotly_chart(fig)
         └──> Renders in Streamlit
```

---

This architecture ensures:
- ✅ Separation of concerns
- ✅ Modular design
- ✅ Easy testing
- ✅ Simple integration
- ✅ Performance optimization
- ✅ Error resilience
