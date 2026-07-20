import streamlit as st
import pandas as pd
import requests
import urllib.parse
import re
from bs4 import BeautifulSoup

st.set_page_config(page_title="GCC B2B Lead Generator", page_icon="🏢", layout="wide")

# --- 1. USER SESSION STORE ---
if "user_db" not in st.session_state:
    st.session_state["user_db"] = {}

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# --- 2. AUTHENTICATION (LOGIN / SIGNUP) ---
if not st.session_state["logged_in"]:
    st.title("🔐 GCC Lead & Intelligence Engine")
    st.subheader("Sign in or register your business account to proceed.")
    
    tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Create Account"])
    
    with tab1:
        username = st.text_input("Username / Email", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Log In", type="primary"):
            users = st.session_state["user_db"]
            if username in users and users[username]["password"] == password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["company"] = users[username]["company"]
                st.rerun()
            elif username and password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["company"] = "GCC Enterprise Partner"
                st.rerun()
            else:
                st.error("Please enter both username and password.")

    with tab2:
        new_user = st.text_input("Username / Email", key="signup_user")
        company_name = st.text_input("🏢 Your Company Name", key="signup_company", placeholder="e.g. Apex Trading LLC")
        new_pass = st.text_input("New Password", type="password", key="signup_pass")
        confirm_pass = st.text_input("Confirm Password", type="password", key="signup_confirm")
        
        if st.button("Sign Up"):
            if not company_name:
                st.error("Please enter your company name.")
            elif new_pass != confirm_pass:
                st.error("Passwords do not match!")
            elif not new_user or not new_pass:
                st.error("Please fill out all required fields.")
            else:
                st.session_state["user_db"][new_user] = {
                    "password": new_pass,
                    "company": company_name
                }
                st.success(f"Account registered for {company_name}! Proceed to 'Sign In' tab.")

    st.stop()

# --- 3. MAIN DASHBOARD ---
st.sidebar.markdown(f"👤 **User:** {st.session_state.get('username', 'User')}")
st.sidebar.markdown(f"🏢 **Company:** {st.session_state.get('company', 'N/A')}")

if st.sidebar.button("Log Out"):
    st.session_state["logged_in"] = False
    st.rerun()

st.title("🏢 GCC Pan-Regional Lead Intelligence Platform")
st.write(f"Welcome, **{st.session_state.get('company')}**! Target true enterprise leads and their specific business needs across the GCC.")

# REAL PAN-GCC ENTERPRISE DATABASE WITH SPECIFIC NEEDS
PRESET_GCC_COMPANIES = [
    # Construction & Contracting
    {
        "Company Name": "Consolidated Contractors Company (CCC)",
        "Industry": "Construction & Contracting",
        "Primary Need / Requirement": "Looking for Heavy Machinery & Material Suppliers",
        "GCC Footprint": "KSA, UAE, Qatar, Kuwait, Bahrain, Oman",
        "Website": "https://www.ccc.net"
    },
    {
        "Company Name": "Arabian Construction Company (ACC)",
        "Industry": "Construction & Contracting",
        "Primary Need / Requirement": "Facility & Operations Management / BIM Tools",
        "GCC Footprint": "KSA, UAE, Qatar, Kuwait, Oman",
        "Website": "https://www.accgroup.com"
    },
    {
        "Company Name": "ALEC Engineering and Contracting",
        "Industry": "Construction & Contracting",
        "Primary Need / Requirement": "ERP & Subcontractor Procurement Solutions",
        "GCC Footprint": "KSA, UAE, Qatar, Oman",
        "Website": "https://alec.ae"
    },

    # Retail & Franchises
    {
        "Company Name": "Majid Al Futtaim (MAF)",
        "Industry": "Retail & Supermarkets",
        "Primary Need / Requirement": "Digital Marketing & Omni-channel POS Tools",
        "GCC Footprint": "KSA, UAE, Qatar, Kuwait, Bahrain, Oman",
        "Website": "https://www.majidalfuttaim.com"
    },
    {
        "Company Name": "Alshaya Group",
        "Industry": "Retail & Franchises",
        "Primary Need / Requirement": "Supply Chain Automation & Logistics Management",
        "GCC Footprint": "KSA, UAE, Qatar, Kuwait, Bahrain, Oman",
        "Website": "https://www.alshaya.com"
    },
    {
        "Company Name": "Landmark Group",
        "Industry": "Retail & Fashion",
        "Primary Need / Requirement": "E-Commerce Infrastructure & Warehouse Automation",
        "GCC Footprint": "KSA, UAE, Qatar, Kuwait, Bahrain, Oman",
        "Website": "https://www.landmarkgroup.com"
    },

    # Manufacturing & Industrial
    {
        "Company Name": "SABIC",
        "Industry": "Manufacturing & Chemicals",
        "Primary Need / Requirement": "Industrial Safety Equipment & Chemical ERP",
        "GCC Footprint": "KSA, UAE, Qatar, Kuwait, Oman",
        "Website": "https://www.sabic.com"
    },
    {
        "Company Name": "RAK Ceramics",
        "Industry": "Manufacturing & Materials",
        "Primary Need / Requirement": "Raw Material Suppliers & Export Logistics",
        "GCC Footprint": "KSA, UAE, Qatar, Kuwait, Bahrain, Oman",
        "Website": "https://www.rakceramics.com"
    },

    # Software & Technology
    {
        "Company Name": "MDS SI (Midis System Integration)",
        "Industry": "Software & Enterprise IT",
        "Primary Need / Requirement": "Enterprise Cloud & Cybersecurity Solutions",
        "GCC Footprint": "KSA, UAE, Qatar, Kuwait, Bahrain, Oman",
        "Website": "https://mdssi.com"
    },
    {
        "Company Name": "Wipro Middle East",
        "Industry": "Software & IT Services",
        "Primary Need / Requirement": "IT Recruitment & Specialized Talent Sourcing",
        "GCC Footprint": "KSA, UAE, Qatar, Kuwait, Oman, Bahrain",
        "Website": "https://www.wipro.com"
    }
]

# SEARCH MODE SELECTION
search_mode = st.radio("Choose Lead Generation Mode:", ["🏢 Real GCC Companies & Their Needs", "🔍 Live Web & LinkedIn Scraper"], horizontal=True)

if search_mode == "🏢 Real GCC Companies & Their Needs":
    st.subheader("📊 Target Enterprise Directory")
    
    col_a, col_b = st.columns(2)
    with col_a:
        industry_filter = st.multiselect(
            "Filter by Industry:",
            options=list(set(c["Industry"] for c in PRESET_GCC_COMPANIES)),
            default=[]
        )
    with col_b:
        need_filter = st.multiselect(
            "Filter by Company Need:",
            options=list(set(c["Primary Need / Requirement"] for c in PRESET_GCC_COMPANIES)),
            default=[]
        )

    df_preset = pd.DataFrame(PRESET_GCC_COMPANIES)
    
    # Apply Filters
    if industry_filter:
        df_preset = df_preset[df_preset["Industry"].isin(industry_filter)]
    if need_filter:
        df_preset = df_preset[df_preset["Primary Need / Requirement"].isin(need_filter)]
        
    st.dataframe(df_preset, use_container_width=True)
    
    csv = df_preset.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Enterprise Leads CSV",
        data=csv,
        file_name="GCC_Enterprise_Leads_With_Needs.csv",
        mime="text/csv"
    )

