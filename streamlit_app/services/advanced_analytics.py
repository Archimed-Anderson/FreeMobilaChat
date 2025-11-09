"""
Advanced Analytics Module
Provides enhanced KPIs and visualizations for FreeMobilaChat
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta


def calculate_thematic_distribution(df: pd.DataFrame) -> Dict[str, int]:
    """
    Calculate distribution by category (fiber, WiFi, mobile, billing, etc.)
    """
    if 'topics' not in df.columns:
        return {}
    
    # Map topics to business categories
    category_mapping = {
        'connexion': 'WiFi',
        'wifi': 'WiFi',
        'internet': 'WiFi',
        'fibre': 'Fiber',
        'mobile': 'Mobile',
        '4g': 'Mobile',
        '5g': 'Mobile',
        'facture': 'Billing',
        'paiement': 'Billing',
        'prix': 'Billing',
        'box': 'Equipment',
        'equipement': 'Equipment',
        'livebox': 'Equipment',
        'decodeur': 'Equipment',
        'reseau': 'Network',
        'coupure': 'Network',
        'panne': 'Technical',
        'technique': 'Technical',
        'commercial': 'Commercial',
        'service': 'Customer Service',
        'assistance': 'Customer Service'
    }
    
    categories = {}
    for topic in df['topics'].dropna():
        topic_lower = str(topic).lower()
        matched = False
        for keyword, category in category_mapping.items():
            if keyword in topic_lower:
                categories[category] = categories.get(category, 0) + 1
                matched = True
                break
        if not matched:
            categories['Other'] = categories.get('Other', 0) + 1
    
    return categories


def calculate_satisfaction_index(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Customer Satisfaction Index based on sentiment polarity
    Range: 0-100
    """
    if 'sentiment' not in df.columns:
        return {'score': 0, 'level': 'Unknown', 'distribution': {}}
    
    sentiment_counts = df['sentiment'].value_counts()
    total = len(df)
    
    # Calculate weighted score
    weights = {
        'positif': 100,
        'neutre': 50,
        'negatif': 0
    }
    
    score = sum(
        sentiment_counts.get(sent, 0) * weight / total
        for sent, weight in weights.items()
    )
    
    # Determine satisfaction level
    if score >= 70:
        level = "Excellent"
    elif score >= 50:
        level = "Good"
    elif score >= 30:
        level = "Fair"
    else:
        level = "Poor"
    
    return {
        'score': round(score, 1),
        'level': level,
        'distribution': {
            'positive': int(sentiment_counts.get('positif', 0)),
            'neutral': int(sentiment_counts.get('neutre', 0)),
            'negative': int(sentiment_counts.get('negatif', 0))
        }
    }


def calculate_urgency_rate(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate proportion of critical urgency messages
    """
    if 'urgence' not in df.columns:
        return {'rate': 0, 'count': 0, 'distribution': {}}
    
    urgence_counts = df['urgence'].value_counts()
    total = len(df)
    
    high_urgency = urgence_counts.get('haute', 0)
    rate = (high_urgency / total * 100) if total > 0 else 0
    
    return {
        'rate': round(rate, 1),
        'count': int(high_urgency),
        'distribution': {
            str(k): int(v) for k, v in urgence_counts.to_dict().items()
        }
    }


def calculate_message_type_distribution(df: pd.DataFrame) -> Dict[str, int]:
    """
    Classify messages into types: complaints, questions, requests
    """
    if 'is_claim' not in df.columns:
        return {}
    
    distribution = {
        'Complaints': int(len(df[df['is_claim'] == 'oui'])),
        'Inquiries': int(len(df[df['is_claim'] == 'non']))
    }
    
    # Further classify non-complaints
    if 'text_cleaned' in df.columns:
        non_complaints = df[df['is_claim'] == 'non']
        question_keywords = ['?', 'comment', 'pourquoi', 'quand', 'où', 'quel']
        request_keywords = ['besoin', 'voudrais', 'souhaite', 'demande', 'merci']
        
        questions = 0
        requests = 0
        
        for text in non_complaints['text_cleaned'].dropna():
            text_lower = str(text).lower()
            if any(kw in text_lower for kw in question_keywords):
                questions += 1
            elif any(kw in text_lower for kw in request_keywords):
                requests += 1
        
        distribution['Questions'] = questions
        distribution['Requests'] = requests
        distribution['General'] = distribution['Inquiries'] - questions - requests
        del distribution['Inquiries']
    
    return distribution


def generate_time_series_data(df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    """
    Generate synthetic time series data for visualization
    Simulates evolution over time
    """
    # If date column exists, use it
    if 'date' in df.columns:
        try:
            df['parsed_date'] = pd.to_datetime(df['date'])
            return df
        except:
            pass
    
    # Generate synthetic dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Distribute tweets across dates
    dates = pd.date_range(start=start_date, end=end_date, periods=len(df))
    df_with_dates = df.copy()
    df_with_dates['synthetic_date'] = dates
    
    return df_with_dates


def create_radar_chart_data(df: pd.DataFrame) -> Dict[str, list]:
    """
    Prepare data for radar chart showing performance across domains
    """
    categories = calculate_thematic_distribution(df)
    
    # Calculate performance metrics for each category
    performance = {}
    
    for category, count in categories.items():
        # Performance = volume + satisfaction for that category
        # Normalize to 0-100 scale
        volume_score = min(count / len(df) * 100 * 5, 100)  # Scale up small values
        
        # Get satisfaction for this category (simplified)
        category_tweets = df[df['topics'].str.contains(category, case=False, na=False)]
        if len(category_tweets) > 0 and 'sentiment' in df.columns:
            positive_rate = len(category_tweets[category_tweets['sentiment'] == 'positif']) / len(category_tweets) * 100
            satisfaction_score = positive_rate
        else:
            satisfaction_score = 50
        
        # Combined score
        performance[category] = round((volume_score + satisfaction_score) / 2, 1)
    
    return performance


def calculate_response_priority_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create urgency vs volume matrix for prioritization
    """
    if 'urgence' not in df.columns or 'topics' not in df.columns:
        return pd.DataFrame()
    
    # Group by topic and urgency
    matrix = df.groupby(['topics', 'urgence']).size().reset_index(name='count')
    
    # Pivot for heatmap
    pivot = matrix.pivot(index='topics', columns='urgence', values='count').fillna(0)
    
    return pivot

