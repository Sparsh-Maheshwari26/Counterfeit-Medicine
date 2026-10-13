import streamlit as st
import sqlite3
import pandas as pd
import time
from verifier import verify_medicine, get_dashboard_stats

# ----------------- PAGE CONFIG -----------------
st.set_page_config(page_title="MedVerify Tech", page_icon="💠", layout="wide", initial_sidebar_state="collapsed")

# ----------------- PREMIUM CSS THEMING & ANIMATIONS -----------------
st.markdown("""
<style>
    :root {
        --navy: #0A192F;
        --navy-light: #112240;
        --emerald: #10B981;
        --cyan: #06B6D4;
        --text-main: #E2E8F0;
        --text-muted: #94A3B8;
    }

    .stApp {
        background-color: var(--navy);
        background-image: radial-gradient(circle at 15% 50%, rgba(6, 182, 212, 0.05), transparent 25%),
                          radial-gradient(circle at 85% 30%, rgba(16, 185, 129, 0.05), transparent 25%);
        color: var(--text-main) !important;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    h1, h2, h3, h4, p, span, div { color: var(--text-main); }
    p { color: var(--text-muted); }

    .glass-card {
        background: rgba(17, 34, 64, 0.7);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 16px;
        border: 1px solid rgba(6, 182, 212, 0.15);
        padding: 2rem;
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
        animation: fadeInUp 0.6s cubic-bezier(0.23, 1, 0.32, 1) both;
    }
    .glass-card:hover {
        border-color: rgba(6, 182, 212, 0.4);
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input, .stNumberInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 8px !important;
        transition: all 0.3s ease;
    }
    .stTextInput > div > div > input:focus {
        border-color: var(--cyan) !important;
        box-shadow: 0 0 0 1px var(--cyan) !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, var(--emerald) 0%, var(--cyan) 100%) !important;
        color: var(--navy) !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.5rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3) !important;
    }
    .stButton > button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.5) !important;
        color: white !important;
    }

    div.row-widget.stRadio > div {
        display: flex;
        flex-direction: row;
        justify-content: center;
        gap: 20px;
        background: rgba(17, 34, 64, 0.8);
        padding: 10px 20px;
        border-radius: 50px;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        margin-bottom: 2rem;
    }

    .scanner-box {
        position: relative;
        height: 4px;
        width: 100%;
        background: rgba(255,255,255,0.1);
        border-radius: 2px;
        overflow: hidden;
        margin: 20px 0;
    }
    .scanner-laser {
        position: absolute;
        top: 0; left: 0;
        height: 100%; width: 50%;
        background: linear-gradient(90deg, transparent, var(--cyan), transparent);
        animation: scan 1.5s infinite ease-in-out;
    }
    
    @keyframes scan { 0% { left: -50%; } 100% { left: 100%; } }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    
    [data-testid="stMetricValue"] { color: var(--cyan) !important; font-weight: 800 !important; }
</style>
""", unsafe_allow_html=True)

# ----------------- SESSION STATE & NAVIGATION -----------------
st.markdown("<h2 style='text-align: center; color: #E2E8F0; font-weight: 800; margin-bottom: 5px;'><span style='color: #06B6D4;'>Med</span>Verify ⚕️</h2>", unsafe_allow_html=True)

nav_selection = st.radio("Navigation", ["Home", "Verify Medicine", "Analytics Dashboard", "Reference Database"], 
                         horizontal=True, label_visibility="collapsed")

# ----------------- PAGE: HOME (LANDING) -----------------
if nav_selection == "Home":
    st.markdown("""
        <div style="text-align: center; padding: 4rem 1rem; animation: fadeInUp 0.8s;">
            <h1 style="font-size: 3.5rem; font-weight: 900; margin-bottom: 1rem; line-height: 1.2;">
                Verify Medicines. <br><span style="color: #10B981;">Protect Lives.</span>
            </h1>
            <p style="font-size: 1.2rem; max-width: 600px; margin: 0 auto 2rem auto;">
                A next-generation metadata analysis engine designed to cross-reference pharmaceutical packaging against official manufacturer registries.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class="glass-card" style="text-align: center;"><h3 style="color: #06B6D4;">1. Input Data</h3><p>Manually enter packaging metadata including batch, dates, and MRP.</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="glass-card" style="text-align: center; animation-delay: 0.1s;"><h3 style="color: #06B6D4;">2. Engine Analysis</h3><p>System validates dates and checks for data anomalies and pricing manipulation.</p></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class="glass-card" style="text-align: center; animation-delay: 0.2s;"><h3 style="color: #06B6D4;">3. Risk Assessment</h3><p>Receive an instant risk score indicating authenticity likelihood.</p></div>""", unsafe_allow_html=True)

