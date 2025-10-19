# Tweet Dataset Documentation

## Data Source and Extraction
- **Original file**: `data/raw/free tweet export.xlsx`
- **Sheet name**: "Tweets nettoyés uniques - LLM"
- **Extraction date**: 2025-10-11 21:07:59
- **Processing script**: `data_preparation.py`

## Dataset Statistics
- **Total tweets (original)**: 3,764
- **Total tweets (after cleaning)**: 3,764
- **Unique authors**: 2,660
- **Date range**: 2020-12-28 to 2025-06-17

## Data Cleaning Operations Applied
1. **Empty text removal**: 0 tweets removed
2. **Duplicate removal**: 0 duplicate tweets removed
3. **Text truncation**: 13 tweets truncated (>500 chars)
4. **Date standardization**: 0 invalid dates fixed
5. **Author extraction**: Usernames extracted from Twitter URLs
6. **Sequential ID assignment**: 6-digit zero-padded tweet IDs assigned

## Column Descriptions

| Column | Data Type | Description | Example |
|--------|-----------|-------------|---------|
| `tweet_id` | string | Sequential 6-digit identifier | "000001" |
| `author` | string | Twitter username (extracted from URL) | "Freebox" |
| `text` | string | Tweet content (cleaned, max 500 chars) | "RT : retrouvez désormais..." |
| `date` | datetime | Tweet creation timestamp (UTC) | "2021-05-14 10:56:22+00:00" |
| `url` | string | Original Twitter URL | "https://twitter.com/Freebox/status/..." |

## Text Statistics
- **Minimum length**: 1 characters
- **Maximum length**: 503 characters
- **Average length**: 152.9 characters
- **Median length**: 152.0 characters

## Data Quality Notes
- All tweets contain non-empty text content
- No duplicate tweets based on text content
- All URLs are valid Twitter/X.com links
- Dates are standardized to UTC timezone
- Text content has been cleaned of control characters and excessive punctuation

## Files Generated
- **Main dataset**: `data/raw/free_tweet_export.csv` - Complete cleaned dataset
- **Sample dataset**: `data/samples/sample_tweets.csv` - Random sample of 100 tweets for testing

## Usage Recommendations
- Use the main dataset for full analysis
- Use the sample dataset for testing and development
- Consider the date range when analyzing temporal patterns
- Author field may contain "unknown" for URLs that couldn't be parsed

## Data Format
- **Encoding**: UTF-8
- **Delimiter**: Comma (,)
- **Quote character**: Double quote (")
- **Header**: First row contains column names
