import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import streamlit as st
import plotly.express as px

def plot_top_artists_interactive(df):
    """Generates an interactive bar plot of top artists using Plotly."""
    if df is None or df.empty:
        st.warning("No data available to plot.")
        return
    
    top_artists = df.rename(columns={'artist': 'Artist', 'popularity': 'Average Popularity'})
    
    fig = px.bar(top_artists, x='Average Popularity', y='Artist', orientation='h', 
                 title='Top 10 Artists by Average Popularity (Interactive)',
                 color='Average Popularity', color_continuous_scale='viridis')
    st.plotly_chart(fig)