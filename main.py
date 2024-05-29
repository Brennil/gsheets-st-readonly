import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from bs4 import BeautifulSoup
import pathlib
import shutil
import branding  # Import the branding module

# Google Analytics configuration
GA_ID = "google_analytics"
GA_SCRIPT = """
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-DKH2RC8PJ5"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-DKH2RC8PJ5');
</script>
"""

def inject_ga():
    index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
    soup = BeautifulSoup(index_path.read_text(), features="html.parser")
    if not soup.find(id=GA_ID):
        bck_index = index_path.with_suffix('.bck')
        if bck_index.exists():
            shutil.copy(bck_index, index_path)
        else:
            shutil.copy(index_path, bck_index)
        html = str(soup)
        new_html = html.replace('<head>', '<head>\n' + GA_SCRIPT)
        index_path.write_text(new_html)

inject_ga()

def authenticate_gsheets():
    creds_json = st.secrets["gspread"]["google_credentials"]
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(creds_json), scope)
    client = gspread.authorize(creds)
    return client

def get_order_items_by_email(email, sheet):
    worksheet = sheet.worksheet('Sheet1')
    records = worksheet.get_all_records()
    
    for record in records:
        if record['Email'] == email:
            return record['Order items'].replace('\\n', '\n')
    return "No record found for this email. Please try another email"

# Initialize Google Sheets client
client = authenticate_gsheets()
sheet = client.open('SST String Session Checker')

def main():
    branding.display_branding()
    email_input = st.text_input("Enter Email", "")

    if st.button("Check workshop venues"):
        order_items = get_order_items_by_email(email_input, sheet)
        if order_items:
            st.success(order_items)
        else:
            st.error("No items found for this email.")

if __name__ == "__main__":
    main()
    st.markdown('')
    st.markdown('Created by [String](https://go.gov.sg/stringme), code for this checker available [here](https://github.com/String-sg/gsheets-st-readonly)')
