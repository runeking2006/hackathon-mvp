# Enterprise Document Intelligence & Secure Data Extraction Platform

## Overview

Enterprise organizations handle large volumes of documents such as invoices, contracts, forms, and identity records. Manual extraction of information from these documents is slow, error-prone, and can expose sensitive data.

This project demonstrates an **AI-powered document processing platform** that automatically extracts structured information from scanned documents using Optical Character Recognition (OCR).

The system analyzes uploaded documents, extracts key entities, validates the extracted information, masks sensitive data, and converts the results into structured records that can be downloaded as **CSV files**.

---

## Key Features

* OCR-based text extraction from scanned documents
* Automatic document classification

  * Invoice
  * Contract
  * Form
  * ID Document
* Entity extraction from documents:

  * Name
  * Invoice Number
  * Amount
  * Date
  * Phone Number
  * Email
* Sensitive data masking for privacy protection
* Rule-based validation of extracted data
* Downloadable structured **CSV records**
* Searchable dashboard for processed documents
* Analytics showing document statistics and OCR confidence

---

## Technologies Used

* **Python**
* **Streamlit** – Interactive web interface
* **EasyOCR** – Optical Character Recognition
* **NumPy** – Image data processing
* **Pillow (PIL)** – Image handling
* **Pandas** – Data analysis and CSV generation
* **Regular Expressions (Regex)** – Entity extraction

---

## Installation

### 1. Clone the repository

```
git clone <your-repository-link>
cd <repository-folder>
```

### 2. Install dependencies

```
pip install -r requirements.txt
```

### 3. Run the application

```
streamlit run app.py
```

---

## Usage

1. Upload a scanned document (PNG, JPG, or JPEG).
2. Click **Process Documents**.
3. The system performs OCR and extracts text from the document.
4. Key fields such as name, amount, and invoice number are automatically detected.
5. Sensitive information is masked for security.
6. Extracted records appear in the dashboard.
7. Processed data can be downloaded as a **CSV file**.

---

## Project Workflow

1. Document Upload
2. Image Preprocessing
3. OCR Text Extraction
4. Document Classification
5. Entity Extraction
6. Data Validation
7. Sensitive Data Masking
8. Structured Data Generation (CSV)
9. Dashboard Monitoring & Search

---

## Applications

* Automated invoice processing
* Document digitization and archiving
* Enterprise document management systems
* Secure data extraction from scanned documents
* Business process automation

---

## Live Demo

Try the application here:

https://runeking2006-hackathon-mvp-app-sjbwov.streamlit.app/
