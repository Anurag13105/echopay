import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000"

# 🔒 Check Admin Authentication
if "authenticated_admin" not in st.session_state or not st.session_state.authenticated_admin:
    st.error("❌ Access Denied. Please log in as an Admin.")
    st.stop()

# 🏠 Admin Dashboard Title
st.title("🛠️ Admin Dashboard - RFID Transactions")

# 🔓 Logout button
if st.button("Logout"):
    del st.session_state.authenticated_admin  # Clear session state
    st.switch_page("app.py")  # Redirect back to login page

# 📡 Fetch RFID List from API
rfid_list_response = requests.get(f"{API_URL}/rfid-list")

if rfid_list_response.status_code == 200:
    rfid_list = rfid_list_response.json()["rfids"]
else:
    st.error("⚠️ Failed to load RFID list from API.")
    rfid_list = []

# 🔄 Select RFID Dropdown
selected_rfid = st.selectbox("Select an RFID:", rfid_list)

# 🔍 Search RFID Manually
search_rfid = st.text_input("Or Search RFID:")
if search_rfid and search_rfid in rfid_list:
    selected_rfid = search_rfid

# 📜 Fetch Transactions from API
if st.button("Get Transactions"):
    if selected_rfid:
        transactions_response = requests.get(f"{API_URL}/transactions/{selected_rfid}")

        if transactions_response.status_code == 200:
            transactions = transactions_response.json()

            if transactions:
                st.write(f"### Transactions for RFID: {selected_rfid}")
                df = pd.DataFrame(transactions)
                st.dataframe(df)  # Display transactions in a table
            else:
                st.info("No transactions found for this RFID.")
        else:
            st.error(f"⚠️ API Error: {transactions_response.json()['detail']}")
    else:
        st.warning("Please select or enter a valid RFID.")
