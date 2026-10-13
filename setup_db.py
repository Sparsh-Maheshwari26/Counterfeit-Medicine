import sqlite3
from datetime import datetime, timedelta

def setup_database():
    conn = sqlite3.connect('medverify_reference.db')
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS authentic_batches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine_name TEXT NOT NULL,
        active_ingredient TEXT NOT NULL,
        strength TEXT NOT NULL,
        manufacturer TEXT NOT NULL,
        batch_number TEXT UNIQUE NOT NULL,
        mfg_date TEXT NOT NULL,
        exp_date TEXT NOT NULL,
        mrp REAL NOT NULL
    )
    ''')
    
    # FIX: Clear existing data AND reset the AUTOINCREMENT sequence to 1
    cursor.execute('DELETE FROM authentic_batches')
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='authentic_batches'")

    # Base list of 50 realistic Indian medicines across 10 categories
    base_medicines = [
        # Pain & Fever
        ("Dolo 650", "Paracetamol", "650mg", "Micro Labs Ltd", 33.00),
        ("Calpol 500", "Paracetamol", "500mg", "GSK India", 17.50),
        ("Combiflam", "Ibuprofen + Paracetamol", "400mg/325mg", "Sanofi India", 45.00),
        ("Zerodol-SP", "Aceclofenac + Paracetamol", "100mg/325mg", "Ipca Labs", 115.00),
        ("Crocin Advance", "Paracetamol", "500mg", "GSK India", 20.00),
        
        # Antibiotics
        ("Augmentin 625 Duo", "Amoxicillin + Clavulanic Acid", "625mg", "GSK India", 204.50),
        ("Azithral 500", "Azithromycin", "500mg", "Alembic Pharma", 132.00),
        ("Taxim-O 200", "Cefixime", "200mg", "Alkem Labs", 108.00),
        ("Monocef-O", "Cefpodoxime", "200mg", "Aristo Pharma", 165.00),
        ("Novamox 500", "Amoxicillin", "500mg", "Cipla Ltd", 75.00),
        
        # Antacids & Digestion
        ("Pan 40", "Pantoprazole", "40mg", "Alkem Labs", 155.00),
        ("Pantocid DSR", "Pantoprazole + Domperidone", "40mg/30mg", "Sun Pharma", 210.00),
        ("Gelusil MPS", "Aluminium Hydroxide + Magnesia", "200ml", "Pfizer India", 125.00),
        ("Digene", "Magnesium Hydroxide", "200ml", "Abbott India", 140.00),
        ("Omee", "Omeprazole", "20mg", "Alkem Labs", 58.00),
        
        # Allergy Relief
        ("Allegra 120", "Fexofenadine", "120mg", "Sanofi India", 218.00),
        ("Cetirizine 10mg", "Cetirizine", "10mg", "Cipla Ltd", 18.00),
        ("Montair LC", "Montelukast + Levocetirizine", "10mg/5mg", "Cipla Ltd", 185.00),
        ("Levocet M", "Levocetirizine", "5mg", "Mankind Pharma", 65.00),
        ("Avil 25", "Pheniramine Maleate", "25mg", "Sanofi India", 12.00),
        
        # Diabetes
        ("Glycomet 500", "Metformin", "500mg", "USV Pvt Ltd", 24.00),
        ("Galvus Met", "Vildagliptin + Metformin", "50mg/500mg", "Novartis", 280.00),
        ("Janumet", "Sitagliptin + Metformin", "50mg/500mg", "MSD Pharma", 310.00),
        ("Trivolibo", "Voglibose", "0.2mg", "Sun Pharma", 145.00),
        ("Amaryl 1M", "Glimepiride + Metformin", "1mg/500mg", "Sanofi India", 195.00),
        
        # Blood Pressure & Cardio
        ("Telmikind 40", "Telmisartan", "40mg", "Mankind Pharma", 56.00),
        ("Amlokind 5", "Amlodipine", "5mg", "Mankind Pharma", 28.00),
        ("Ecosprin 75", "Aspirin", "75mg", "USV Pvt Ltd", 5.50),
        ("Rosuvas 10", "Rosuvastatin", "10mg", "Sun Pharma", 180.00),
        ("Atorva 20", "Atorvastatin", "20mg", "Zydus Cadila", 112.00),
        
        # Vitamins & Supplements
        ("Shelcal 500", "Calcium + Vitamin D3", "500mg", "Torrent Pharma", 119.50),
        ("Zincovit", "Multivitamins + Zinc", "Tablet", "Apex Labs", 105.00),
        ("Supradyn", "Multivitamin Minerals", "Tablet", "Bayer Pharma", 55.00),
        ("Limcee 500", "Vitamin C", "500mg", "Abbott India", 25.00),
        ("Neurobion Forte", "Vitamin B Complex", "Tablet", "P&G Health", 38.00),
        
        # Cough & Cold
        ("Ascoril LS", "Ambroxol + Levosalbutamol", "100ml", "Glenmark", 118.00),
        ("Benadryl DR", "Diphenhydramine", "150ml", "J&J India", 145.00),
        ("Corex DX", "Dextromethorphan", "100ml", "Pfizer India", 125.00),
        ("Cheston Cold", "Cetirizine + Paracetamol", "Tablet", "Cipla Ltd", 45.00),
        ("Sinarest", "Chlorpheniramine + Paracetamol", "Tablet", "Centaur Pharma", 65.00),
        
        # Skin & Topical
        ("Betadine 10%", "Povidone Iodine", "Ointment", "Win-Medicare", 150.00),
        ("Soframycin", "Framycetin", "Cream", "Sanofi India", 55.00),
        ("Candid-B", "Clotrimazole + Beclometasone", "Cream", "Glenmark", 120.00),
        ("Volini Gel", "Diclofenac", "30g Gel", "Sun Pharma", 115.00),
        ("Quadriderm", "Clotrimazole + Neomycin", "Cream", "MSD Pharma", 95.00),
        
        # Thyroid & General RX
        ("Thyronorm 50", "Thyroxine", "50mcg", "Abbott India", 168.00),
        ("Eltroxin 50", "Thyroxine", "50mcg", "GSK India", 145.00),
        ("Drotin DS", "Drotaverine", "80mg", "Martin & Harris", 185.00),
        ("Meftal Spas", "Mefenamic Acid", "Tablet", "Blue Cross Labs", 48.00),
        ("Urimax 0.4", "Tamsulosin", "0.4mg", "Cipla Ltd", 265.00),
    ]

    generated_records = []
    
    # Generate 3 variations per medicine (2 Authentic/Active, 1 Expired/Archived)
    # Total = 50 * 3 = 150 unique records
    for i, med in enumerate(base_medicines):
        name, active_ing, strength, mfg_company, mrp = med
        base_batch = f"{name[:3].upper()}{i+100}"
        
        # Variation 1: Active Batch (Manufactured recently)
        generated_records.append((
            name, active_ing, strength, mfg_company, f"{base_batch}-A1", 
            "2024-10", "2027-10", mrp
        ))
        
        # Variation 2: Active Batch (Different month, minor price shift)
        generated_records.append((
            name, active_ing, strength, mfg_company, f"{base_batch}-B2", 
            "2025-02", "2028-02", mrp * 1.05  # 5% price increase logic
        ))
        
        # Variation 3: Officially Expired Batch (For testing expired logic)
        generated_records.append((
            name, active_ing, strength, mfg_company, f"{base_batch}-EXP", 
            "2020-01", "2022-01", mrp * 0.90
        ))

    # Bulk insert all 150 records safely
    cursor.executemany('''
    INSERT INTO authentic_batches (medicine_name, active_ingredient, strength, manufacturer, batch_number, mfg_date, exp_date, mrp)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', generated_records)

    conn.commit()
    conn.close()
    print(f"✅ Secure Database Init Complete! 150 unique records inserted. Autoincrement reset to 1.")

if __name__ == "__main__":
    setup_database()