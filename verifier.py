import sqlite3
from datetime import datetime

# Auto-initialize the history table so you don't have to rebuild your database
def init_history_db():
    conn = sqlite3.connect('medverify_reference.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS verification_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME,
        batch_number TEXT,
        medicine_name TEXT,
        manufacturer TEXT,
        status TEXT,
        risk_score INTEGER
    )
    ''')
    conn.commit()
    conn.close()

# Run initialization immediately when imported
init_history_db()

def log_verification(batch, name, mfg, status, score):
    conn = sqlite3.connect('medverify_reference.db')
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
    INSERT INTO verification_history (timestamp, batch_number, medicine_name, manufacturer, status, risk_score)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (timestamp, batch, name, mfg, status, score))
    conn.commit()
    conn.close()

def get_dashboard_stats():
    """Fetches real application data for the dashboard."""
    conn = sqlite3.connect('medverify_reference.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM verification_history")
    total = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as authentic FROM verification_history WHERE status LIKE '%VERIFIED%' OR status LIKE '%Match%'")
    authentic = cursor.fetchone()['authentic']
    
    cursor.execute("SELECT COUNT(*) as suspicious FROM verification_history WHERE status LIKE '%SUSPICIOUS%'")
    suspicious = cursor.fetchone()['suspicious']
    
    cursor.execute("SELECT COUNT(*) as fake FROM verification_history WHERE status LIKE '%HIGH RISK%' OR status LIKE '%Not Found%'")
    fake = cursor.fetchone()['fake']
    
    cursor.execute("SELECT * FROM verification_history ORDER BY timestamp DESC LIMIT 10")
    recent = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return total, authentic, suspicious, fake, recent

def verify_medicine(batch_number, medicine_name, manufacturer, mfg_date, exp_date, entered_mrp=None):
    conn = sqlite3.connect('medverify_reference.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM authentic_batches WHERE batch_number = ?", (batch_number.strip(),))
    record = cursor.fetchone()
    conn.close()

    flags = []
    
    # Check 1: Existence
    if not record:
        result = {
            "status": "Information Not Found",
            "score": 100,
            "badge": "🔴",
            "reasons": ["Batch number not found in official manufacturer records.", 
                        "Cannot authenticate this product based on provided data."]
        }
        log_verification(batch_number, medicine_name, manufacturer, result['status'], result['score'])
        return result
    
    # Check 2: Medicine Name Match
    if medicine_name.strip().lower() != record['medicine_name'].lower():
        flags.append(f"Name mismatch: Expected '{record['medicine_name']}', entered '{medicine_name}'.")

    # Check 3: Manufacturer Match
    if manufacturer.strip().lower() != record['manufacturer'].lower():
        flags.append(f"Manufacturer mismatch: Expected '{record['manufacturer']}'.")

    # Check 4: Date Consistency
    try:
        mfg_dt_input = datetime.strptime(mfg_date, "%Y-%m")
        exp_dt_input = datetime.strptime(exp_date, "%Y-%m")
        
        if exp_dt_input <= mfg_dt_input:
            flags.append("Invalid dates: Expiry date cannot be earlier than manufacturing date.")
            
        if exp_date != record['exp_date']:
            flags.append(f"Altered expiry date: Official record is {record['exp_date']}, entered was {exp_date}.")
            
        current_date = datetime.now()
        if current_date > datetime.strptime(record['exp_date'], "%Y-%m"):
            flags.append("Expired stock: According to official records, this batch has already expired.")
            
    except ValueError:
        flags.append("Invalid date format. Use YYYY-MM.")

    # Rupee (₹) Price Check
    if entered_mrp is not None and entered_mrp > 0:
        official_mrp = record['mrp']
        if entered_mrp < (official_mrp * 0.70):
            flags.append(f"Price anomaly: Price (₹{entered_mrp:.2f}) is over 30% below official MRP (₹{official_mrp:.2f}).")
        elif entered_mrp > (official_mrp * 1.30):
            flags.append(f"Price anomaly: Price (₹{entered_mrp:.2f}) is significantly higher than official MRP (₹{official_mrp:.2f}).")

    if not flags:
        result = {
            "status": "Match Found (Verified)", 
            "score": 0, 
            "badge": "🟢",
            "reasons": ["All packaging metadata and pricing match official records."]
        }
    else:
        calculated_score = min(100, len(flags) * 35)
        result = {
            "status": "Suspicious / Mismatch", 
            "score": calculated_score, 
            "badge": "🟡",
            "reasons": flags
        }
        
    log_verification(batch_number, medicine_name, manufacturer, result['status'], result['score'])
    return result