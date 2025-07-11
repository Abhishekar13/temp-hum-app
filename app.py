import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- Page Config ---
st.set_page_config(page_title="Comet Envions Pvt Ltd", layout="wide")

# --- Header ---
st.markdown("<h2 style='color:green;'>🌍 Comet Envions Pvt Ltd</h2>", unsafe_allow_html=True)
st.title("📈 Temperature & Humidity Plotter")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, engine='python')
    df.columns = df.columns.str.strip()

    try:
        # Convert Time Column
        df['Time'] = pd.to_datetime(df['Time'], format='%H:%M', errors='coerce').dt.time
        df = df.dropna(subset=['Time'])

        # Create Timestamp
        start_date = datetime(2025, 7, 7)
        timestamps = []
        last_hour = 0
        day_offset = 0

        for t in df['Time']:
            hour = t.hour
            if hour < last_hour:
                day_offset += 1
            dt = datetime.combine(start_date + timedelta(days=day_offset), t)
            timestamps.append(dt)
            last_hour = hour

        df['Timestamp'] = timestamps

        # Rename columns
        df.rename(columns={
            'TEMPERATURE PV (Deg C)'        : 'Temp_PV',
            'TEMPERATURE Set Point (Deg C)' : 'Temp_SP',
            'HUMIDITY PV (RH)'              : 'Hum_PV',
            'HUMIDITY Set Point (RH)'       : 'Hum_SP'
        }, inplace=True)

        # Drop rows with missing values
        df = df.dropna(subset=['Temp_PV', 'Temp_SP', 'Hum_PV', 'Hum_SP'])

        # --- Plotly Interactive Plot ---
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df['Timestamp'], y=df['Temp_PV'],
            mode='lines',
            name='Temp PV (°C)',
            line=dict(color='red', width=2)
        ))

        fig.add_trace(go.Scatter(
            x=df['Timestamp'], y=df['Temp_SP'],
            mode='lines',
            name='Temp SP (°C)',
            line=dict(color='blue', dash='dash', width=2)
        ))

        fig.add_trace(go.Scatter(
            x=df['Timestamp'], y=df['Hum_PV'],
            mode='lines',
            name='Humidity PV (%)',
            line=dict(color='green', width=2)
        ))

        fig.add_trace(go.Scatter(
            x=df['Timestamp'], y=df['Hum_SP'],
            mode='lines',
            name='Humidity SP (%)',
            line=dict(color='orange', dash='dash', width=2)
        ))

        # --- Layout Settings ---
        fig.update_layout(
            title='Temperature and Humidity Over Time',
            xaxis_title='Time',
            yaxis_title='Values',
            hovermode='x unified',
            dragmode='zoom',
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1h", step="hour", stepmode="backward"),
                        dict(count=6, label="6h", step="hour", stepmode="backward"),
                        dict(count=12, label="12h", step="hour", stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                rangeslider=dict(visible=True),
                type="date"
            ),
            template='plotly_white',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        )

        # --- Show Plot ---
        st.plotly_chart(fig, use_container_width=True)
        st.info("👆 Zoom with your mouse or fingers. Click camera icon to save a snapshot of the graph.")

    except Exception as e:
        st.error(f"❌ Error processing the file: {e}")
