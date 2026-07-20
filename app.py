import streamlit as st
import pandas as pd
import requests
import urllib.parse
import re
from bs4 import BeautifulSoup

# --- CONFIG & BRANDING ---
st.set_page_config(
    page_title="Shadow Point | GCC B2B Lead Generator",
    page_icon="🎯",
    layout="wide"
)
# Reliable direct image link
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"
# Replace this with your direct logo image URL if you have one hosted online
LOGO_URL = "https://img.icons8.com/color/96/target-molecule.png"

# --- 1. USER SESSION & SAVED LIST STORE ---
if "user_db" not in st.session_state:
    st.session_state["user_db"] = {}

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "saved_companies" not in st.session_state:
    st.session_state["saved_companies"] = []

# --- 2. AUTHENTICATION (LOGIN / SIGNUP) ---
if not st.session_state["logged_in"]:
    st.image(LOGO_URL, width=80)
    st.title("🎯 Shadow Point")
    st.subheader("GCC B2B Enterprise Lead & Intelligence Platform")
    st.write("Sign in or register your business account to proceed.")
    
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
                st.session_state["company"] = "Shadow Point Partner"
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

# --- 3. SIDEBAR BRANDING & NAVIGATION ---
st.sidebar.image(LOGO_URL, width=60)
st.sidebar.title("Shadow Point")
st.sidebar.caption("GCC Lead Intelligence")
st.sidebar.markdown("---")

nav_choice = st.sidebar.radio("Navigation", ["🏠 Home Dashboard", "🔍 Search & Filter Leads", "⭐ Saved Companies"])

st.sidebar.markdown("---")
st.sidebar.markdown(f"👤 **User:** {st.session_state.get('username', 'User')}")
st.sidebar.markdown(f"🏢 **Company:** {st.session_state.get('company', 'N/A')}")
st.sidebar.markdown(f"⭐ **Saved Items:** {len(st.session_state['saved_companies'])}")

if st.sidebar.button("Log Out"):
    st.session_state["logged_in"] = False
    st.session_state["saved_companies"] = []
    st.rerun()

# --- DATABASE OF PAN-GCC ENTERPRISES ---
PRESET_GCC_COMPANIES = [
    # Construction
    {
        "Company Name": "Consolidated Contractors Company (CCC)",
        "Location": "Riyadh, Saudi Arabia & Dubai, UAE",
        "Industry": "Construction & Contracting",
        "Type": "Multinational Enterprise",
        "Needs": "Heavy Cranes, Construction Machinery & Building Materials",
        "Phone": "+966 11 465 7700",
        "Website": "https://www.ccc.net"
    },
    {
        "Company Name": "Arabian Construction Company (ACC)",
        "Location": "Abu Dhabi, UAE & Jeddah, Saudi Arabia",
        "Industry": "Construction & Contracting",
        "Type": "Regional Enterprise",
        "Needs": "Safety Equipment, Scaffolding & Site Generators",
        "Phone": "+971 2 644 5400",
        "Website": "https://www.accgroup.com"
    },
    {
        "Company Name": "ALEC Engineering and Contracting",
        "Location": "Dubai, UAE & Riyadh, Saudi Arabia",
        "Industry": "Construction & Contracting",
        "Type": "Private Enterprise",
        "Needs": "BIM Software, Construction Fleet & Pre-fab Concrete",
        "Phone": "+971 4 429 0599",
        "Website": "https://alec.ae"
    },

    # Retail
    {
        "Company Name": "Majid Al Futtaim (MAF)",
        "Location": "Dubai, UAE & All GCC Cities",
        "Industry": "Retail & Supermarkets",
        "Type": "Conglomerate",
        "Needs": "Point of Sale (POS) Hardware, Cold Chain Storage & Commercial Refrigeration",
        "Phone": "+971 4 294 2444",
        "Website": "https://www.majidalfuttaim.com"
    },
    {
        "Company Name": "Alshaya Group",
        "Location": "Kuwait City, Kuwait & Riyadh, KSA",
        "Industry": "Retail & Franchises",
        "Type": "Conglomerate",
        "Needs": "Logistics Trucks, Warehouse Automation & Commercial Kitchen Equipment",
        "Phone": "+965 2224 2000",
        "Website": "https://www.alshaya.com"
    },
    {
        "Company Name": "Landmark Group",
        "Location": "Dubai, UAE & Riyadh, Saudi Arabia",
        "Industry": "Retail & Fashion",
        "Type": "Private Enterprise",
        "Needs": "E-Commerce Packaging, Security Scanners & Office Hardware",
        "Phone": "+971 4 809 6000",
        "Website": "https://www.landmarkgroup.com"
    },

    # Manufacturing
    {
        "Company Name": "SABIC",
        "Location": "Riyadh, Saudi Arabia",
        "Industry": "Manufacturing & Chemicals",
        "Type": "Semi-Government / Enterprise",
        "Needs": "Industrial Chemical Sensors, Safety Gear & Heavy Processing Machinery",
        "Phone": "+966 11 225 8000",
        "Website": "https://www.sabic.com"
    },
    {
        "Company Name": "RAK Ceramics",
        "Location": "Ras Al Khaimah, UAE & Riyadh, KSA",
        "Industry": "Manufacturing & Materials",
        "Type": "Public Enterprise",
        "Needs": "Kiln Machinery, Raw Clay Materials & Export Cargo Containers",
        "Phone": "+971 7 244 7000",
        "Website": "https://www.rakceramics.com"
    },

    # Software & Tech
    {
        "Company Name": "MDS SI (Midis System Integration)",
        "Location": "Abu Dhabi, UAE & Riyadh, Saudi Arabia",
        "Industry": "Software & Tech",
        "Type": "System Integrator",
        "Needs": "Data Center Rack Equipment, Server Hardware & Cloud Security Software",
        "Phone": "+971 2 610 8000",
        "Website": "https://mdssi.com"
    },
    {
        "Company Name": "Wipro Middle East",
        "Location": "Dubai, UAE & Riyadh, KSA",
        "Industry": "Software & Tech",
        "Type": "Global IT Consultancy",
        "Needs": "Laptops & IT Workstations, Specialized Developer Talent & Enterprise Software",
        "Phone": "+971 4 391 3500",
        "Website": "https://www.wipro.com"
    }
]

