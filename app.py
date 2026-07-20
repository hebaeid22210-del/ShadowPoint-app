import streamlit as st
import pandas as pd
import requests
import urllib.parse
import re
from bs4 import BeautifulSoup

st.set_page_config(page_title="GCC B2B Lead Generator", page_icon="🏢", layout="wide")

# Initialize user database/session store
if "user_db" not in st.session_state:
    st.session_state["user_db"] = {}  # Format: {username: {"password": pwd, "company": company_name}}

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# --- 1. LOGIN / SIGNUP SYSTEM ---
if not st.session_state["logged_in"]:
    st.title("🔐 Welcome to GCC B2B Lead Generator")
    st.subheader("Please sign in or create an account to access the search tool.")
    
    tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Create Account"])
    
    # LOGIN TAB
    with tab1:
        username = st.text_input("Username / Email", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Log In", type="primary"):
            users = st.session_state["user_db"]
            if username in users and users[username]["password"] == password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["company"] = users[username]["company"]
                st.success("Login successful!")
                st.rerun()
            elif username and password:
                # Direct entry fallback if testing before signing up
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["company"] = "Guest Business"
                st.rerun()
            else:
                st.error("Please enter both username and password.")

    # SIGNUP TAB
    with tab2:
        new_user = st.text_input("Username / Email", key="signup_user")
        company_name = st.text_input("🏢 Your Company Name", key="signup_company", placeholder="e.g. Acme Tech Solutions")
        new_pass = st.text_input("New Password", type="password", key="signup_pass")
        confirm_pass = st.text_input("Confirm Password", type="password", key="signup_confirm")
        
        if st.button("Sign Up"):
            if not company_name:
                st.error("Please enter your company name.")
            elif new_pass != confirm_pass:
                st.error("Passwords do not match!")
            elif not new_user or not new_pass:
                st.error("Please complete all required fields.")
            else:
                # Store user account details
                st.session_state["user_db"][new_user] = {
                    "password": new_pass,
                    "company": company_name
                }
                st.success(f"Account created for {company_name}! Switch to the Sign In tab to log in.")

    st.stop()  # Stop remaining page render until authenticated

# --- 2. MAIN APP CONTENT (Only visible after login) ---
st.sidebar.markdown(f"👤 **User:** {st.session_state.get('username', 'User')}")
st.sidebar.markdown(f"🏢 **Company:** {st.session_state.get('company', 'N/A')}")

if st.sidebar.button("Log Out"):
    st.session_state["logged_in"] = False
    st.rerun()

st.title("🏢 GCC B2B Lead & Industry Finder")
st.write(f"Welcome, **{st.session_state.get('company')}**! Search for target industries and leads across GCC markets.")

GCC_CITIES = {
    "Riyadh, Saudi Arabia": {"lat": 24.7136, "lon": 46.6753},
    "Jeddah, Saudi Arabia": {"lat": 21.5433, "lon": 39.1728},
    "Dubai, UAE": {"lat": 25.2048, "lon": 55.2708},
    "Abu Dhabi, UAE": {"lat": 24.4539, "lon": 54.3773},
    "Doha, Qatar": {"lat": 25.2854, "lon": 51.5310},
    "Kuwait City, Kuwait": {"lat": 29.3759, "lon": 47.9774},
    "Manama, Bahrain": {"lat": 26.2285, "lon": 50.5860},
    "Muscat, Oman": {"lat": 23.5880, "lon": 58.3829},
}

INDUSTRIES = [
    "Manufacturing Companies",
    "Construction & Contracting Companies",
    "Retail & Wholesale Businesses",
    "Software & Tech Companies",
    "Logistics & Supply Chain Companies",
    "Custom / Other"
]

COMPANY_NEEDS = [
    "Looking for Suppliers / Equipment",
    "Hiring / Recruitment Needs",
    "ERP & CRM Automation",
    "Digital Marketing & Lead Generation",
    "Facility & Operations Management",
    "General Search (All Needs)"
]

col1, col2, col3 = st.columns(3)

with col1:
    selected_location = st.selectbox("🌍 Select Target GCC City", list(GCC_CITIES.keys()))

with col2:
    selected_industry = st.selectbox("🏭 Target Industry", INDUSTRIES)
    if selected_industry == "Custom / Other":
        selected_industry = st.text_input("Type Custom Industry", value="Real Estate Companies")

with col3:
    selected_need = st.selectbox("🎯 Company Needs / Intent", COMPANY_NEEDS)

if st.button("🚀 Search GCC Leads", type="primary"):
    coords = GCC_CITIES[selected_location]
    
    st.subheader(f"🗺️ Target Region: {selected_location}")
    map_df = pd.DataFrame({"lat": [coords["lat"]], "lon": [coords["lon"]]})
    st.map(map_df, zoom=10)
    
    if selected_need != "General Search (All Needs)":
        full_search = f"{selected_industry} contact phone number {selected_need} in {selected_location}"
    else:
        full_search = f"{selected_industry} contact phone number in {selected_location}"
        
    st.info(f"Scanning for: **{full_search}**")
    
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
                "Lead #": f"GCC-{idx}",
                "Company Name": title,
                "Phone Number": phone_number,
                "Industry": selected_industry,
                "Requirement": selected_need,
                "Location": selected_location,
                "Website": link,
                "Snippet": snippet[:120] + "..." if len(snippet) > 120 else snippet
            })
            
        if results:
            df_results = pd.DataFrame(results)
            st.subheader("📊 Found Leads & Contacts")
            st.dataframe(df_results, use_container_width=True)
            
            csv_data = df_results.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV with Contacts",
                data=csv_data,
                file_name=f"{selected_industry.replace(' ', '_')}_leads.csv",
                mime="text/csv"
            )
        else:
            st.warning("No results found. Try broadening the search terms.")
            
    except Exception as e:
        st.error(f"Error fetching data: {e}")
