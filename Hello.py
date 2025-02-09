import os
import streamlit as st
from pdf_parsing import process_pdf  # Import the PDF processing function
import time

# Set page configuration including title and icon
st.set_page_config(page_title="UniGPT", page_icon="🎓", layout="wide")


# Initialize dark mode state
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# Dark mode toggle button
if st.button("Toggle Dark/Light Mode"):
    st.session_state.dark_mode = not st.session_state.dark_mode

# Apply styles based on dark mode state
if st.session_state.dark_mode:
    st.markdown(
        """
        <style>
        /* General app styles */
        .stApp {
            background-color: #121212 !important;
            color: #e0e0e0 !important;
            transition: background-color 0.5s ease, color 0.5s ease;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #bb86fc !important;
            transition: color 0.5s ease;
        }
        .stButton > button {
            background-color: #bb86fc !important;
            color: #fff !important;
            border-radius: 12px;
            font-weight: bold;
            padding: 8px 16px;
            transition: background-color 0.3s ease, color 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #3700b3 !important;
        }
        .stFileUploader > div > button {
            background-color: #bb86fc !important;
            color: #121212 !important;
            border-radius: 12px;
            font-weight: bold;
        }
        footer {
            background-color: #1e1e1e;
            color: #bb86fc;
            padding: 10px;
            border-radius: 8px;
        }
        .css-1v3fvcr {
            background-color: #1e1e1e !important;
            color: #bb86fc !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #f7f7f7 !important;
            color: #333 !important;
            transition: background-color 0.5s ease, color 0.5s ease;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #6a1b9a !important;
            transition: color 0.5s ease;
        }
        .stButton > button {
            background-color: #6a1b9a !important;
            color: #fff !important;
            border-radius: 12px;
            font-weight: bold;
            padding: 8px 16px;
            transition: background-color 0.3s ease, color 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #4a148c !important;
        }
        .stFileUploader > div > button {
            background-color: #6a1b9a !important;
            color: #fff !important;
            border-radius: 12px;
            font-weight: bold;
        }
        footer {
            background-color: #f3e5f5;
            color: #6a1b9a;
            padding: 10px;
            border-radius: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Header section
st.markdown(
    """
    <div style="text-align: center; margin-top: 20px; animation: fadeIn 2s;">
        <h1 style="font-size: 3rem">🎓 Welcome to UniGPT!</h1>
        <p>Explore the inner insights based on the course materials you provide.</p>
    </div>
    <style>
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Features section with icons and animation
st.markdown(
    """
    <div style="text-align: center; margin: 20px; border: 2px solid purple; border-radius: 30px; padding: 20px; animation: slideIn 1s;">
        <h3>🛠 Features:</h3>
        <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
            <div style="flex: 1; max-width: 300px;">
                <p>📁 <b>Upload Materials:</b> Easily upload PDFs, DOCX, or TXT files.</p>
            </div>
            <div style="flex: 1; max-width: 300px;">
                <p>📄 <b>Summarize Content:</b> Generate concise summaries.</p>
            </div>
            <div style="flex: 1; max-width: 300px;">
                <p>💬 <b>Chat with Content:</b> Ask questions directly from your material.</p>
            </div>
        </div>
    </div>
    <style>
    @keyframes slideIn {
        from { transform: translateY(20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# File uploader section
st.markdown(
    """
    <div style="text-align: center; margin: 20px; animation: fadeIn 2s;">
        <h3>📁 Upload Your File:</h3>
    </div>
    """,
    unsafe_allow_html=True,
)
uploaded_file = st.file_uploader("", type=["pdf", "docx", "txt"], label_visibility="collapsed")
if uploaded_file is not None:
    st.success(f"✅ Uploaded: {uploaded_file.name}")
    
    # Process PDF files using process_pdf function
    if uploaded_file.name.lower().endswith(".pdf"):
        temp_pdf_path = "temp.pdf"
        with open(temp_pdf_path, "wb") as f:
            f.write(uploaded_file.read())
        st.write("Processing the PDF file...")
        try:
            # Create a progress bar and spinner
            progress_bar = st.progress(0)
            with st.spinner("Processing PDF..."):
                # Simulate inital progress update
                progress_bar.progress(20)
                time.sleep(0.2)
                # Call the processing function - might take time
                summary = process_pdf(temp_pdf_path)
                # Update progress to near completion
                progress_bar.progress(80)
                time.sleep(0.2)  # Optional delay for visual effect

                # Final the progress bar to 100%
                progress_bar.progress(100)

            st.subheader("Summary")
            st.write(summary)
        except Exception as e:
            st.error(f"Error processing PDF: {e}")
        finally:
            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)
    else:
        st.info("Currently, only PDF files are processed for summarization.")

# Display a banner image with animation
st.image("assets/banner.png", use_container_width=True, caption="Your AI-powered assistant.")

# Footer section
st.markdown(
    """
    <hr>
    <footer style="text-align: center; margin-top: 20px; animation: fadeIn 2s;">
        <p>Made with ❤️ by the UniGPT Team</p>
    </footer>
    """,
    unsafe_allow_html=True,
)
