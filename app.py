import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import urllib.parse
import matplotlib.pyplot as plt

st.set_page_config(page_title="ShadowPoint Web Intelligence", page_icon="🌐", layout="wide")

st.title("🌐 ShadowPoint Live Web Search & Lead Finder")
st.write("Search any topic or domain across the live web to extract and score high-intent leads.")

# User Inputs
col1, col2 = st.columns([2, 1])

with col1:
    search_query = st.text_input("🔍 Search Topic / Niche", value="SaaS startups looking for marketing")
with col2:
    keywords_str = st.text_input("🔑 Target Keywords (comma separated)", value="saas, marketing, tool, ai, growth")

if st.button("🚀 Search Web & Analyze Leads", type="primary"):
    if not search_query.strip():
        st.warning("Please enter a search query.")
    else:
        st.info(f"Scanning live web for: **{search_query}**...")
        
        try:
            # Format query for DuckDuckGo HTML search
            encoded_query = urllib.parse.quote(search_query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract search result blocks
            results = []
            keywords = [k.strip().lower() for k in keywords_str.split(",") if k.strip()]
            
            search_items = soup.find_all("div", class_="result__body")
            
            for idx, item in enumerate(search_items[:10], 1):
                title_tag = item.find("a", class_="result__url")
                snippet_tag = item.find("a", class_="result__snippet")
                
                title = item.find("a", class_="result__title").text.strip() if item.find("a", class_="result__title") else "N/A"
                link = title_tag["href"] if title_tag and "href" in title_tag.attrs else "#"
                snippet = snippet_tag.text.strip() if snippet_tag else ""
                
                # Intent scoring based on keyword match
                combined_text = (title + " " + snippet).lower()
                matched = [kw for kw in keywords if kw in combined_text]
                
                intent = "HIGH INTENT" if len(matched) >= 1 else "STANDARD"
                
                results.append({
                    "Lead #": f"Lead-{idx}",
                    "Title / Business": title,
                    "Website / URL": link,
                    "Matched Keywords": ", ".join(matched) if matched else "None",
                    "Intent Score": intent,
                    "Snippet": snippet[:100] + "..." if len(snippet) > 100 else snippet
                })
                
            if not results:
                st.error("No results found. Try a different search query.")
            else:
                df = pd.DataFrame(results)
                
                # Display Results Table
                st.subheader(f"📊 Results for '{search_query}'")
                st.dataframe(df, use_container_width=True)
                
                # Breakdown Stats
                high_intent_count = len(df[df["Intent Score"] == "HIGH INTENT"])
                standard_count = len(df) - high_intent_count
                
                st.success(f"Found {len(df)} live search results. {high_intent_count} flagged as High Intent!")
                
                # Chart
                st.subheader("📈 Lead Qualification Breakdown")
                fig, ax = plt.subplots(figsize=(5, 3))
                ax.pie([high_intent_count, standard_count], labels=["High Intent", "Standard"], colors=["#2E7D32", "#B0BEC5"], autopct='%1.0f%%', startangle=90)
                st.pyplot(fig)
                
        except Exception as e:
            st.error(f"Error fetching live results: {e}")
