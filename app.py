import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Page Configuration
st.set_page_config(page_title="💾 Data Sweeper", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for Modern UI
st.markdown("""
    <style>
        body {
            font-family: 'Arial', sans-serif;
        }
        .main-container {
            background-color: #f9f9f9;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 2px 2px 15px rgba(0, 0, 0, 0.1);
        }
        .stButton>button {
            background-color: #007BFF !important;
            color: white !important;
            border-radius: 8px;
            padding: 8px 16px;
        }
        .stDownloadButton>button {
            background-color: #28a745 !important;
            color: white !important;
            border-radius: 8px;
            padding: 8px 16px;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar - File Upload
st.sidebar.header("📂 Upload Your Files")
uploaded_files = st.sidebar.file_uploader("Upload CSV or Excel files", type=['csv', 'xlsx'], accept_multiple_files=True)

# Title & Description
st.markdown("<h1 style='color:#007BFF;'>🧹 Data Sweeper</h1>", unsafe_allow_html=True)
st.write("📂 **Upload your data file, clean it, analyze it, and export it effortlessly!**")

# Tabs for workflow
tabs = st.tabs(["📄 Files", "🛠 Clean Data", "📊 Visualize", "⬇️ Export"])

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.sidebar.error(f"❌ Unsupported file type: {file_ext}")
            continue

        # File Details
        with tabs[0]:  # Upload Tab
            st.subheader(f"📋 File Details - {file.name}")
            st.markdown(f"""
            - **📄 File Name:** {file.name}
            - **📏 File Size:** {file.size / 1024:.2f} KB  
            """)
            with st.expander("🔍 **Preview Data**"):
                st.dataframe(df.head())

        # Data Cleaning
        with tabs[1]:  # Clean Data Tab
            st.subheader("🛠 Data Cleaning Options")

            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"🗑 Remove Duplicates ({file.name})"):
                    df.drop_duplicates(inplace=True)
                    st.success("✅ Duplicates removed!")

            with col2:
                if st.button(f"🧮 Fill Missing Values ({file.name})"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.success("✅ Missing values filled!")

            # Column Selection
            st.subheader("📊 Select Columns")
            columns = st.multiselect(f"📌 Choose columns to keep for {file.name}", df.columns, default=df.columns)
            df = df[columns]

        # Data Visualization
        with tabs[2]:  # Visualize Tab
            st.subheader("📊 Data Visualizations")
            with st.expander(f"📊 Show Summary of {file.name}"):
                numeric_df = df.select_dtypes(include=['number'])
                if not numeric_df.empty:
                    # Ensure column names are valid for Altair
                    numeric_df.columns = [str(col).strip().replace(" ", "_") for col in numeric_df.columns]
                    try:
                        st.bar_chart(numeric_df.iloc[:, :2])
                    except Exception as e:
                        st.error(f"⚠️ Error rendering chart: {e}")
                else:
                    st.warning("⚠️ No numerical data available for visualization.")

        # File Conversion & Export
        with tabs[3]:  # Export Tab
            st.subheader("🔄 Convert & Download")

            conversion_type = st.radio(f"🎯 Convert {file.name} to:", ["CSV", "Excel"], key=file.name)

            if st.button(f"🔄 Convert {file.name}"):
                buffer = BytesIO()
                if conversion_type == "CSV":
                    df.to_csv(buffer, index=False)
                    file_name = file.name.replace(file_ext, ".csv")
                    mime_type = "text/csv"
                elif conversion_type == "Excel":
                    df.to_excel(buffer, index=False)
                    file_name = file.name.replace(file_ext, ".xlsx")
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

                buffer.seek(0)

                st.download_button(
                    label=f"⬇️ Download {file_name}",
                    data=buffer,
                    file_name=file_name,
                    mime=mime_type
                )
                st.success(f"✅ {file_name} has been converted to {conversion_type}!")
