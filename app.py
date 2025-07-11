import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

# Page config
st.set_page_config(page_title="Comet Envions Pvt Ltd", layout="wide")

# Title and brand
st.markdown("<h2 style='color:green;'>🌍 Comet Envions Pvt Ltd</h2>", unsafe_allow_html=True)
st.title("📊 Dynamic Data Plotter")

# Upload file (any type)
uploaded_file = st.file_uploader("Upload your data file", type=["csv", "xlsx", "txt"])

if uploaded_file:
    # Determine file type
    file_type = uploaded_file.name.split('.')[-1].lower()

    # Read file dynamically
    try:
        if file_type == 'csv':
            df = pd.read_csv(uploaded_file)
        elif file_type == 'xlsx':
            df = pd.read_excel(uploaded_file)
        elif file_type == 'txt':
            df = pd.read_csv(uploaded_file, delimiter='\t')
        else:
            st.error("Unsupported file format.")
            st.stop()

        df.columns = df.columns.str.strip()
        st.success("✅ File loaded successfully!")

        # Timestamp support (optional)
        if 'Time' in df.columns or 'Timestamp' in df.columns:
            time_col = st.selectbox("Select Time Column (Optional)", options=df.columns, index=0)
        else:
            time_col = None

        # Column selector
        selected_columns = st.multiselect("Select columns to plot", options=df.columns, default=df.columns[1:3])

        if selected_columns:
            # Show data table
            st.subheader("📋 Data Preview")
            st.dataframe(df[[*selected_columns]])

            # Prepare Plot
            fig = go.Figure()
            x_vals = df[time_col] if time_col else df.index

            for col in selected_columns:
                fig.add_trace(go.Scatter(
                    x=x_vals,
                    y=df[col],
                    mode='lines+markers',
                    name=col,
                    line=dict(width=2)
                ))

            fig.update_layout(
                title='📈 Selected Data Plot',
                xaxis_title='Time' if time_col else 'Index',
                yaxis_title='Values',
                template="plotly_white",
                showlegend=True
            )

            st.plotly_chart(fig, use_container_width=True)

            # Downloadable PNG without clutter
            st.subheader("🖨️ Download Clean Graph")
            png_bytes = fig.to_image(format="png", width=1200, height=500, scale=2)
            st.download_button(
                label="📷 Download Graph as PNG",
                data=png_bytes,
                file_name="clean_graph.png",
                mime="image/png"
            )

    except Exception as e:
        st.error(f"Error loading or processing file: {e}")

