import streamlit as st
import pandas as pd
import requests
import urllib.parse
from geopy.geocoders import Nominatim

st.set_page_config(page_title="ShadowPoint Geo-Lead Engine", page_icon="📍", layout="wide")

st.title("📍 ShadowPoint Location & Lead Intelligence Platform")
st.write("Search any location worldwide to map coordinates, discover high-intent leads, and extract intelligence.")

# User Inputs
col1, col2 = st.columns([2, 2])

with col1:
    location_input = st.text_input("🌍 Target Location / City", value="London")
with col2:
    search_query = st.text_input("🔍 Business / Lead Niche", value="AI startups")

if st.button("🚀 Search Location & Generate Map", type="primary"):
    if not location_input.strip() or not search_query.strip():
        st.warning("Please fill in both location and business niche fields.")
    else:
        # Step 1: Geocode Location
        st.info(f"Geocoding location: **{location_input}**...")
        geolocator = Nominatim(user_agent="shadowpoint_lead_app")
        
        try:
            loc_data = geolocator.geocode(location_input)
            
            if not loc_data:
                st.error("Could not find coordinates for this location. Please try another city.")
            else:
                lat = loc_data.latitude
                lon = loc_data.longitude
                
                st.success(f"📍 Found Location: **{loc_data.address}** (Lat: {lat}, Lon: {lon})")
                
                # Step 2: Display Interactive Map
                st.subheader("🗺️ Target Location Map")
                map_df = pd.DataFrame({"lat": [lat], "lon": [lon]})
                st.map(map_df, zoom=11)
                
                # Step 3: Fetch Live Location Leads
                st.subheader(f"🔎 Live Search Results for '{search_query}' in {location_input}")
                
                full_search = f"{search_query} in {location_input}"
                encoded_query = urllib.parse.quote(full_search)
                url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
                
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                response = requests.get(url, headers=headers, timeout=10)
                
                from bs4 import BeautifulSoup
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
                        "Lead #": f"Lead-{idx}",
                        "Business Name / Title": title,
                        "Location": location_input,
                        "Website": link,
                        "Snippet": snippet[:120] + "..." if len(snippet) > 120 else snippet
                    })
                
                if results:
                    df_results = pd.DataFrame(results)
                    st.dataframe(df_results, use_container_width=True)
                    
                    # CSV Download Button
                    csv_data = df_results.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Leads as CSV",
                        data=csv_data,
                        file_name=f"{location_input}_{search_query}_leads.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No search results returned for this query.")
                    
        except Exception as e:
            st.error(f"An error occurred: {e}")
