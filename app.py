import streamlit as st
import easyocr
import re
from PIL import Image, ImageDraw, ImageOps
import numpy as np
import json
import pandas as pd
from datetime import datetime
import os
import time
import statistics

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Enterprise Document Intelligence", page_icon="📄", layout="wide")

st.title("Enterprise Document Intelligence")
st.markdown(
"<p style='text-align: center;'>AI-powered OCR, entity extraction, validation, and secure enterprise document processing.</p>",
unsafe_allow_html=True
)

# ---------------- CSS ----------------
st.markdown("""
<style>
.stApp {background-color:#f5f7fb;}
h1 {color:#1f4e79;text-align:center;}
.stButton>button{
background-color:#1f77b4;
color:white;
border-radius:8px;
padding:8px 16px;
font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

# ---------------- OCR MODEL ----------------
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'], gpu=False)

reader = load_ocr()

# ---------------- STORAGE ----------------
DATA_FILE = "records.json"

def load_records():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE,"r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_records(records):
    tmp="records_tmp.json"
    with open(tmp,"w") as f:
        json.dump(records,f,indent=4)
    os.replace(tmp,DATA_FILE)

if "records" not in st.session_state:
    st.session_state.records=load_records()

# ---------------- UPLOAD ----------------
uploaded_files = st.file_uploader(
"Upload Documents",
type=["png","jpg","jpeg"],
accept_multiple_files=True
)

process = st.button("Process Documents")

# ---------------- OCR PROCESS ----------------
if uploaded_files and process:

    for uploaded_file in uploaded_files:

        start=time.time()

        col1,col2 = st.columns([1,1])

        with col1:

            image = Image.open(uploaded_file)

            # auto orientation
            image = ImageOps.exif_transpose(image)

            # preprocessing
            gray = image.convert("L")
            img_array = np.array(gray)

            st.subheader("Document Preview")
            st.image(image,use_container_width=True)

        with st.spinner("Running OCR..."):

            results = reader.readtext(img_array)

        text="\n".join([r[1] for r in results])

        confidences=[r[2] for r in results]

        avg_conf = statistics.mean(confidences) if confidences else 0
        median_conf = statistics.median(confidences) if confidences else 0

        with col2:

            st.subheader("OCR Metrics")

            st.metric("Average Confidence",round(avg_conf*100,2))
            st.metric("Median Confidence",round(median_conf*100,2))

            if confidences:
                st.bar_chart(pd.DataFrame(confidences,columns=["confidence"]))

        # ---------------- BOUNDING BOXES ----------------
        draw = ImageDraw.Draw(image)

        for (bbox,text_detected,prob) in results:

            p0,p1,p2,p3=bbox

            draw.line([tuple(p0),tuple(p1),tuple(p2),tuple(p3),tuple(p0)],width=3)

            draw.text(tuple(p0),f"{text_detected} ({round(prob*100)}%)")

        st.subheader("Detected Text Regions")
        st.image(image,use_container_width=True)

        # ---------------- CLASSIFICATION ----------------
        text_lower=text.lower()

        scores={
        "Invoice":0,
        "Contract":0,
        "Form":0,
        "ID Document":0
        }

        invoice_words=["invoice","bill","receipt","total"]
        contract_words=["agreement","contract","terms"]
        form_words=["application","form","submit"]
        id_words=["aadhaar","passport","identity"]

        for w in invoice_words:
            if w in text_lower: scores["Invoice"]+=1

        for w in contract_words:
            if w in text_lower: scores["Contract"]+=1

        for w in form_words:
            if w in text_lower: scores["Form"]+=1

        for w in id_words:
            if w in text_lower: scores["ID Document"]+=1

        doc_type=max(scores,key=scores.get)

        st.subheader("Document Type")
        st.success(doc_type)

        # ---------------- ENTITY EXTRACTION ----------------
        name=re.findall(r"(?:name|customer|client|buyer|ship to|bill to|vendor)[^\n:]*[:\s]*([A-Za-z ]+)",text,re.I)

        invoice_no=re.findall(r"(?:invoice|bill)[^\n]*?(?:no|number|#)?[:\s]*([A-Z0-9-]+)",text,re.I)

        amount=re.findall(r"(?:₹|\$|INR)?\s?([\d,]+\.\d+|[\d,]+)",text)

        date=re.findall(r"\d{2}[/-]\d{2}[/-]\d{4}|\d{4}[/-]\d{2}[/-]\d{2}",text)

        phone=re.findall(r"\+?\d[\d -]{8,12}\d",text)

        email=re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",text)

        aadhaar=re.findall(r"\b\d{4}\s?\d{4}\s?\d{4}\b",text)

        pan=re.findall(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",text)

        # ---------------- MASKING ----------------
        masked_phone=["XXXXXX"+p[-4:] for p in phone]

        masked_email=[e[0:3]+"***@"+e.split("@")[1] for e in email]

        masked_aadhaar=["XXXX XXXX "+a[-4:] for a in aadhaar]

        masked_pan=["XXXXX"+p[-4:] for p in pan]

        # ---------------- STRUCTURED DATA ----------------
        data={
        "timestamp":str(datetime.now()),
        "document_type":doc_type,
        "name":name,
        "invoice_number":invoice_no,
        "amount":[float(a.replace(",","")) for a in amount] if amount else [],
        "date":date,
        "phone_masked":masked_phone,
        "email_masked":masked_email,
        "aadhaar_masked":masked_aadhaar,
        "pan_masked":masked_pan,
        "ocr_confidence":round(avg_conf*100,2)
        }

        # duplicate prevention
        existing=[r.get("invoice_number") for r in st.session_state.records]

        if data["invoice_number"] not in existing:
            st.session_state.records.append(data)
            save_records(st.session_state.records)

        st.subheader("Structured Output")
        st.json(data)

        # processing time
        end=time.time()
        st.info(f"Processing Time: {round(end-start,2)} sec")

# ---------------- SEARCH ----------------
st.subheader("Search Documents")

query=st.text_input("Search by name, invoice, or type")

filtered=st.session_state.records

if query:

    filtered=[
    r for r in st.session_state.records
    if query.lower() in str(r.get("name","")).lower()
    or query.lower() in str(r.get("invoice_number","")).lower()
    or query.lower() in str(r.get("document_type","")).lower()
    ]

# pagination
page_size=10
page=st.number_input("Page",1,max(1,len(filtered)//page_size+1),1)

start=(page-1)*page_size
end=start+page_size

st.table(filtered[start:end])

# ---------------- ANALYTICS ----------------
st.subheader("Analytics")

records=st.session_state.records

if records:

    df=pd.DataFrame(records)

    st.metric("Total Documents",len(df))

    st.metric("Average OCR Confidence",round(df["ocr_confidence"].mean(),2))

    if "document_type" in df:
        st.bar_chart(df["document_type"].value_counts())

    if "ocr_confidence" in df:
        st.line_chart(df["ocr_confidence"])

    if "amount" in df:
        amounts=[sum(a) if isinstance(a,list) else 0 for a in df["amount"]]
        st.metric("Total Amount Extracted",sum(amounts))

    csv=df.to_csv(index=False)

    st.download_button(
    "Download All Records CSV",
    csv,
    "enterprise_records.csv",
    "text/csv"
    )