df_all = pd.DataFrame(PRESET_GCC_COMPANIES)

# ==========================================
# PAGE 1: HOME DASHBOARD
# ==========================================
if nav_choice == "🏠 Home Dashboard":
    col_logo, col_title = st.columns([1, 6])
    with col_logo:
        st.image(LOGO_URL, width=90)
    with col_title:
        st.title("Shadow Point")
        st.caption("Target Enterprise Intelligence Engine")

    st.markdown("---")
    st.write(f"Welcome back, **{st.session_state.get('company')}**! Use Shadow Point to identify key B2B leads, company requirements, and commercial contacts across the GCC.")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Enterprise Companies", len(df_all))
    m2.metric("GCC Regions Covered", "6 Countries")
    m3.metric("Key Industries", len(df_all["Industry"].unique()))
    m4.metric("Saved Companies", len(st.session_state["saved_companies"]))
    
    st.markdown("---")
    
    col_dash1, col_dash2 = st.columns(2)
    
    with col_dash1:
        st.subheader("📊 Companies by Industry")
        ind_counts = df_all["Industry"].value_counts()
        st.bar_chart(ind_counts)
        
    with col_dash2:
        st.subheader("⭐ Quick Access: Saved Companies")
        if st.session_state["saved_companies"]:
            df_saved = pd.DataFrame(st.session_state["saved_companies"])
            st.dataframe(df_saved[["Company Name", "Industry", "Phone", "Website"]], use_container_width=True)
        else:
            st.info("No saved companies yet. Go to 'Search & Filter Leads' to mark companies.")