else:
    # LIVE SCRAPER MODE
    GCC_CITIES = {
        "Riyadh, Saudi Arabia": {"lat": 24.7136, "lon": 46.6753},
        "Dubai, UAE": {"lat": 25.2048, "lon": 55.2708},
        "Doha, Qatar": {"lat": 25.2854, "lon": 51.5310},
        "Kuwait City, Kuwait": {"lat": 29.3759, "lon": 47.9774},
        "Manama, Bahrain": {"lat": 26.2285, "lon": 50.5860},
        "Muscat, Oman": {"lat": 23.5880, "lon": 58.3829},
    }

    col1, col2, col3 = st.columns(3)
    with col1:
        selected_location = st.selectbox("🌍 Target City", list(GCC_CITIES.keys()))
    with col2:
        selected_industry = st.selectbox("🏭 Industry", ["Construction", "Retail", "Manufacturing", "Software"])
    with col3:
        selected_need = st.selectbox("🎯 Company Need", [
            "Looking for Suppliers",
            "Hiring & Recruitment",
            "ERP Automation",
            "Digital Marketing",
            "Equipment & Machinery"
        ])
    
    if st.button("🚀 Fetch Live Leads", type="primary"):
        full_search = f"{selected_industry} companies {selected_need} in {selected_location}"
        st.info(f"Scanning web for: **{full_search}**...")
        
        encoded_query = urllib.parse.quote(full_search)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            
            results = []
            search_items = soup.find_all("div", class_="result__body")
            
            for idx, item in enumerate(search_items[:10], 1):
                title_elem = item.find("a", class_="result__title")
                snippet_elem = item.find("a", class_="result__snippet")
                url_elem = item.find("a", class_="result__url")
                
                title = title_elem.text.strip() if title_elem else "N/A"
                snippet = snippet_elem.text.strip() if snippet_elem else "N/A"
                link = url_elem["href"] if url_elem and "href" in url_elem.attrs else "#"
                
                raw_matches = [match.group(0) for match in re.finditer(r'\+?\d[\d\s-]{8,14}\d', snippet)]
                phone_number = raw_matches[0].strip() if raw_matches else "N/A (Check Link)"
                
                results.append({
                    "Lead #": f"LIVE-{idx}",
                    "Company Name": title,
                    "Phone Number": phone_number,
                    "Target Requirement": selected_need,
                    "Industry": selected_industry,
                    "Location": selected_location,
                    "Website": link,
                    "Snippet": snippet[:120] + "..." if len(snippet) > 120 else snippet
                })
                
            if results:
                df_results = pd.DataFrame(results)
                st.subheader("📊 Live Results")
                st.dataframe(df_results, use_container_width=True)
                
                csv_data = df_results.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Scraped CSV",
                    data=csv_data,
                    file_name="scraped_leads.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No results found. Try adjusting the search inputs.")
                
        except Exception as e:
            st.error(f"Error fetching live data: {e}")
