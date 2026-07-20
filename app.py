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

# --- DATABASE OF PAN-GCC ENTERPRISES ---
PRESET_GCC_COMPANIES = [
    # Construction
    {
        "Company Name": "Consolidated Contractors Company (CCC)",
        "Location": "Riyadh, Saudi Arabia & Dubai, UAE",
        "Industry": "Construction & Contracting",
        "Type": "Multinational Enterprise",
        "Needs": "Heavy Machinery, Fleet Management & Material Suppliers",
        "Phone": "+966 11 465 7700",
        "Website": "https://www.ccc.net"
    },
    {
        "Company Name": "Arabian Construction Company (ACC)",
        "Location": "Abu Dhabi, UAE & Jeddah, Saudi Arabia",
        "Industry": "Construction & Contracting",
        "Type": "Regional Enterprise",
        "Needs": "BIM Software, Facility Management & Subcontractors",
        "Phone": "+971 2 644 5400",
        "Website": "https://www.accgroup.com"
    },
    {
        "Company Name": "ALEC Engineering and Contracting",
        "Location": "Dubai, UAE & Riyadh, Saudi Arabia",
        "Industry": "Construction & Contracting",
        "Type": "Private Enterprise",
        "Needs": "ERP Automation & Subcontractor Procurement Solutions",
        "Phone": "+971 4 429 0599",
        "Website": "https://alec.ae"
    },

    # Retail
    {
        "Company Name": "Majid Al Futtaim (MAF)",
        "Location": "Dubai, UAE & All GCC Cities",
        "Industry": "Retail & Supermarkets",
        "Type": "Conglomerate",
        "Needs": "Digital Marketing, POS Solutions & Omni-Channel Tools",
        "Phone": "+971 4 294 2444",
        "Website": "https://www.majidalfuttaim.com"
    },
    {
        "Company Name": "Alshaya Group",
        "Location": "Kuwait City, Kuwait & Riyadh, KSA",
        "Industry": "Retail & Franchises",
        "Type": "Conglomerate",
        "Needs": "Supply Chain Automation, Warehouse & Logistics",
        "Phone": "+965 2224 2000",
        "Website": "https://www.alshaya.com"
    },
    {
        "Company Name": "Landmark Group",
        "Location": "Dubai, UAE & Riyadh, Saudi Arabia",
        "Industry": "Retail & Fashion",
        "Type": "Private Enterprise",
        "Needs": "E-Commerce Infrastructure & Warehouse Tech",
        "Phone": "+971 4 809 6000",
        "Website": "https://www.landmarkgroup.com"
    },

    # Manufacturing
    {
        "Company Name": "SABIC",
        "Location": "Riyadh, Saudi Arabia",
        "Industry": "Manufacturing & Chemicals",
        "Type": "Semi-Government / Enterprise",
        "Needs": "Industrial Safety Gear & Process Automation ERP",
        "Phone": "+966 11 225 8000",
        "Website": "https://www.sabic.com"
    },
    {
        "Company Name": "RAK Ceramics",
        "Location": "Ras Al Khaimah, UAE & Riyadh, KSA",
        "Industry": "Manufacturing & Materials",
        "Type": "Public Enterprise",
        "Needs": "Raw Material Suppliers & Global Freight Logistics",
        "Phone": "+971 7 244 7000",
        "Website": "https://www.rakceramics.com"
    },

    # Software & Tech
    {
        "Company Name": "MDS SI (Midis System Integration)",
        "Location": "Abu Dhabi, UAE & Riyadh, Saudi Arabia",
        "Industry": "Software & Tech",
        "Type": "System Integrator",
        "Needs": "Enterprise Cloud Infrastructure & Cybersecurity Tools",
        "Phone": "+971 2 610 8000",
        "Website": "https://mdssi.com"
    },
    {
        "Company Name": "Wipro Middle East",
        "Location": "Dubai, UAE & Riyadh, KSA",
        "Industry": "Software & Tech",
        "Type": "Global IT Consultancy",
        "Needs": "IT Specialized Recruitment & Tech Talent Sourcing",
        "Phone": "+971 4 391 3500",
        "Website": "https://www.wipro.com"
    }
]

# --- HEADER & TOP LAYOUT ---
header_left, header_right = st.columns([2, 1])

with header_left:
    st.title("🏢 GCC Pan-Regional Lead Finder")
    st.write(f"Logged in as: **{st.session_state.get('company')}**")

