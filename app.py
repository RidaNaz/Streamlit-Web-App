import streamlit as st
import pandas as pd
import os
from io import BytesIO
import base64
import altair as alt

# Must be the first Streamlit command
st.set_page_config(
    page_title="Rida Naz",
    layout="wide",
    page_icon="favicon.ico",
)

# Then add the background color style
st.markdown("""
    <style>
        .stApp {
            background-color: #1e1e1e;
        }
    </style>
""", unsafe_allow_html=True)

# Custom CSS for styling the app with dark mode aesthetics
st.markdown(
    """
    <style>
        .main {
            background-color: #121212;  /* Overall dark background for the main page */
        }
        .block-container {
            padding: 3rem 2rem;  /* Padding around main container for spacing */
            border-radius: 12px;  /* Rounds the corners of the container */
            background-color: #1e1e1e;  /* Slightly lighter shade for contrast */
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);  /* Adds subtle shadow for depth */
        }
        h1, h2, h3, h4, h5, h6 {
            color: #66c2ff;  /* Light blue color for headings to stand out */
        }
        .stButton>button {
            border: none;
            border-radius: 8px;  /* Rounds button edges */
            background-color: #0078D7;  /* Primary blue for buttons */
            color: white;  /* White text for contrast */
            padding: 0.75rem 1.5rem;  /* Enlarges button for better interaction */
            font-size: 1rem;  /* Readable button text */
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);  /* Shadow for button depth */
        }
        .stButton>button:hover {
            background-color: #005a9e;  /* Darker blue on hover for visual feedback */
            cursor: pointer;
        }
        .stDataFrame, .stTable {
            border-radius: 10px;  /* Smooth edges for data tables and frames */
            overflow: hidden;  /* Prevents data from overflowing the container */
        }
        .css-1aumxhk, .css-18e3th9 {
            text-align: left;
            color: white;  /* Ensures all standard text is white for readability */
        }
        .stRadio>label {
            font-weight: bold;
            color: white;
        }
        .stCheckbox>label {
            color: white;
        }
        .stDownloadButton>button {
            background-color: #28a745;  /* Green color for download buttons */
            color: white;
        }
        .stDownloadButton>button:hover {
            background-color: #218838;  /* Darker green on hover for download buttons */
        }
        
        /* Center the title */
        h1 {
            color: #66c2ff;
            text-align: center !important;
        }
        
        /* If needed, also center the subtitle text */
        .stMarkdown div:first-child p {
            text-align: center;
            margin-bottom: 5rem !important;  /* Adds space after the subtitle */
        }
        
        /* Style the file uploader */
        .css-1v0mbdj {
            margin-top: 2rem;  /* Additional space above file uploader */
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Display the main app title and introductory text
st.title("Advanced Data Sweeper")  # Large, eye-catching title
st.markdown("<p style='text-align: center;'>Transform your files between CSV and Excel formats with built-in data cleaning and visualization.</p>", unsafe_allow_html=True)  # Centered subtitle

# File uploader widget that accepts CSV and Excel files
uploaded_files = st.file_uploader("Upload your files (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

# Processing logic for uploaded files (if any files are uploaded)
if uploaded_files:
    for file in uploaded_files:
        # Extract the file extension to determine if it's CSV or Excel
        file_extension = os.path.splitext(file.name)[-1].lower()
        
        # Read the uploaded file into a pandas DataFrame based on its extension
        if file_extension == ".csv":
            df = pd.read_csv(file)
        elif file_extension == ".xlsx":
            df = pd.read_excel(file)  
        else:
            # Show an error message if the file type is unsupported
            st.error(f"Unsupported file type: {file_extension}")
            continue
        
        # Display uploaded file information (name and size)
        st.write(f"**📄 File Name:** {file.name}")
        st.write(f"**📏 File Size:** {file.size / 1024:.2f} KB")

        # Preview the first 5 rows of the uploaded file
        st.write("🔍 Preview of the Uploaded File:")
        st.dataframe(df.head())
        
        # Section for data cleaning options
        st.subheader("🛠️ Data Cleaning Options")
        if st.checkbox(f"Clean Data for {file.name}"):
            col1, col2 = st.columns(2)
            with col1:
                # Button to remove duplicate rows from the DataFrame
                if st.button(f"Remove Duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("Duplicates Removed!")
            with col2:
                # Button to fill missing numeric values with column means
                if st.button(f"Fill Missing Values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("Missing Values in Numeric Columns Filled with Column Means!")

        # Section to choose specific columns to convert
        st.subheader("🎯 Select Columns to Convert")
        columns = st.multiselect(f"Choose Columns for {file.name}", df.columns, default=df.columns)
        df = df[columns] 
        
        # Visualization section for uploaded data
        st.subheader("📊 Data Visualization")
        if st.checkbox(f"Show Visualization for {file.name}"):
            # First, ensure your numeric columns are properly formatted
            df_numeric = df.select_dtypes(include='number')

            # Convert the index to a string type if it's not already
            df_numeric.index = df_numeric.index.astype(str)

            # Create a bar chart using Altair
            chart = alt.Chart(df_numeric.reset_index()).mark_bar().encode(
                x=alt.X(df_numeric.columns[0], type='quantitative'),
                y=alt.Y(df_numeric.columns[1], type='quantitative')
            )

            # Display the chart
            st.altair_chart(chart, use_container_width=True)
        
        # Section to choose file conversion type (CSV or Excel)
        st.subheader("🔄 Conversion Options")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)
        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                file_name = file.name.replace(file_extension, ".csv")
                mime_type = "text/csv"
            elif conversion_type == "Excel":
                df.to_excel(buffer, index=False, engine='openpyxl')
                file_name = file.name.replace(file_extension, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            buffer.seek(0)
            
            # Download button for the converted file
            st.download_button(
                label=f"⬇️ Download {file.name} as {conversion_type}",
                data=buffer,
                file_name=file_name,
                mime=mime_type
            )

            st.success("🎉 All files processed successfully!")

# Add footer with name and favicon
favicon_path = "favicon.ico"
footer_html = """
    <div style="position: fixed; bottom: 0; left: 0; right: 0; background-color: #1e1e1e; 
    padding: 0.5rem; margin: 0; width: 100%; text-align: center;">
"""

if os.path.exists(favicon_path):
    with open(favicon_path, "rb") as f:
        favicon_b64 = base64.b64encode(f.read()).decode()
    footer_html += f'<img src="data:image/x-icon;base64,{favicon_b64}" style="height: 30px; vertical-align: middle; margin-right: 10px;">'

footer_html += '<span style="color: white; font-size: 1.2rem;">Rida Naz</span></div>'
st.markdown(footer_html, unsafe_allow_html=True)