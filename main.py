import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from utils import (
    format_amount,
    calculate_balance,
    create_transaction_summary,
    create_spending_by_category,
    create_income_expense_trend
)

# Page configuration
st.set_page_config(
    page_title="Personal Finance Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'transactions' not in st.session_state:
    st.session_state.transactions = pd.DataFrame(
        columns=['date', 'type', 'category', 'amount', 'description']
    )

# Title and description
st.title("💰 Personal Finance Tracker")
st.markdown("Track your daily income and expenses with ease!")

# Sidebar for adding transactions
with st.sidebar:
    st.header("Add New Transaction")
    
    # Transaction form
    with st.form("transaction_form"):
        date = st.date_input("Date", datetime.now())
        
        transaction_type = st.selectbox(
            "Type",
            options=["Income", "Expense"]
        )
        
        categories = {
            "Income": ["Salary", "Freelance", "Investments", "Other Income"],
            "Expense": ["Food", "Transport", "Housing", "Utilities", "Entertainment", "Shopping", "Other"]
        }
        
        category = st.selectbox(
            "Category",
            options=categories[transaction_type]
        )
        
        amount = st.number_input("Amount ($)", min_value=0.01, step=0.01)
        description = st.text_input("Description")
        
        submit_button = st.form_submit_button("Add Transaction")
        
        if submit_button:
            new_transaction = pd.DataFrame([{
                'date': date,
                'type': transaction_type,
                'category': category,
                'amount': amount,
                'description': description
            }])
            
            st.session_state.transactions = pd.concat(
                [st.session_state.transactions, new_transaction],
                ignore_index=True
            )
            st.success("Transaction added successfully!")

# Main content area
col1, col2, col3 = st.columns(3)

# Calculate summary metrics
total_income, total_expenses, balance = create_transaction_summary(st.session_state.transactions)

# Display metrics
with col1:
    st.metric("Total Income", format_amount(total_income))
with col2:
    st.metric("Total Expenses", format_amount(total_expenses))
with col3:
    st.metric("Current Balance", format_amount(balance))

# Data visualization section
st.header("Financial Overview")

# Date filter
date_range = st.date_input(
    "Select Date Range",
    value=(
        st.session_state.transactions['date'].min() if not st.session_state.transactions.empty
        else datetime.now(),
        st.session_state.transactions['date'].max() if not st.session_state.transactions.empty
        else datetime.now()
    ),
    key='date_range'
)

# Filter transactions based on date range
filtered_df = st.session_state.transactions[
    (st.session_state.transactions['date'] >= date_range[0]) &
    (st.session_state.transactions['date'] <= date_range[1])
]

# Display charts
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(
        create_spending_by_category(filtered_df),
        use_container_width=True
    )

with col2:
    st.plotly_chart(
        create_income_expense_trend(filtered_df),
        use_container_width=True
    )

# Transactions table
st.header("Recent Transactions")

if not filtered_df.empty:
    st.dataframe(
        filtered_df.sort_values('date', ascending=False)
        .style.format({'amount': '${:.2f}'})
        .set_properties(**{'background-color': '#262730', 'color': '#fafafa'})
    )
else:
    st.info("No transactions found for the selected date range.")

# Footer
st.markdown("---")
st.markdown(
    "Made with ❤️ using Streamlit | "
    "Data is stored locally in your session"
)
