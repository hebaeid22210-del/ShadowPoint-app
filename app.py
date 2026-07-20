import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

st.set_page_config(page_title="ShadowPoint Lead Engine", page_icon="🎯", layout="wide")

st.title("🎯 ShadowPoint B2B Sales Intelligence Dashboard")
st.write("Scan live web feeds, filter high-intent prospects, and auto-generate custom pitches.")

feed_url = st.text_input("🌐 Target Feed URL", value="https://news.ycombinator.com/")
keywords_str = st.text_input("🔑 Intent Keywords", value="ai, tool, launch, app, system, build")

if st.button("🚀 Run ShadowPoint Pipeline", type="primary"):
    keywords = [k.strip().lower() for k in keywords_str.split(",") if k.strip()]
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(feed_url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    links = soup.find_all('span', class_='titleline')
    if not links:
        links = soup.find_all(['h1', 'h2', 'h3'])
        
    posts = [item.text.strip() for item in links[:12]]
    
    results = []
    high_intent_count = 0
    filtered_count = 0
    
    for idx, post in enumerate(posts, 1):
        text_lower = post.lower()
        if any(kw in text_lower for kw in keywords):
            high_intent_count += 1
            results.append({
                "Company / Target": f"Lead-#{idx}",
                "Post Content": post,
                "Intent Evaluation": "HIGH INTENT",
                "AI Pitch": f"Hi! We noticed your update regarding '{post[:35]}...'. Scale it with ShadowPoint!"
            })
        else:
            filtered_count += 1
            
    st.success(f"✅ Scanned {len(posts)} posts. Identified {high_intent_count} High-Intent Lead(s).")
    
    df_results = pd.DataFrame(results) if results else pd.DataFrame(columns=["Company / Target", "Post Content", "Intent Evaluation", "AI Pitch"])
    
    st.subheader("🎯 Identified Leads")
    st.dataframe(df_results, use_container_width=True)
    
    st.subheader("📈 Lead Analytics")
    fig, ax = plt.subplots(figsize=(5, 4))
    sizes = [high_intent_count, filtered_count]
    labels = ['High Intent Leads', 'Filtered Noise']
    colors = ['#1F497D', '#D9D9D9']
    ax.pie(sizes if sum(sizes) > 0 else [0, 1], labels=labels, colors=colors, autopct='%1.0f%%', startangle=140)
    st.pyplot(fig)