# ----------------- PAGE: VERIFY MEDICINE -----------------
elif nav_selection == "Verify Medicine":
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("🛡️ Authentication Scanner")
    st.write("Enter pharmaceutical metadata. All fields are required for accurate analysis.")
    
    with st.form("verify_form", border=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            batch_no = st.text_input("Batch Number", placeholder="e.g., DOL100-A1")
            med_name = st.text_input("Medicine Brand Name", placeholder="e.g., Dolo 650")
        with c2:
            manufacturer = st.text_input("Manufacturer", placeholder="e.g., Micro Labs Ltd")
            mfg_date = st.text_input("Mfg Date (YYYY-MM)", placeholder="2024-10")
        with c3:
            exp_date = st.text_input("Exp Date (YYYY-MM)", placeholder="2027-10")
            entered_mrp = st.number_input("Printed MRP (₹)", min_value=0.0, step=1.00)
            
        st.text("")
        submitted = st.form_submit_button("Initiate Security Scan", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        if not batch_no or not med_name or not manufacturer or not mfg_date or not exp_date:
            st.warning("⚠ System validation failed: All fields are required to run an accurate query.")
        else:
            scan_placeholder = st.empty()
            scan_placeholder.markdown("""
                <div class="glass-card" style="text-align: center;">
                    <h4 style="color: #06B6D4;">Querying Official Database...</h4>
                    <div class="scanner-box"><div class="scanner-laser"></div></div>
                    <p style="font-size: 0.9rem;">Cross-referencing batch metadata & executing anomaly detection.</p>
                </div>
            """, unsafe_allow_html=True)
            
            time.sleep(1.2) 
            scan_placeholder.empty() 
            
            result = verify_medicine(batch_no, med_name, manufacturer, mfg_date, exp_date, entered_mrp)
            
            st.markdown("<div class='glass-card' style='margin-top: 1rem;'>", unsafe_allow_html=True)
            st.subheader("📑 Final Diagnostic Report")
            
            rc1, rc2 = st.columns(2)
            rc1.metric(label="Calculated Risk Score", value=f"{result['score']} / 100")
            rc2.metric(label="Authentication Status", value=f"{result['badge']} {result['status']}")

            if "Match Found" in result['status']:
                st.success("**Clearance:** The provided metadata aligns perfectly with authorized manufacturer reference records.")
            elif "Suspicious" in result['status']:
                st.warning("**Caution Required:** Conflicting data detected. This may indicate tampering, price gouging, or a counterfeit.")
            else:
                st.error("**Critical Alert:** High probability of counterfeit product. Batch unrecognized in official systems.")
            
            st.markdown("#### Detailed Logic Findings")
            for reason in result['reasons']:
                st.markdown(f"<span style='color: #E2E8F0;'>• {reason}</span>", unsafe_allow_html=True)
            
            st.divider()
            st.caption("ℹ️ **Important Disclaimer:** This is a prototype system. MedVerify authenticates metadata logic against an internal reference database. It does not perform chemical authentication.")
            st.markdown("</div>", unsafe_allow_html=True)

# ----------------- PAGE: ANALYTICS DASHBOARD -----------------
elif nav_selection == "Analytics Dashboard":
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("📊 System Analytics & History")
    
    total, authentic, suspicious, fake, recent = get_dashboard_stats()
    
    dc1, dc2, dc3, dc4 = st.columns(4)
    dc1.metric("Total Verification Scans", total)
    dc2.metric("Authentic Matches", authentic)
    dc3.metric("Suspicious Flags", suspicious)
    dc4.metric("Unknown / Fakes", fake)
    
    st.divider()
    st.markdown("#### Recent Activity Log")
    if len(recent) == 0:
        st.info("No verification history found. Run a scan to generate data.")
    else:
        df = pd.DataFrame(recent)
        df = df[['timestamp', 'batch_number', 'medicine_name', 'status', 'risk_score']]
        # Generate clean 1-based index for the dashboard
        df.insert(0, '#', range(1, len(df) + 1))
        st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------- PAGE: REFERENCE REGISTRY -----------------
elif nav_selection == "Reference Database":
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("🏢 Approved Manufacturer Registry")
    
    try:
        conn = sqlite3.connect('medverify_reference.db')
        df = pd.read_sql_query("SELECT * FROM authentic_batches", conn)
        conn.close()
        
        # Display live count metrics
        st.metric(label="Total Official Records Loaded", value=len(df))
        
        # Apply Search Filtering
        search = st.text_input("🔎 Search by Medicine or Batch:", "")
        if search:
            df = df[df['medicine_name'].str.contains(search, case=False) | df['batch_number'].str.contains(search, case=False)]
            
        # FIX: The Serial Number Bug Solution
        # 1. Drop the internal SQLite 'id' column which jumps due to database operations
        df = df.drop(columns=['id'], errors='ignore')
        
        # 2. Re-calculate a clean, sequential 'S.No.' column starting at 1 based on the currently filtered view
        df.insert(0, 'S.No.', range(1, len(df) + 1))
        
        # Format Data for UI
        df['mrp'] = df['mrp'].apply(lambda x: f"₹ {x:.2f}")
        df.rename(columns={'mrp': 'MRP', 'medicine_name': 'Medicine Name', 'batch_number': 'Batch No.'}, inplace=True)
        
        st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error("Reference database not found. Ensure setup_db.py has been run.")
    st.markdown("</div>", unsafe_allow_html=True)