import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from utils import (
    format_amount,
    calculate_balance,
    create_transaction_summary,
    create_spending_by_category,
    create_income_expense_trend,
    init_db,
    add_transaction,
    get_transactions,
    update_transaction,
    delete_transaction
)
from ai_advisor import generate_financial_advice, get_monthly_advice

# Initialize database
init_db()

# Page configuration
st.set_page_config(
    page_title="Control de Finanzas Personales",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("💰 Control de Finanzas Personales")
st.markdown("¡Controla tus ingresos y gastos diarios de manera fácil!")

# Sidebar for adding transactions
with st.sidebar:
    st.header("Agregar Nueva Transacción")

    # Transaction form
    with st.form("transaction_form"):
        date = st.date_input("Fecha", datetime.now())

        transaction_type = st.selectbox(
            "Tipo",
            options=["Ingreso", "Gasto"]
        )

        categories = {
            "Ingreso": ["Salario", "Freelance", "Inversiones", "Otros Ingresos"],
            "Gasto": ["Alimentación", "Transporte", "Vivienda", "Servicios", "Entretenimiento", "Compras", "Otros"]
        }

        category = st.selectbox(
            "Categoría",
            options=categories[transaction_type]
        )

        amount = st.number_input("Monto ($)", min_value=0.01, step=0.01)
        description = st.text_input("Descripción")

        submit_button = st.form_submit_button("Agregar Transacción")

        if submit_button:
            add_transaction(date, transaction_type, category, amount, description)
            st.success("¡Transacción agregada exitosamente!")
            st.rerun()

# Main content area
col1, col2, col3 = st.columns(3)

# Date filter
date_range = st.date_input(
    "Seleccionar Rango de Fechas",
    value=(
        datetime.now().replace(day=1),  # First day of current month
        datetime.now()
    ),
    key='date_range'
)

# Get filtered transactions
filtered_df = get_transactions(date_range[0], date_range[1])

# Calculate summary metrics
total_income, total_expenses, balance = create_transaction_summary(filtered_df)

# Display metrics
with col1:
    st.metric("Ingresos Totales", format_amount(total_income))
with col2:
    st.metric("Gastos Totales", format_amount(total_expenses))
with col3:
    st.metric("Balance Actual", format_amount(balance))

# Data visualization section
st.header("Resumen Financiero")

# Display charts
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(
        create_spending_by_category(filtered_df),
        use_container_width=True,
        key="pie_chart"
    )

with col2:
    st.plotly_chart(
        create_income_expense_trend(filtered_df),
        use_container_width=True,
        key="line_chart"
    )

# AI Financial Advice Section
st.header("💡 Consejos Financieros Personalizados")
col1, col2 = st.columns([2, 1])

with col1:
    if not filtered_df.empty:
        monthly_advice = get_monthly_advice(filtered_df)
        st.markdown(f"### Análisis Mensual\n{monthly_advice}")
    else:
        st.info("Agrega transacciones para recibir un análisis mensual personalizado.")

with col2:
    if not filtered_df.empty:
        st.markdown("### Consejos para Mejorar")
        financial_advice = generate_financial_advice(filtered_df)
        st.markdown(financial_advice)
    else:
        st.info("Comienza a registrar tus gastos para recibir consejos personalizados.")


# Transactions table
st.header("Transacciones Recientes")

if not filtered_df.empty:
    # Add edit and delete buttons to each row
    for index, row in filtered_df.iterrows():
        col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 0.5, 0.5])

        with col1:
            st.write(f"**{row['description']}**")
        with col2:
            st.write(row['date'].strftime('%Y-%m-%d'))
        with col3:
            st.write(row['type'])
        with col4:
            st.write(format_amount(row['amount']))
        with col5:
            if st.button("✏️", key=f"edit_{row['id']}"):
                st.session_state.editing = row['id']
                st.session_state.edit_date = row['date']
                st.session_state.edit_type = row['type']
                st.session_state.edit_category = row['category']
                st.session_state.edit_amount = row['amount']
                st.session_state.edit_description = row['description']
        with col6:
            if st.button("🗑️", key=f"delete_{row['id']}"):
                delete_transaction(row['id'])
                st.success("Transacción eliminada exitosamente")
                st.rerun()

        # Show edit form if editing this transaction
        if 'editing' in st.session_state and st.session_state.editing == row['id']:
            with st.form(key=f"edit_form_{row['id']}"):
                edit_date = st.date_input("Fecha", st.session_state.edit_date)
                edit_type = st.selectbox("Tipo", options=["Ingreso", "Gasto"], index=0 if st.session_state.edit_type == "Ingreso" else 1)
                edit_category = st.selectbox("Categoría", options=categories[edit_type])
                edit_amount = st.number_input("Monto", value=float(st.session_state.edit_amount), min_value=0.01, step=0.01)
                edit_description = st.text_input("Descripción", st.session_state.edit_description)

                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Guardar"):
                        update_transaction(row['id'], edit_date, edit_type, edit_category, edit_amount, edit_description)
                        del st.session_state.editing
                        st.success("Transacción actualizada exitosamente")
                        st.rerun()
                with col2:
                    if st.form_submit_button("Cancelar"):
                        del st.session_state.editing
                        st.rerun()
else:
    st.info("No hay transacciones para el rango de fechas seleccionado.")

# Footer
st.markdown("---")
st.markdown(
    "Hecho con ❤️ usando Streamlit | "
    "Tus datos están almacenados de forma segura en una base de datos"
)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(environ.get("PORT", 5000)))
