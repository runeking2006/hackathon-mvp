import streamlit as st
import easyocr
import re
from PIL import Image, ImageDraw
import numpy as np
import json
import pandas as pd
from datetime import datetime
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Enterprise Document Intelligence", page_icon="📄", layout="wide")

st.title("Enterprise Document Intelligence")
st.markdown(
    "<p style='text-align: center;'>AI-powered OCR, entity extraction, validation, and secure enterprise document processing.</p>",
    unsafe_allow_html=True
)

# Inline CSS
st.markdown("""
<style>
.stApp {background-color: #f5f7fb;}
h1 {color: #1f4e79;text-align:center;}
h3 {color:#2c3e50;}
.stButton>button {
background-color:#1f77b4;
color:white;
border-radius:8px;
padding:8px 16px;
font-weight:bold;
}
.stButton>button:hover {background-color:#145a86;}
</style>
""", unsafe_allow_html=True)

# ---------------- OCR MODEL (CACHED) ----------------
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

reader = load_ocr()

# ---------------- STORAGE ----------------
DATA_FILE = "records.json"

def load_records():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_records(records):
    with open(DATA_FILE, "w") as f:
        json.dump(records, f, indent=4)

if "records" not in st.session_state:
    st.session_state.records = load_records()

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("Upload Document", type=["png","jpg","jpeg","pdf"])

if uploaded_file:

    # file size protection
    if uploaded_file.size > 5_000_000:
        st.error("File too large (>5MB)")
        st.stop()

    image = Image.open(uploaded_file)

    st.subheader("Uploaded Document Preview")
    st.image(image, use_container_width=True)

process = st.button("Process Document")

# ---------------- PROCESS ----------------
if uploaded_file and process:

    try:

        with st.spinner("Processing document with OCR..."):

            image = Image.open(uploaded_file)

            img_array = np.array(image)

            results = reader.readtext(img_array)

            text = "\n".join([res[1] for res in results])

            confidence_scores = [res[2] for res in results]
            avg_conf = sum(confidence_scores)/len(confidence_scores) if confidence_scores else 0

            st.subheader("OCR Confidence")
            st.progress(int(avg_conf*100))
            st.write(f"Average OCR Confidence: {round(avg_conf*100,2)}%")

            # ---------------- BOUNDING BOXES ----------------
            draw = ImageDraw.Draw(image)

            for (bbox, text_detected, prob) in results:
                p0,p1,p2,p3 = bbox
                draw.line([tuple(p0),tuple(p1),tuple(p2),tuple(p3),tuple(p0)], width=3)

            st.subheader("Detected Text Regions")
            st.image(image, use_container_width=True)

            # ---------------- DOCUMENT TYPE ----------------
            text_lower = text.lower()

            if any(k in text_lower for k in ["invoice","bill","receipt"]):
                doc_type="Invoice"
            elif any(k in text_lower for k in ["contract","agreement"]):
                doc_type="Contract"
            elif any(k in text_lower for k in ["form","application"]):
                doc_type="Form"
            elif any(k in text_lower for k in ["aadhaar","passport","identity","id"]):
                doc_type="ID Document"
            else:
                doc_type="Unknown"

            st.subheader("Document Type")
            st.success(doc_type)

            # ---------------- TEXT OUTPUT ----------------
            st.subheader("Extracted Text")
            st.text_area("Extracted Text", text, height=200)

            # ---------------- ENTITY EXTRACTION ----------------
            name = re.findall(r"(?:name|customer|client|buyer)[^\n:]*[:\s]*([A-Za-z ]+)", text, re.IGNORECASE)

            invoice_no = re.findall(r"(?:invoice|bill)[^\n]*?(?:no|number|#)?[:\s]*([A-Z0-9-]+)", text, re.IGNORECASE)

            amount = re.findall(r"(?:amount|total)[^\d]*([\d,]+)", text.lower())

            date = re.findall(r"\d{2}/\d{2}/\d{4}", text)

            phone = re.findall(r"\b\d{10}\b", text)

            email = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)

            aadhaar = re.findall(r"\b\d{4}\s?\d{4}\s?\d{4}\b", text)

            pan = re.findall(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", text)

            # ---------------- MASKING ----------------
            masked_phone = ["XXXXXX"+p[-4:] for p in phone]
            masked_aadhaar = ["XXXX XXXX "+a[-4:] for a in aadhaar]
            masked_pan = ["XXXXX"+p[-4:] for p in pan]

            # ---------------- VALIDATION ----------------
            validation_messages=[]

            if not amount:
                validation_messages.append("❌ Amount not detected")

            if date:
                try:
                    datetime.strptime(date[0], "%d/%m/%Y")
                except:
                    validation_messages.append("❌ Invalid date format")
            else:
                validation_messages.append("❌ Date not detected")

            if phone and len(phone[0])!=10:
                validation_messages.append("❌ Invalid phone number")

            st.subheader("Validation Results")

            if validation_messages:
                for msg in validation_messages:
                    st.warning(msg)
            else:
                st.success("All fields validated successfully")

            # ---------------- STRUCTURED DATA ----------------
            data={
                "timestamp":str(datetime.now()),
                "document_type":doc_type,
                "name":name,
                "invoice_number":invoice_no,
                "amount":[int(a.replace(",","")) for a in amount] if amount else [],
                "date":date,
                "phone_masked":masked_phone,
                "email":email,
                "aadhaar_masked":masked_aadhaar,
                "pan_masked":masked_pan,
                "ocr_confidence":round(avg_conf*100,2)
            }

            st.subheader("Structured Output")
            st.json(data)

            st.session_state.records.append(data)

            save_records(st.session_state.records)

            # ---------------- DOWNLOAD JSON ----------------
            json_data=json.dumps(data,indent=4)

            st.download_button(
                label="Download Structured Enterprise Record (JSON)",
                data=json_data,
                file_name="extracted_document.json",
                mime="application/json"
            )

    except Exception as e:
        st.error(f"OCR Processing Failed: {e}")

# ---------------- SEARCH ----------------
st.subheader("Search Processed Documents")

search=st.text_input("Search by Name or Document Type")

filtered_records=st.session_state.records

if search:
    filtered_records=[r for r in st.session_state.records if search.lower() in str(r).lower()]

if filtered_records:
    st.table(filtered_records)
else:
    st.info("No matching records found")

# ---------------- ANALYTICS ----------------
st.subheader("Document Analytics")

total_docs=len(st.session_state.records)

invoice_count=sum(1 for r in st.session_state.records if r["document_type"]=="Invoice")

st.metric("Total Documents Processed",total_docs)
st.metric("Invoices Detected",invoice_count)

# convert to dataframe
if st.session_state.records:

    df=pd.DataFrame(st.session_state.records)

    st.subheader("Document Type Distribution")
    st.bar_chart(df["document_type"].value_counts())

    st.subheader("OCR Confidence Trend")
    st.line_chart(df["ocr_confidence"])

    # CSV Export
    csv=df.to_csv(index=False)

    st.download_button(
        "Download All Records CSV",
        csv,
        "enterprise_records.csv",
        "text/csv"
    )