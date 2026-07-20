import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

st.set_page_config(page_title="ShadowPoint Lead Engine", page_icon="🎯", layout="wide")

st.title("🎯 ShadowPoint B2B Sales Intelligence Dashboard")
st.write("Scan live web feeds, filter high-intent prospects, and auto-generate custom pitches.")

feed_url = st.text_input("🌐 Target Feed URL", value="https://news.ycombinator.com/")
st.subheader("🎯 Identified Leads")
st.dataframe(df_results, use_container_width=True)

st.subheader("📈 Lead Analytics")
fig, ax = plt.subplots(figsize=(5, 4))
sizes = [high_intent_count, filtered_count]
labels = ['High Intent Leads', 'Filtered Noise']
colors = ['#1F497D', '#D9D9D9']
ax.pie(sizes if sum(sizes) > 0 else [0, 1], labels=labels, colors=colors, autopct='%1.0f%%', startangle=140)
st.pyplot(fig)

except Exception as e:
st.error(f"❌ Error: {e}")
