import streamlit as st
import pandas as pd
import requests
import urllib.parse
from bs4 import BeautifulSoup

st.set_page_config(page_title="ShadowPoint GCC Intelligence", page_icon="🌐", layout="wide")

st.title("🌐 ShadowPoint GCC Market & Lead Intelligence")
st.write("Search and discover business leads across Saudi Arabia, UAE, Qatar, Kuwait, Bahrain, and Oman.")

# GCC Coordinates for Mapping
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

col1, col2 = st.columns([2, 2])

with col1:
    selected_location = st.selectbox("🌍 Select Target GCC City", list(GCC_CITIES.keys()))
with col2:
    search_query = st.text_input("🔍 Business Niche / Service", value="Software companies")

if st.button("🚀 Find GCC Leads & Map Location", type="primary"):
    coords = GCC_CITIES[selected_location]
    
    # Show Map
    st.subheader(f"🗺️ Target Location: {selected_location}")
    map_df = pd.DataFrame({"lat": [coords["lat"]], "lon": [coords["lon"]]})
    st.map(map_df, zoom=10)
    
    # Fetch Search Results
    st.info(f"Scanning market for: **{search_query}** in **{selected_location}**...")
    
    full_search = f"{search_query} in {selected_location}"
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
                "Lead #": f"GCC-Lead-{idx}",
                "Business Name": title,
                "City/Country": selected_location,
                "Website Link": link,
                "Snippet Description": snippet[:120] + "..." if len(snippet) > 120 else snippet
            })
            
        if results:
            df_results = pd.DataFrame(results)
            st.subheader("📊 Identified GCC Leads")
            st.dataframe(df_results, use_container_width=True)
            
            # Export CSV
            csv_data = df_results.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download GCC Leads (CSV)",
                data=csv_data,
                file_name=f"{selected_location.replace(' ', '_')}_leads.csv",
                mime="text/csv"
            )
        else:
            st.warning("No search results returned. Try another niche or city.")
            
    except Exception as e:
        st.error(f"Error fetching data: {e}")
