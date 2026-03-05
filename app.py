import streamlit as st
import easyocr
import re
from PIL import Image
import numpy as np
import json
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Enterprise Document Intelligence", page_icon="📄", layout="wide")


st.title("Enterprise Document Intelligence")
st.caption("AI-powered OCR, entity extraction, validation, and secure enterprise document processing.")

st.markdown(
    """
    <meta name="google-site-verification" content="abc123xyz" />
    """,
    unsafe_allow_html=True
)

# Inline CSS(cascading styles sheet)
st.markdown("""
<style>

/* Main background */
.stApp {
    background-color: #f5f7fb;
}

/* Title styling */
h1 {
    color: #1f4e79;
    text-align: center;
}

/* Subheaders */
h3 {
    color: #2c3e50;
}

/* Buttons */
.stButton>button {
    background-color: #1f77b4;
    color: white;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: bold;
}

.stButton>button:hover {
    background-color: #145a86;
}

/* Metrics box */
[data-testid="stMetricValue"] {
    font-size: 28px;
    color: #1f4e79;
}

/* JSON output box */
.css-1d391kg {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)
# Store processed documents
if "records" not in st.session_state:
    st.session_state.records = []

uploaded_file = st.file_uploader("Upload Document", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)

    st.subheader("Uploaded Document Preview")
    st.image(image, use_container_width=True)

process = st.button("Process Document")

if uploaded_file is not None and process:

    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Document", use_container_width=True)

    # Initialize EasyOCR
    reader = easyocr.Reader(['en'])

    # Convert image to numpy array
    img_array = np.array(image)

    # OCR
    results = reader.readtext(img_array)

    # Combine detected text
    text = "\n".join([res[1] for res in results])

    # OCR Confidence
    confidence_scores = [res[2] for res in results]
    avg_conf = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0

    st.subheader("OCR Confidence")
    st.progress(avg_conf)
    st.write(f"Average OCR Confidence: {round(avg_conf*100,2)}%")

    # Highlight detected fields
    st.subheader("Detected Fields")
    for (bbox, text_detected, prob) in results:
        if any(k in text_detected.lower() for k in ["name", "amount", "date"]):
            st.write(f"🔍 {text_detected}")

    # Document classification
    text_lower = text.lower()
    if "invoice" in text_lower:
        doc_type = "Invoice"
    elif "contract" in text_lower:
        doc_type = "Contract"
    elif "form" in text_lower:
        doc_type = "Form"
    elif "aadhaar" in text_lower or "id" in text_lower:
        doc_type = "ID Document"
    else:
        doc_type = "Unknown"

    st.subheader("Extracted Text")
    st.text_area("Extracted Text", text, height=200)

    # Entity extraction
    name = re.findall(r"Name[:\s]*([A-Za-z ]+)", text)
    invoice_no_matches = re.findall(r"Invoice\s*(?:No|Number)?[:\s]*([0-9]+)", text)
    invoice_no = invoice_no_matches
    amount = re.findall(r"Amount[:\s]*([0-9]+)", text)
    date = re.findall(r"\d{2}/\d{2}/\d{4}", text)
    phone = re.findall(r"\d{10}", text)

    st.subheader("Document Type")
    st.success(doc_type)

    # Mask phone numbers
    masked_phone = ["XXXXXX" + p[-4:] for p in phone]

    # Validation Rules
    validation_messages = []

    if amount:
        if not amount[0].isdigit():
            validation_messages.append("❌ Invalid amount format")
    else:
        validation_messages.append("❌ Amount not detected")

    if date:
        try:
            datetime.strptime(date[0], "%d/%m/%Y")
        except:
            validation_messages.append("❌ Invalid date format")
    else:
        validation_messages.append("❌ Date not detected")

    if phone:
        if len(phone[0]) != 10:
            validation_messages.append("❌ Invalid phone number")
    else:
        validation_messages.append("❌ Phone number not detected")

    st.subheader("Validation Results")

    if validation_messages:
        for msg in validation_messages:
            st.warning(msg)
    else:
        st.success("All fields validated successfully")

    data = {
        "document_type": doc_type,
        "name": name,
        "invoice_number": invoice_no,
        "amount": amount,
        "date": date,
        "phone_masked": masked_phone
    }

    # Save record
    st.session_state.records.append(data)

    st.subheader("Structured Output")
    st.json(data)

    # Convert dictionary to JSON string
    json_data = json.dumps(data, indent=4)

    # Download button
    st.download_button(
        label="Download Structured Enterprise Record (JSON)",
        data=json_data,
        file_name="extracted_document.json",
        mime="application/json"
    )

# Searchable dashboard
st.subheader("Search Processed Documents")

search = st.text_input("Search by Name or Document Type")

filtered_records = st.session_state.records

if search:
    filtered_records = [
        r for r in st.session_state.records
        if search.lower() in str(r).lower()
    ]

if filtered_records:
    st.table(filtered_records)
else:
    st.info("No matching records found")

# Analytics Dashboard
st.subheader("Document Analytics")

total_docs = len(st.session_state.records)
invoice_count = sum(1 for r in st.session_state.records if r["document_type"] == "Invoice")

st.metric("Total Documents Processed", total_docs)
st.metric("Invoices Detected", invoice_count)
