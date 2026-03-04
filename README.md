# Enterprise Document Intelligence & Secure Data Extraction Platform

## Overview

This project demonstrates an AI-powered system that automatically processes scanned enterprise documents such as invoices, contracts, and forms. The system extracts important information from uploaded documents using OCR and converts it into structured data.

The platform reduces manual effort, improves accuracy, and protects sensitive information through automated validation and masking techniques.

## Features

* OCR-based text extraction from scanned documents
* Automatic document classification (Invoice, Contract, Form, ID Document)
* Key information extraction (Name, Amount, Date, Invoice Number, Phone Number)
* Sensitive data masking for privacy protection
* Validation of extracted data using predefined rules
* Structured JSON output for easy storage and integration
* Downloadable structured records
* Searchable dashboard for processed documents
* Simple analytics showing processed document statistics

## Technologies Used

* Python
* Streamlit
* EasyOCR
* NumPy
* Pillow (PIL)
* Regular Expressions (Regex)

## Installation

1. Clone the repository

```
git clone <your-repository-link>
cd <repository-folder>
```

2. Install required dependencies

```
pip install -r requirements.txt
```

3. Run the application

```
streamlit run app.py
```

## Usage

1. Upload a scanned document (PNG, JPG, or JPEG).
2. Click **Process Document**.
3. The system performs OCR and extracts relevant data.
4. Extracted fields are validated and sensitive information is masked.
5. The structured data is displayed and can be downloaded as a JSON file.
6. Processed documents can be searched through the dashboard.

## Project Workflow

1. Document Upload
2. OCR Text Extraction
3. Document Classification
4. Entity Extraction
5. Data Validation
6. Sensitive Data Masking
7. Structured JSON Generation
8. Dashboard Monitoring & Search

## Applications

* Invoice processing automation
* Document digitization
* Enterprise document management
* Secure data extraction from scanned records
