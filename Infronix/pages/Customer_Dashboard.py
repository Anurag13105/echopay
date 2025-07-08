import streamlit as st
import requests

API_URL = "http://localhost:8000"

if "authenticated_user" not in st.session_state:
    st.error("❌ Access Denied. Please log in as a Customer.")
    st.stop()

rfid = st.session_state.authenticated_user

st.title("🎟️ Customer Dashboard")

# Logout button
if st.button("Logout"):
    del st.session_state.authenticated_user
    st.switch_page("app.py")

# Fetch customer details
response = requests.get(f"{API_URL}/rfid/{rfid}")

if response.status_code == 200:
    user_data = response.json()
    st.success("✅ Login Successful!")
    
    st.markdown(f"""
        <div style="text-align: center; padding: 20px; background-color: black; color: white; border-radius: 10px;">
            <h3>🎟️ RFID: {rfid}</h3>
            <p><b>💰 Balance:</b> {user_data['balance']} </p>
            <p><b>🔄 Linked ESPID:</b> {user_data['esp_id']} </p>
        </div>
    """, unsafe_allow_html=True)

    # Fetch transactions
    transactions_response = requests.get(f"{API_URL}/transactions/{rfid}")
    
    st.subheader("📜 Transaction History")
    if transactions_response.status_code == 200:
        transactions = transactions_response.json()
        for t in transactions:
            st.write(f"🔹 **ESP ID:** {t['esp_id']} | **Amount:** {t['amount']}")
    else:
        st.warning("No transactions found.")
else:
    st.error("RFID details not found.")

