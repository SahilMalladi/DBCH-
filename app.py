import streamlit as st
import pandas as pd
from datetime import datetime
import os


# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="DBCH PBC Automation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown(
    """
    <style>
        .main-title {
            font-size: 42px;
            font-weight: 800;
            color: #F5F7FA;
            margin-bottom: 5px;
        }

        .sub-title {
            font-size: 17px;
            color: #B8C0CC;
            margin-bottom: 25px;
        }

        .metric-card {
            background-color: #1F2937;
            padding: 20px;
            border-radius: 14px;
            border: 1px solid #374151;
            text-align: center;
        }

        .section-card {
            background-color: #111827;
            padding: 22px;
            border-radius: 14px;
            border: 1px solid #374151;
            margin-bottom: 20px;
        }

        .small-muted {
            color: #9CA3AF;
            font-size: 14px;
        }

        .footer {
            color: #9CA3AF;
            font-size: 13px;
            text-align: center;
            margin-top: 30px;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("DBCH Automation")

st.sidebar.markdown("### PBC Logic Selection")

logic_name = st.sidebar.selectbox(
    "Choose validation logic",
    [
        "Logic 1 - Bill Frequency Mismatch",
        "Logic 2 - Subscription vs Invoice Run Pending",
        "Logic 3 - Commercial Mismatch",
        "Logic 22 - Duplicate Validation"
    ]
)

st.sidebar.markdown("---")

st.sidebar.markdown("### Process Flow")
st.sidebar.write("1. Select PBC logic")
st.sidebar.write("2. Upload required reports")
st.sidebar.write("3. Preview uploaded data")
st.sidebar.write("4. Run validation")
st.sidebar.write("5. Download output Excel")

st.sidebar.markdown("---")

st.sidebar.markdown("### Supported File Type")
st.sidebar.info("Currently supported: `.xlsx` files")


# =========================================================
# HEADER
# =========================================================
st.markdown('<div class="main-title">📊 DBCH PBC Automation Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Upload input reports, run selected validation logic, and download the processed Excel output.</div>',
    unsafe_allow_html=True
)


# =========================================================
# TOP STATUS CARDS
# =========================================================
col_a, col_b, col_c = st.columns(3)

with col_a:
    st.metric("Selected Logic", logic_name.split(" - ")[0])

with col_b:
    st.metric("File Type", "XLSX")

with col_c:
    st.metric("Status", "Ready")


st.divider()


# =========================================================
# LOGIC DETAILS
# =========================================================
required_files = {
    "Logic 1 - Bill Frequency Mismatch": "Subscription Report",
    "Logic 2 - Subscription vs Invoice Run Pending": "Subscription Report + Invoice Run Pending Report",
    "Logic 3 - Commercial Mismatch": "Subscription Report + MRC Report",
    "Logic 22 - Duplicate Validation": "MRC Report"
}

logic_description = {
    "Logic 1 - Bill Frequency Mismatch": "Validates bill frequency consistency in the Subscription Report.",
    "Logic 2 - Subscription vs Invoice Run Pending": "Compares Subscription Report records with Invoice Run Pending Report records.",
    "Logic 3 - Commercial Mismatch": "Checks commercial amount differences between Subscription and MRC reports.",
    "Logic 22 - Duplicate Validation": "Identifies duplicate records in the MRC Report."
}

st.subheader("Validation Details")

detail_col1, detail_col2 = st.columns(2)

with detail_col1:
    st.info(f"**Selected Logic:** {logic_name}")

with detail_col2:
    st.info(f"**Required Input File(s):** {required_files[logic_name]}")

st.write(logic_description[logic_name])


# =========================================================
# FILE UPLOAD SECTION
# =========================================================
st.divider()
st.subheader("Upload Input Files")

subscription_file = None
invoice_file = None
mrc_file = None

upload_col1, upload_col2 = st.columns(2)

if logic_name == "Logic 1 - Bill Frequency Mismatch":
    with upload_col1:
        subscription_file = st.file_uploader(
            "Upload Subscription Report",
            type=["xlsx"],
            key="sub_logic1"
        )

elif logic_name == "Logic 2 - Subscription vs Invoice Run Pending":
    with upload_col1:
        subscription_file = st.file_uploader(
            "Upload Subscription Report",
            type=["xlsx"],
            key="sub_logic2"
        )

    with upload_col2:
        invoice_file = st.file_uploader(
            "Upload Invoice Run Pending Report",
            type=["xlsx"],
            key="inv_logic2"
        )

elif logic_name == "Logic 3 - Commercial Mismatch":
    with upload_col1:
        subscription_file = st.file_uploader(
            "Upload Subscription Report",
            type=["xlsx"],
            key="sub_logic3"
        )

    with upload_col2:
        mrc_file = st.file_uploader(
            "Upload MRC Report",
              type=["xlsx"],
            key="mrc_logic3"
        )

elif logic_name == "Logic 22 - Duplicate Validation":
    with upload_col1:
        mrc_file = st.file_uploader(
            "Upload MRC Report",
            type=["xlsx"],
            key="mrc_logic22"
        )


# =========================================================
# FILE PREVIEW
# =========================================================
def preview_file(uploaded_file, file_label):
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file, nrows=10)
            uploaded_file.seek(0)

            st.markdown(f"#### {file_label} Preview")
            st.caption(f"Uploaded file: {uploaded_file.name}")
            st.dataframe(df, use_container_width=True)

            return df.shape[1]

        except Exception as e:
            st.error(f"Unable to preview {file_label}. Error: {e}")
            return None


st.divider()
st.subheader("Uploaded File Preview")

uploaded_count = 0

if subscription_file:
    uploaded_count += 1
    preview_file(subscription_file, "Subscription Report")

if invoice_file:
    uploaded_count += 1
    preview_file(invoice_file, "Invoice Run Pending Report")

if mrc_file:
    uploaded_count += 1
    preview_file(mrc_file, "MRC Report")


# =========================================================
# FILE READINESS CHECK
# =========================================================
def files_ready():
    if logic_name == "Logic 1 - Bill Frequency Mismatch":
        return subscription_file is not None

    if logic_name == "Logic 2 - Subscription vs Invoice Run Pending":
        return subscription_file is not None and invoice_file is not None

    if logic_name == "Logic 3 - Commercial Mismatch":
        return subscription_file is not None and mrc_file is not None

    if logic_name == "Logic 22 - Duplicate Validation":
        return mrc_file is not None

    return False


# =========================================================
# RUN SECTION
# =========================================================
st.divider()
st.subheader("Run Validation")

if files_ready():
    st.success("All required files are uploaded. You can run the validation.")
else:
    st.warning("Upload all required files to enable validation.")

run_button = st.button(
    "🚀 Run Validation",
    type="primary",
    disabled=not files_ready()
)


if run_button:
    with st.spinner("Running selected PBC validation..."):

        # Temporary professional output.
        # Later, we will connect your actual backend PBC logic here.
        output_df = pd.DataFrame({
            "Selected_Logic": [logic_name],
            "Run_Time": [datetime.now().strftime("%d-%m-%Y %H:%M:%S")],
            "Uploaded_Files_Count": [uploaded_count],
            "Validation_Status": ["Completed"]
        })

        output_file = "PBC_Output.xlsx"
        output_df.to_excel(output_file, index=False)

    st.success("Validation completed successfully.")

    with open(output_file, "rb") as file:
        st.download_button(
            label="⬇️ Download Output Excel",
            data=file,
            file_name="PBC_Output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


# =========================================================
# FOOTER
# =========================================================
st.divider()
st.markdown(
    '<div class="footer">DBCH PBC Automation Dashboard | Internal Validation Utility</div>',
    unsafe_allow_html=True
)
