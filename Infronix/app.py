import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="RFID Access System", page_icon="🔑", layout="centered")

st.title("🔑 RFID Access System")

page = st.sidebar.radio("Select Role", ["Customer Login", "Admin Login"])

if page == "Customer Login":
    st.subheader("🎟️ Customer Login")
    rfid = st.text_input("Enter RFID")
    password = st.text_input("Enter Password", type="password")
    
    if st.button("Login"):
        response = requests.post(f"{API_URL}/authenticate/customer", json={"rfid": rfid, "password": password})
        
        if response.status_code == 200:
            st.session_state.authenticated_user = rfid
            st.switch_page("pages/Customer_Dashboard.py")
        else:
            st.error("❌ Invalid RFID or Password.")

elif page == "Admin Login":
    st.subheader("🛠️ Admin Login")
    username = st.text_input("Enter Admin Username")
    password = st.text_input("Enter Password", type="password")
    
    if st.button("Login"):
        response = requests.post(f"{API_URL}/authenticate/admin", json={"username": username, "password": password})
        
        if response.status_code == 200:
            st.session_state.authenticated_admin = True
            st.switch_page("pages/Admin_Dashboard.py")
        else:
            st.error("❌ Invalid Admin Credentials.")
