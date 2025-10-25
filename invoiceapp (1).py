#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import pdfplumber
import re
import pandas as pd

# --- Functions ---
def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_invoice_data(text):
    invoice_data = {}

    # Extract main fields
    invoice_data['Bill To'] = re.search(r'Bill To:\s*(.+)', text)
    invoice_data['Date'] = re.search(r'Date:\s*(.+)', text)
    invoice_data['Payment Terms'] = re.search(r'Payment Terms:\s*(.+)', text)
    invoice_data['Due Date'] = re.search(r'Due Date:\s*(.+)', text)
    invoice_data['PO Number'] = re.search(r'PO Number:\s*(.+)', text)
    invoice_data['Balance Due'] = re.search(r'Balance Due:\s*₹?([\d,\.]+)', text)

    # Process matches
    for key, match in invoice_data.items():
        invoice_data[key] = match.group(1).strip() if match else None

    # Extract line items
    items_pattern = re.findall(r'(.+?)\s+(\d+)\s+₹([\d,\.]+)\s+₹([\d,\.]+)', text)
    items = []
    for item in items_pattern:
        items.append({
            'Item': item[0].strip(),
            'Quantity': int(item[1]),
            'Rate': float(item[2].replace(',', '')),
            'Amount': float(item[3].replace(',', ''))
        })

    invoice_data['Items'] = items
    return invoice_data

# --- Streamlit UI ---
st.title("PDF Invoice Extraction")

uploaded_file = st.file_uploader("Upload a PDF invoice", type="pdf")

if uploaded_file is not None:
    text = extract_text_from_pdf(uploaded_file)
    data = extract_invoice_data(text)
    
    st.subheader("Invoice Details")
    main_fields = {k: v for k, v in data.items() if k != 'Items'}
    st.json(main_fields)

    if data['Items']:
        st.subheader("Line Items")
        df_items = pd.DataFrame(data['Items'])
        st.table(df_items)

        # CSV download
        csv = df_items.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Items as CSV",
            data=csv,
            file_name='invoice_items.csv',
            mime='text/csv'
        )

    # Optional: raw PDF text for debugging
    with st.expander("Show raw PDF text"):
        st.text(text)

