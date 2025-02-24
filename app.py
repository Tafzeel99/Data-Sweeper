import streamlit as st
import pandas as pd
import os
from io import BytesIO


#Set up our App
st.set_page_config(page_title="💾 Data Sweeper", layout="wide")
st.title("Data Sweeper")
st.write("Upload your data file and we will clean it for you!")


uploaded_files = st.file_uploader("Upload your files (CSV or Excel)", type=['csv', 'xlsx'], accept_multiple_files=True)	

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"File type not supported {file_ext}")
            continue

        #Display info about the file
        st.write(f"**File Name**: {file.name}")
        st.write(f"**File Size**: {file.size/1024}")


        #Show 5 rows of our data frame
        st.write("preview of the head of the Dataframe")
        st.dataframe(df.head())

        #Options for Data cleaning
        st.subheader("Data Cleaning Options")
        if st.checkbox(f"Clean data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove Duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("Duplicates removed!")

            with col2:
                if st.button(f"Fill missing values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns    
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean()) 
                    st.write("Missing values are filled!")
                    

        # Choose specifc columns to keep or convert
        st.subheader("Select columns to convert")
        columns = st.multiselect(f"Select columns for {file.name}", df.columns, default=df.columns)
        df = df[columns]


        # Crare some visualizations
        st.subheader("Data Visualizations")
        if st.checkbox(f"Show Data Summary {file.name}"):
            st.bar_chart(df.select_dtypes(include=['number']).iloc[:,:2])

        # Convert the files -> CSV to Excel 
        st.subheader("Convert Data Options")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)
        if st.button(f"Convert {file.name}"):
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


            # Download the file
            st.download_button(
                label=f"Click here to download {file_name} as {conversion_type}", 
                data=buffer, 
                file_name=file_name, 
                mime=mime_type
            )

            st.success(f"{file_name} has been converted to {conversion_type}")