with header_right:
    st.write(" ")
    st.write(" ")
    # SEARCH BAR TOOL ON THE RIGHT SIDE
    search_keyword = st.text_input("🔍 Quick Keyword Search", placeholder="Type name, location, or keyword...")

st.markdown("---")

# --- CATEGORY FILTERS SECTION (DOWNSIDE) ---
st.subheader("📊 Category Filters & Lead Explorer")

# 5 Filter Columns for: Company, Location, Industry, Type, Needs
col_comp, col_loc, col_ind, col_type, col_need = st.columns(5)

df_all = pd.DataFrame(PRESET_GCC_COMPANIES)

with col_comp:
    selected_company = st.multiselect(
        "🏢 Company",
        options=sorted(list(df_all["Company Name"].unique())),
        default=[]
    )

with col_loc:
    selected_location = st.multiselect(
        "🌍 Location",
        options=sorted(list(set([loc for sublist in df_all["Location"].str.split(" & ") for loc in sublist]))),
        default=[]
    )

with col_ind:
    selected_industry = st.multiselect(
        "🏭 Industry",
        options=sorted(list(df_all["Industry"].unique())),
        default=[]
    )

with col_type:
    selected_type = st.multiselect(
        "🏷️ Type",
        options=sorted(list(df_all["Type"].unique())),
        default=[]
    )

with col_need:
    selected_needs = st.multiselect(
        "🎯 Needs / Requirements",
        options=sorted(list(df_all["Needs"].unique())),
        default=[]
    )

# --- FILTERING LOGIC ---
filtered_df = df_all.copy()

# Apply Keyword Search from Right Search Bar
if search_keyword.strip():
    kw = search_keyword.lower()
    filtered_df = filtered_df[
        filtered_df["Company Name"].str.lower().str.contains(kw) |
        filtered_df["Location"].str.lower().str.contains(kw) |
        filtered_df["Industry"].str.lower().str.contains(kw) |
        filtered_df["Type"].str.lower().str.contains(kw) |
        filtered_df["Needs"].str.lower().str.contains(kw)
    ]

# Apply Category Dropdown Filters
if selected_company:
    filtered_df = filtered_df[filtered_df["Company Name"].isin(selected_company)]

if selected_location:
    pattern = "|".join(selected_location)
    filtered_df = filtered_df[filtered_df["Location"].str.contains(pattern, case=False, na=False)]

if selected_industry:
    filtered_df = filtered_df[filtered_df["Industry"].isin(selected_industry)]

if selected_type:
    filtered_df = filtered_df[filtered_df["Type"].isin(selected_type)]

if selected_needs:
    filtered_df = filtered_df[filtered_df["Needs"].isin(selected_needs)]

# --- DISPLAY RESULTS TABLE ---
st.markdown("### 📋 Matching Leads")
st.dataframe(filtered_df, use_container_width=True)

# Export Data Button
csv_data = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Export Filtered Leads (CSV)",
    data=csv_data,
    file_name="GCC_Categorized_Leads.csv",
    mime="text/csv"
)

# --- LIVE SCRAPER ACCORDION SECTION ---
with st.expander("🔍 Switch to Live Web & LinkedIn Scraper"):
    col1, col2, col3 = st.columns(3)
    with col1:
        live_city = st.text_input("Target City", value="Riyadh, Saudi Arabia")
    with col2:
        live_industry = st.selectbox("Live Industry", ["Construction", "Retail", "Manufacturing", "Software & Tech"])
    with col3:
        live_need = st.text_input("Specific Need", value="Looking for Equipment Suppliers")
        
    if st.button("🚀 Run Live Web Search", type="primary"):
        full_query = f"{live_industry} companies {live_need} in {live_city}"
        st.info(f"Scanning web for: **{full_query}**...")
        
        try:
            encoded_query = urllib.parse.quote(full_query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            
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
                phone = raw_matches[0].strip() if raw_matches else "N/A (Check Link)"
                
                results.append({
                    "Lead #": f"LIVE-{idx}",
                    "Company Name": title,
                    "Location": live_city,
                    "Industry": live_industry,
                    "Type": "Web Lead",
                    "Needs": live_need,
                    "Phone": phone,
                    "Website": link
                })
                
            if results:
                df_live = pd.DataFrame(results)
                st.dataframe(df_live, use_container_width=True)
            else:
                st.warning("No results found.")
        except Exception as e:
            st.error(f"Error fetching live results: {e}")
