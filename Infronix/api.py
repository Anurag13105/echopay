from fastapi import FastAPI, HTTPException
import sqlite3
from pydantic import BaseModel
from typing import List

# Initialize FastAPI app
app = FastAPI()

DB_PATH = "./Database.db"

# ---------- Database Connection ----------
def get_db():
    """Establish a database connection with dictionary-like row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enables access via column names
    return conn

# ---------- Request Models ----------
class UserAuthRequest(BaseModel):
    rfid: str
    password: str

class AdminAuthRequest(BaseModel):
    username: str
    password: str

class TransactionResponse(BaseModel):
    rfid: str
    esp_id: str
    amount: int  # Matches INTEGER type from database
    
class UpdateRFIDRequest(BaseModel):
    rfid: str
    espid: str
    transaction_amount: int


# ---------- API Endpoints ----------

@app.get("/")
def home():
    return {"message": "Welcome to the RFID API"}

# ✅ Authenticate Customer
@app.post("/authenticate/customer")
def authenticate_customer(request: UserAuthRequest):
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT Password FROM UserAuth WHERE RFID = ?", (request.rfid,))
        user = cursor.fetchone()

        if user and user["Password"] == request.password:  # Fetch password from dictionary row
            return {"status": "success", "message": "Login successful"}
        raise HTTPException(status_code=401, detail="Invalid RFID or Password")
    
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    
    finally:
        conn.close()

# ✅ Authenticate Admin
@app.post("/authenticate/admin")
def authenticate_admin(request: AdminAuthRequest):
    if request.username == "admin" and request.password == "admin":
        return {"status": "success", "message": "Admin login successful"}
    raise HTTPException(status_code=401, detail="Invalid Admin Credentials")

# ✅ Fetch RFID Details
@app.get("/rfid/{rfid}")
def get_rfid_details(rfid: str):
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT Balance, ESPID FROM RFIDTable WHERE RFID = ?", (rfid,))
        result = cursor.fetchone()

        if result:
            return {"rfid": rfid, "balance": result["Balance"], "esp_id": result["ESPID"]}  # Access columns by name
        raise HTTPException(status_code=404, detail="RFID not found")
    
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    
    finally:
        conn.close()

# ✅ Fetch Transactions for RFID
@app.get("/transactions/{rfid}", response_model=List[TransactionResponse])
def get_transactions(rfid: str):
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Ensure correct column names
        cursor.execute("SELECT RFID, ESPID, TransactionAmt FROM ESPNumber WHERE RFID = ?", (rfid,))
        transactions = cursor.fetchall()

        if transactions:
            return [
                {"rfid": t["RFID"], "esp_id": t["ESPID"], "amount": t["TransactionAmt"]} 
                for t in transactions
            ]
        raise HTTPException(status_code=404, detail="No transactions found")
    
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    
    finally:
        conn.close()

# ✅ Fetch All Unique RFIDs
@app.get("/rfid-list")
def get_rfid_list():
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT DISTINCT RFID FROM RFIDTable")
        rfids = [row["RFID"] for row in cursor.fetchall()]  # Extract RFID values
        return {"rfids": rfids}
    
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    
    finally:
        conn.close()
        
@app.get("/balance/{rfid}")
def get_balance(rfid: str):
    conn = get_db()
    cursor = conn.cursor()
    print(rfid)
    try:
        # Query to fetch balance from RFIDTable
        cursor.execute("SELECT Balance FROM RFIDTable WHERE RFID = ?", (rfid,))
        result = cursor.fetchone()

        if result:
            return {
                "rfid": rfid,
                "balance": result[0]  # Extract balance from the tuple
            }
        else:
            raise HTTPException(status_code=404, detail="RFID not found")

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    finally:
        conn.close()
        
@app.put("/update-rfid")
def update_rfid(request: UpdateRFIDRequest):
    conn = get_db()
    cursor = conn.cursor()

    try:
        # Check if RFID exists
        cursor.execute("SELECT * FROM RFIDTable WHERE RFID = ?", (request.rfid,))
        existing_entry = cursor.fetchone()

        if existing_entry:
            # Update RFIDTable
            cursor.execute(
                "UPDATE RFIDTable SET ESPID = ?, `Transaction Amount` = ? WHERE RFID = ?",
                (request.espid, request.transaction_amount, request.rfid),
            )
            
            # Update ESPNumber Table
            cursor.execute(
                "UPDATE ESPNumber SET ESPID = ?, TransactionAmt = ? WHERE RFID = ?",
                (request.espid, request.transaction_amount, request.rfid),
            )

            conn.commit()
            return {"status": "success", "message": "RFID details updated successfully"}

        else:
            raise HTTPException(status_code=404, detail="RFID not found in the database")

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    finally:
        conn.close()

@app.get("/transaction-amount/{espid}/{rfid}")
def get_transaction_amount(espid: str, rfid: str):
    conn = get_db()
    cursor = conn.cursor()

    try:
        # Query to fetch the transaction amount where both ESPID and RFID match
        cursor.execute("SELECT TransactionAmt FROM ESPNumber WHERE ESPID = ? AND RFID = ?", (espid, rfid))
        result = cursor.fetchone()

        if result:
            return {
                "espid": espid,
                "rfid": rfid,
                "transaction_amount": result[0]  # Extract the transaction amount
            }
        else:
            raise HTTPException(status_code=404, detail="No transaction amount found for the given ESPID and RFID")

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    finally:
        conn.close()
