import streamlit as st

# Custom SVG Logo Function for Shadow Point
def render_shadow_point_logo(width=220):
    svg_code = f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 80" width="{width}px">
        <!-- Dark Hexagon Icon -->
        <polygon points="40,10 70,25 70,55 40,70 10,55 10,25" fill="#1E293B" />
        <!-- Inner Accent Shape -->
        <polygon points="40,18 62,30 62,50 40,62 18,50 18,30" fill="#0EA5E9" />
        <!-- Target Center Point -->
        <circle cx="40" cy="40" r="8" fill="#FFFFFF" />
        
        <!-- Typography -->
        <text x="85" y="42" font-family="'Helvetica Neue', Arial, sans-serif" font-size="24" font-weight="800" fill="#0F172A">SHADOW</text>
        <text x="85" y="62" font-family="'Helvetica Neue', Arial, sans-serif" font-size="20" font-weight="400" fill="#0EA5E9" letter-spacing="2">POINT</text>
    </svg>
    """
    st.markdown(svg_code, unsafe_allow_html=True)

# --- HOW TO USE IT IN YOUR APP ---

# 1. Sidebar Logo
with st.sidebar:
    render_shadow_point_logo(width=180)
    st.caption("GCC Enterprise Intelligence Engine")

# 2. Main Page Banner Logo
render_shadow_point_logo(width=260)
st.title("GCC Pan-Regional Lead Intelligence Platform")
