import google.generativeai as genai
import os
from datetime import datetime
import pandas as pd

# Configure Gemini API
genai.configure(api_key=os.environ['GOOGLE_GEMINI_API_KEY'])
model = genai.GenerativeModel('gemini-pro')

def generate_financial_advice(transactions_df):
    """
    Genera consejos financieros personalizados basados en el historial de transacciones.
    """
    if transactions_df.empty:
        return "Para generar consejos personalizados, comienza agregando algunas transacciones."

    # Calcular estadísticas relevantes
    total_gastos = transactions_df[transactions_df['type'] == 'Gasto']['amount'].sum()
    gastos_por_categoria = transactions_df[transactions_df['type'] == 'Gasto'].groupby('category')['amount'].sum()
    categoria_mayor_gasto = gastos_por_categoria.idxmax() if not gastos_por_categoria.empty else "ninguna categoría"
    monto_mayor_gasto = gastos_por_categoria.max() if not gastos_por_categoria.empty else 0

    # Crear el prompt para Gemini
    prompt = f"""
    Como asesor financiero experto, analiza los siguientes datos de gastos y proporciona 3 consejos financieros personalizados en español:

    Estadísticas del usuario:
    - Gasto total: ${total_gastos:,.2f}
    - Categoría con mayor gasto: {categoria_mayor_gasto} (${monto_mayor_gasto:,.2f})
    - Distribución de gastos por categoría:
    {gastos_por_categoria.to_string()}

    Proporciona 3 consejos financieros específicos y prácticos basados en estos datos.
    Usa un tono amigable y motivador.
    Cada consejo debe ser conciso y accionable.
    Formatea la respuesta con viñetas (•).
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Lo siento, no pude generar consejos en este momento. Por favor, intenta más tarde. Error: {str(e)}"

def get_monthly_advice(transactions_df):
    """
    Genera un resumen mensual con consejos personalizados.
    """
    if transactions_df.empty:
        return "Comienza a registrar tus transacciones para recibir un análisis personalizado."

    current_month = datetime.now().strftime('%B %Y')
    
    # Análisis mensual
    ingresos_mes = transactions_df[transactions_df['type'] == 'Ingreso']['amount'].sum()
    gastos_mes = transactions_df[transactions_df['type'] == 'Gasto']['amount'].sum()
    ahorro_mes = ingresos_mes - gastos_mes
    ratio_ahorro = (ahorro_mes / ingresos_mes * 100) if ingresos_mes > 0 else 0

    prompt = f"""
    Como asesor financiero experto, analiza el siguiente resumen mensual y proporciona recomendaciones personalizadas en español:

    Resumen de {current_month}:
    - Ingresos totales: ${ingresos_mes:,.2f}
    - Gastos totales: ${gastos_mes:,.2f}
    - Ahorro: ${ahorro_mes:,.2f}
    - Ratio de ahorro: {ratio_ahorro:.1f}%

    Proporciona:
    1. Una evaluación breve del desempeño financiero del mes
    2. Un consejo específico para mejorar el ratio de ahorro
    3. Una sugerencia para el próximo mes

    Usa un tono positivo y motivador.
    Formatea la respuesta en párrafos cortos.
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"No se pudo generar el análisis mensual. Por favor, intenta más tarde. Error: {str(e)}"
