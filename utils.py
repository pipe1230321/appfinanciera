import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def format_amount(amount):
    """Format amount with currency symbol and thousand separators"""
    return f"${amount:,.2f}"

def calculate_balance(df):
    """Calculate total balance from transactions"""
    if df.empty:
        return 0
    return df[df['type'] == 'Income']['amount'].sum() - df[df['type'] == 'Expense']['amount'].sum()

def create_transaction_summary(df):
    """Create summary metrics for transactions"""
    if df.empty:
        return 0, 0, 0
    
    total_income = df[df['type'] == 'Income']['amount'].sum()
    total_expenses = df[df['type'] == 'Expense']['amount'].sum()
    balance = total_income - total_expenses
    
    return total_income, total_expenses, balance

def create_spending_by_category(df):
    """Create a pie chart of spending by category"""
    if df.empty or len(df[df['type'] == 'Expense']) == 0:
        return go.Figure()
    
    expenses_by_category = df[df['type'] == 'Expense'].groupby('category')['amount'].sum()
    fig = px.pie(
        values=expenses_by_category.values,
        names=expenses_by_category.index,
        title='Expenses by Category',
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#fafafa'
    )
    return fig

def create_income_expense_trend(df):
    """Create a line chart showing income and expense trends"""
    if df.empty:
        return go.Figure()
    
    daily_summary = df.groupby(['date', 'type'])['amount'].sum().reset_index()
    fig = px.line(
        daily_summary,
        x='date',
        y='amount',
        color='type',
        title='Income vs Expenses Trend',
        color_discrete_map={'Income': '#00ff95', 'Expense': '#ff6b6b'}
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#fafafa',
        xaxis_title='Date',
        yaxis_title='Amount ($)'
    )
    return fig
