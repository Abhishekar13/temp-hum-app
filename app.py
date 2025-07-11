import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- Page Config ---
st.set_page_config(page_title="Comet Envions Pvt Ltd", layout="wide")

# --- Header ---
st.markdown("<h2 style='color:green;'>🌍 Comet Envions Pvt Ltd</h2>", unsafe_allow_html=True)
st.title("📈 Real-Time Data Plotter")

# --- Theme Toggle ---
theme = st.radio("Select Theme", ['Light', 'Dark'], horizontal=True)
plotly_template = "plotly_dark" if theme == "Dark" else "plotly_white"

# --- File Upload ---
uploaded_file = st.file_uploader("📁 Upload CSV file", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, engine='python')
        df.columns = df.columns.str.strip()

        # Handle Time column
        if 'Time' in df.columns:
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
        else:
            st.error("No 'Time' column found in file.")
            st.stop()

        # --- Select Columns ---
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        if not numeric_cols:
            st.warning("No numeric columns found.")
            st.stop()

        selected_columns = st.multiselect("✅ Select columns to plot (Y-axis)", numeric_cols,
                                          default=numeric_cols[:2])  # Select first two by default

        # --- Plot Graph ---
        if selected_columns:
            fig = go.Figure()
            for col in selected_columns:
                fig.add_trace(go.Scatter(
                    x=df['Timestamp'],
                    y=df[col],
                    mode='lines+markers',
                    name=col,
                    line=dict(width=2)
                ))

            fig.update_layout(
                title="📊 Sensor Data Over Time",
                xaxis_title="Time",
                yaxis_title="Values",
                hovermode='x unified',
                dragmode='zoom',
                template=plotly_template,
                xaxis=dict(
                    rangeselector=dict(
                        buttons=[
                            dict(count=1, label="1h", step="hour", stepmode="backward"),
                            dict(count=6, label="6h", step="hour", stepmode="backward"),
                            dict(count=12, label="12h", step="hour", stepmode="backward"),
                            dict(step="all")
                        ]
                    ),
                    rangeslider=dict(visible=True),
                    type="date"
                ),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            )

            st.plotly_chart(fig, use_container_width=True)

            # --- Export CSV ---
            st.subheader("⬇️ Export Data")
            st.download_button(
                label="Download Full Data as CSV",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name="sensor_data.csv",
                mime='text/csv'
            )

            # --- Reset Zoom ---
            if st.button("🔄 Reset Zoom"):
                st.experimental_rerun()

            st.info("👆 Zoom using mouse or fingers. Click camera icon to save the graph.")

        else:
            st.warning("👉 Please select at least one column to plot.")

    except Exception as e:
        st.error(f"❌ Error processing the file: {e}")
