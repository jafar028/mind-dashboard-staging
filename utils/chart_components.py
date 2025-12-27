"""
Chart Components
Reusable visualization functions using Plotly
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st
from typing import List, Dict, Optional


# Color schemes
COLORS = {
    'primary': '#FF6B6B',
    'secondary': '#4ECDC4',
    'success': '#45B7D1',
    'warning': '#FFA07A',
    'danger': '#E74C3C',
    'info': '#3498DB',
    'dark': '#0E1117',
    'background': '#262730'
}

GRADE_COLORS = {
    'A (90-100)': '#2ECC71',
    'B (80-89)': '#3498DB',
    'C (70-79)': '#F39C12',
    'D (60-69)': '#E67E22',
    'F (Below 60)': '#E74C3C'
}


def create_metric_cards(metrics: List[Dict], columns: int = 4):
    """
    Create metric cards layout
    
    Args:
        metrics: List of dicts with 'label', 'value', 'delta' keys
        columns: Number of columns
    """
    cols = st.columns(columns)
    for idx, metric in enumerate(metrics):
        with cols[idx % columns]:
            st.metric(
                label=metric.get('label', ''),
                value=metric.get('value', 'N/A'),
                delta=metric.get('delta', None),
                help=metric.get('help', None)
            )


def plot_line_chart(df: pd.DataFrame, x: str, y: str, title: str, 
                    color: str = None, height: int = 400) -> go.Figure:
    """Create a line chart"""
    fig = px.line(
        df, x=x, y=y, color=color,
        title=title,
        template='plotly_dark',
        height=height
    )
    
    fig.update_layout(
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['dark'],
        font=dict(color='#FAFAFA'),
        hovermode='x unified'
    )
    
    return fig


def plot_bar_chart(df: pd.DataFrame, x: str, y: str, title: str,
                   color: str = None, orientation: str = 'v', 
                   height: int = 400) -> go.Figure:
    """Create a bar chart"""
    fig = px.bar(
        df, x=x, y=y, color=color,
        title=title,
        template='plotly_dark',
        orientation=orientation,
        height=height
    )
    
    fig.update_layout(
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['dark'],
        font=dict(color='#FAFAFA'),
        showlegend=True if color else False
    )
    
    return fig


def plot_pie_chart(df: pd.DataFrame, values: str, names: str, 
                   title: str, height: int = 400) -> go.Figure:
    """Create a pie chart"""
    fig = px.pie(
        df, values=values, names=names,
        title=title,
        template='plotly_dark',
        height=height,
        hole=0.4  # Donut chart
    )
    
    fig.update_layout(
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['dark'],
        font=dict(color='#FAFAFA')
    )
    
    return fig


def plot_heatmap(df: pd.DataFrame, x: str, y: str, z: str,
                 title: str, height: int = 500) -> go.Figure:
    """Create a heatmap"""
    # Pivot data for heatmap
    pivot_df = df.pivot(index=y, columns=x, values=z)
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_df.values,
        x=pivot_df.columns,
        y=pivot_df.index,
        colorscale='RdYlGn',
        hoverongaps=False
    ))
    
    fig.update_layout(
        title=title,
        template='plotly_dark',
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['dark'],
        font=dict(color='#FAFAFA'),
        height=height
    )
    
    return fig


def plot_radar_chart(categories: List[str], values: List[float],
                     class_avg: List[float] = None,
                     title: str = "Performance Radar",
                     height: int = 500) -> go.Figure:
    """Create a radar chart for performance comparison"""
    
    fig = go.Figure()
    
    # Student performance
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Your Score',
        line=dict(color=COLORS['primary'])
    ))
    
    # Class average if provided
    if class_avg:
        fig.add_trace(go.Scatterpolar(
            r=class_avg,
            theta=categories,
            fill='toself',
            name='Class Average',
            line=dict(color=COLORS['secondary'])
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        title=title,
        template='plotly_dark',
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['dark'],
        font=dict(color='#FAFAFA'),
        height=height
    )
    
    return fig


def plot_scatter(df: pd.DataFrame, x: str, y: str, title: str,
                 color: str = None, size: str = None,
                 height: int = 500) -> go.Figure:
    """Create a scatter plot"""
    fig = px.scatter(
        df, x=x, y=y, color=color, size=size,
        title=title,
        template='plotly_dark',
        height=height
    )
    
    fig.update_layout(
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['dark'],
        font=dict(color='#FAFAFA')
    )
    
    return fig


def plot_funnel(df: pd.DataFrame, x: str, y: str, title: str,
                height: int = 500) -> go.Figure:
    """Create a funnel chart"""
    fig = go.Figure(go.Funnel(
        y=df[y],
        x=df[x],
        textinfo="value+percent initial",
        marker=dict(color=COLORS['primary'])
    ))
    
    fig.update_layout(
        title=title,
        template='plotly_dark',
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['dark'],
        font=dict(color='#FAFAFA'),
        height=height
    )
    
    return fig


def plot_box_plot(df: pd.DataFrame, x: str, y: str, title: str,
                  height: int = 500) -> go.Figure:
    """Create a box plot"""
    fig = px.box(
        df, x=x, y=y,
        title=title,
        template='plotly_dark',
        height=height
    )
    
    fig.update_layout(
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['dark'],
        font=dict(color='#FAFAFA')
    )
    
    return fig


def plot_gauge(value: float, title: str, max_value: float = 100,
               threshold_good: float = 80, threshold_warning: float = 60,
               height: int = 300) -> go.Figure:
    """Create a gauge chart"""
    
    # Determine color based on thresholds
    if value >= threshold_good:
        color = '#2ECC71'
    elif value >= threshold_warning:
        color = '#F39C12'
    else:
        color = '#E74C3C'
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16}},
        gauge={
            'axis': {'range': [None, max_value], 'tickwidth': 1},
            'bar': {'color': color},
            'bgcolor': COLORS['background'],
            'borderwidth': 2,
            'bordercolor': "#666",
            'steps': [
                {'range': [0, threshold_warning], 'color': 'rgba(231, 76, 60, 0.2)'},
                {'range': [threshold_warning, threshold_good], 'color': 'rgba(243, 156, 18, 0.2)'},
                {'range': [threshold_good, max_value], 'color': 'rgba(46, 204, 113, 0.2)'}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['dark'],
        font=dict(color='#FAFAFA', size=14),
        height=height
    )
    
    return fig


def plot_timeline(df: pd.DataFrame, x: str, y: str, title: str,
                  color: str = None, height: int = 400) -> go.Figure:
    """Create a timeline/gantt chart"""
    fig = px.timeline(
        df, x_start=x, x_end=y, y=color,
        title=title,
        template='plotly_dark',
        height=height
    )
    
    fig.update_layout(
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['dark'],
        font=dict(color='#FAFAFA')
    )
    
    return fig


def plot_histogram(df: pd.DataFrame, x: str, title: str,
                   nbins: int = 20, height: int = 400) -> go.Figure:
    """Create a histogram"""
    fig = px.histogram(
        df, x=x, nbins=nbins,
        title=title,
        template='plotly_dark',
        height=height
    )
    
    fig.update_layout(
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['dark'],
        font=dict(color='#FAFAFA')
    )
    
    return fig


def create_multi_line_chart(df: pd.DataFrame, x: str, y_columns: List[str],
                           title: str, height: int = 400) -> go.Figure:
    """Create a multi-line chart"""
    fig = go.Figure()
    
    colors_list = [COLORS['primary'], COLORS['secondary'], COLORS['success'], COLORS['info']]
    
    for idx, col in enumerate(y_columns):
        fig.add_trace(go.Scatter(
            x=df[x],
            y=df[col],
            name=col,
            mode='lines+markers',
            line=dict(color=colors_list[idx % len(colors_list)])
        ))
    
    fig.update_layout(
        title=title,
        template='plotly_dark',
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['dark'],
        font=dict(color='#FAFAFA'),
        hovermode='x unified',
        height=height
    )
    
    return fig


def export_dataframe_to_csv(df: pd.DataFrame, filename: str):
    """Provide CSV download button for DataFrame"""
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=filename,
        mime='text/csv',
    )


def export_dataframe_to_excel(df: pd.DataFrame, filename: str):
    """Provide Excel download button for DataFrame"""
    import io
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    
    st.download_button(
        label="📥 Download Excel",
        data=buffer.getvalue(),
        file_name=filename,
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
