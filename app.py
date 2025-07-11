import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
import io

st.set_page_config(page_title="Comet Envions Pvt Ltd", layout="wide")
st.markdown("<h2 style='color:green;'>🌍 Comet Envions Pvt Ltd</h2>", unsafe_allow_html=True)
st.title("📊 Universal Sensor Data Plotter")

# File upload
uploaded_file = st.file_uploader("📁 Upload Data File (CSV, Excel, TXT...)", type=None)

if uploaded_file:
    try:
        # Detect file type and read accordingly
        file_name = uploaded_file.name
        if file_name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, engine="python")
        elif file_name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
        elif file_name.endswith(".txt"):
            df = pd.read_csv(uploaded_file, delimiter="\t", engine="python")
        else:
            st.error("❌ Unsupported file type.")
            st.stop()

        # Clean & de-duplicate column names
        cleaned_cols = []
        col_counts = {}
        for col in df.columns:
            cleaned = re.sub(r'[^\w\s]', '', str(col)).strip().replace(" ", "_")
            if cleaned in col_counts:
                col_counts[cleaned] += 1
                cleaned = f"{cleaned}_{col_counts[cleaned]}"
            else:
                col_counts[cleaned] = 1
            cleaned_cols.append(cleaned)
        df.columns = cleaned_cols

        # Handle timestamp or fallback to index
        date_col = next((c for c in df.columns if "date" in c.lower()), None)
        time_col = next((c for c in df.columns if "time" in c.lower()), None)

        if date_col and time_col:
            df['Timestamp'] = pd.to_datetime(df[date_col].astype(str) + " " + df[time_col].astype(str), errors='coerce')
            x_axis = 'Timestamp'
        else:
            timestamp_col = next((c for c in df.columns if "timestamp" in c.lower()), None)
            if timestamp_col:
                df['Timestamp'] = pd.to_datetime(df[timestamp_col], errors='coerce')
                x_axis = 'Timestamp'
            else:
                df['Index'] = df.index
                x_axis = 'Index'

        # Convert to numeric and keep only columns with valid numbers
        numeric_columns = []
        for col in df.columns:
            if col == x_axis:
                continue
            df[col] = pd.to_numeric(df[col], errors='coerce')
            if df[col].notna().sum() > 0:
                numeric_columns.append(col)

        # DEBUGGING: Show columns identified
        st.write("✅ Detected Numeric Columns:", numeric_columns)

        # Column selection
        selected_cols_plot = st.multiselect("📊 Select Columns to Plot", numeric_columns)
        selected_cols_table = st.multiselect("🖨️ Select Columns to Show in Table", numeric_columns, default=selected_cols_plot)

        # Plotting
        if selected_cols_plot:
            fig = go.Figure()
            for col in selected_cols_plot:
                non_null_df = df[[x_axis, col]].dropna()
                fig.add_trace(go.Scatter(
                    x=non_null_df[x_axis],
                    y=non_null_df[col],
                    mode='lines+markers',
                    name=col.replace("_", " "),
                    line=dict(width=2)
                ))

            fig.update_layout(
                title="📈 Sensor Data Over Time",
                xaxis_title="Time",
                yaxis_title="Sensor Values",
                hovermode='x',
                template="plotly_white",
                dragmode=False  # disable box zoom
            )

            st.plotly_chart(fig, use_container_width=True)

            # Download as PNG
            try:
                buf = io.BytesIO()
                fig.write_image(buf, format="png")
                st.download_button(
                    label="📥 Download Clean Plot as PNG",
                    data=buf.getvalue(),
                    file_name="sensor_plot.png",
                    mime="image/png"
                )
            except Exception as e:
                st.warning(f"⚠️ PNG export failed: {e}")

        else:
            st.warning("👈 Please select at least one column to plot.")

        # Data table
        if selected_cols_table:
            st.subheader("🖨️ Selected Data Table")
            st.dataframe(df[[x_axis] + selected_cols_table].dropna(how='all'))

    except Exception as e:
        st.error(f"❌ Error while processing file: {e}")
