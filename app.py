import streamlit as st
import pandas as pd
import requests
import urllib.parse
from bs4 import BeautifulSoup

st.set_page_config(page_title="GCC B2B Lead Generator", page_icon="🏢", layout="wide")

st.title("🏢 GCC B2B Lead & Industry Finder")
st.write("Target specific industries and business needs across GCC markets.")

# 1. Geographic Selection
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

# 2. Industry Categories
INDUSTRIES = [
    "Manufacturing Companies",
    "Construction & Contracting Companies",
    "Retail & Wholesale Businesses",
    "Software & Tech Companies",
    "Logistics & Supply Chain Companies",
    "Custom / Other"
]

# 3. What the Company Needs (Requirements)
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
    
    # Map Display
    st.subheader(f"🗺️ Target Region: {selected_location}")
    map_df = pd.DataFrame({"lat": [coords["lat"]], "lon": [coords["lon"]]})
    st.map(map_df, zoom=10)
    
    # Build Search Term
    if selected_need != "General Search (All Needs)":
        full_search = f"{selected_industry} {selected_need} in {selected_location}"
    else:
        full_search = f"{selected_industry} in {selected_location}"
        
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
            
            results.append({
                "Lead #": f"GCC-{idx}",
                "Company / Business Name": title,
                "Industry": selected_industry,
                "Target Requirement": selected_need,
                "Location": selected_location,
                "Website Link": link,
                "Details": snippet[:120] + "..." if len(snippet) > 120 else snippet
            })
            
        if results:
            df_results = pd.DataFrame(results)
            st.subheader("📊 Found Leads")
            st.dataframe(df_results, use_container_width=True)
            
            # Export CSV
            csv_data = df_results.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=f"{selected_industry.replace(' ', '_')}_leads.csv",
                mime="text/csv"
            )
        else:
            st.warning("No results found. Try broadening the search terms.")
            
    except Exception as e:
        st.error(f"Error fetching data: {e}")