# ==========================================
# PAGE 2: SEARCH & FILTER LEADS
# ==========================================
elif nav_choice == "🔍 Search & Filter Leads":
    header_left, header_right = st.columns([2, 1])

    with header_left:
        st.title("🎯 Shadow Point Lead Search")
        st.write("Filter enterprise opportunities across GCC markets.")

    with header_right:
        st.write(" ")
        search_keyword = st.text_input("🔍 Quick Keyword Search", placeholder="Type name, machinery, equipment...")

    st.markdown("---")

    # CATEGORY FILTERS SECTION
    st.subheader("📊 Category Filters")

    col_comp, col_loc, col_ind, col_type, col_need = st.columns(5)

    with col_comp:
        selected_company = st.multiselect("🏢 Company", options=sorted(list(df_all["Company Name"].unique())), default=[])

    with col_loc:
        all_locs = sorted(list(set([loc for sublist in df_all["Location"].str.split(" & ") for loc in sublist])))
        selected_location = st.multiselect("🌍 Location", options=all_locs, default=[])

    with col_ind:
        selected_industry = st.multiselect("🏭 Industry", options=sorted(list(df_all["Industry"].unique())), default=[])

    with col_type:
        selected_type = st.multiselect("🏷️ Type", options=sorted(list(df_all["Type"].unique())), default=[])

    with col_need:
        selected_needs = st.multiselect("🎯 Equipment & Needs", options=sorted(list(df_all["Needs"].unique())), default=[])

    # FILTERING LOGIC
    filtered_df = df_all.copy()

    if search_keyword.strip():
        kw = search_keyword.lower()
        filtered_df = filtered_df[
            filtered_df["Company Name"].str.lower().str.contains(kw) |
            filtered_df["Location"].str.lower().str.contains(kw) |
            filtered_df["Industry"].str.lower().str.contains(kw) |
            filtered_df["Type"].str.lower().str.contains(kw) |
            filtered_df["Needs"].str.lower().str.contains(kw)
        ]

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

    # ADD CHECKBOX "MARK TO SAVE" COLUMN
    saved_names = [c["Company Name"] for c in st.session_state["saved_companies"]]
    filtered_df["Mark to Save"] = filtered_df["Company Name"].apply(lambda name: name in saved_names)

    cols = ["Mark to Save", "Company Name", "Location", "Industry", "Type", "Needs", "Phone", "Website"]
    filtered_df = filtered_df[cols]

    st.markdown("### 📋 Matching Leads (Check the box to save a company)")

    edited_df = st.data_editor(
        filtered_df,
        column_config={
            "Mark to Save": st.column_config.CheckboxColumn(
                "⭐ Save",
                help="Check to bookmark this company to your saved list",
                default=False,
            ),
            "Website": st.column_config.LinkColumn("Website")
        },
        disabled=["Company Name", "Location", "Industry", "Type", "Needs", "Phone", "Website"],
        hide_index=True,
        use_container_width=True,
        key="lead_table_editor"
    )

    # UPDATE SAVED LIST
    new_saved_list = []
    for index, row in edited_df.iterrows():
        if row["Mark to Save"]:
            comp_data = row.to_dict()
            del comp_data["Mark to Save"]
            new_saved_list.append(comp_data)

    if new_saved_list != st.session_state["saved_companies"]:
        st.session_state["saved_companies"] = new_saved_list
        st.toast(f"Saved List Updated! ({len(new_saved_list)} saved)", icon="⭐")

    export_df = edited_df.drop(columns=["Mark to Save"])
    csv_data = export_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Filtered Leads (CSV)",
        data=csv_data,
        file_name="ShadowPoint_Leads.csv",
        mime="text/csv"
    )

# ==========================================
# PAGE 3: SAVED COMPANIES
# ==========================================
elif nav_choice == "⭐ Saved Companies":
    st.title("⭐ Shadow Point Saved Leads")
    st.write("Manage your bookmarked enterprise prospects.")
    
    if st.session_state["saved_companies"]:
        df_saved = pd.DataFrame(st.session_state["saved_companies"])
        st.dataframe(df_saved, use_container_width=True)
        
        col_rem1, col_rem2 = st.columns([3, 1])
        with col_rem1:
            comp_to_remove = st.selectbox("Select company to remove:", options=[c["Company Name"] for c in st.session_state["saved_companies"]])
        with col_rem2:
            st.write(" ")
            st.write(" ")
            if st.button("❌ Remove Company"):
                st.session_state["saved_companies"] = [c for c in st.session_state["saved_companies"] if c["Company Name"] != comp_to_remove]
                st.success(f"Removed {comp_to_remove}.")
                st.rerun()

        csv_saved = df_saved.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Saved List (CSV)",
            data=csv_saved,
            file_name="ShadowPoint_Saved_Leads.csv",
            mime="text/csv"
        )
    else:
        st.info("You haven't saved any companies yet. Go to 'Search & Filter Leads' and check the '⭐ Save' box!")
