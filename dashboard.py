"""
Crash Tracking Dashboard
Beautiful, user-friendly Streamlit application for visualizing crash data
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="🎮 Game Crash Dashboard",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Beautiful Custom CSS - Modern Dark Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    
    :root {
        --primary-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%);
        --card-bg: rgba(30, 32, 44, 0.85);
        --card-border: rgba(99, 102, 241, 0.2);
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Outfit', sans-serif;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
    }
    
    .welcome-banner {
        background: var(--primary-gradient);
        border-radius: 24px;
        padding: 2.5rem 3rem;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(99, 102, 241, 0.3);
    }
    
    .welcome-banner h1 {
        color: white;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.8rem;
        font-weight: 700;
        margin: 0;
    }
    
    .welcome-banner p {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
        margin: 0.75rem 0 0 0;
    }
    
    .metric-card {
        background: var(--card-bg);
        backdrop-filter: blur(10px);
        border: 1px solid var(--card-border);
        border-radius: 20px;
        padding: 1.75rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 16px 32px rgba(99, 102, 241, 0.25);
    }
    
    .metric-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
    
    .metric-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text-primary);
    }
    
    .metric-label {
        color: var(--text-secondary);
        font-size: 0.95rem;
        font-weight: 500;
        text-transform: uppercase;
    }
    
    .upload-box {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%);
        border: 2px dashed rgba(99, 102, 241, 0.4);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    .insight-box {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 12px;
        padding: 1.25rem;
        margin: 1rem 0;
    }
    
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1a 100%);
    }
    
    .filter-header {
        background: var(--primary-gradient);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    .filter-header h2 {
        color: white;
        font-size: 1.25rem;
        margin: 0;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(30, 32, 44, 0.5);
        border-radius: 12px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: var(--text-secondary);
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--primary-gradient) !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)


# ==================== DATA FUNCTIONS ====================

def parse_date(date_str):
    if pd.isna(date_str):
        return None
    date_str = str(date_str).strip()
    formats = ['%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%b-%Y', '%Y/%m/%d']
    for fmt in formats:
        try:
            return pd.to_datetime(date_str, format=fmt)
        except:
            continue
    try:
        return pd.to_datetime(date_str, dayfirst=True)
    except:
        return None


def extract_crash_count(value):
    if pd.isna(value):
        return 0
    import re
    value_str = str(value).strip().upper()
    if value_str in ['', 'NA', 'N/A', '-', 'NONE', 'NULL']:
        return 0
    if 'K' in value_str:
        match = re.search(r'([\d.]+)\s*K', value_str)
        if match:
            return int(float(match.group(1)) * 1000)
    if 'M' in value_str:
        match = re.search(r'([\d.]+)\s*M', value_str)
        if match:
            return int(float(match.group(1)) * 1000000)
    numbers = re.findall(r'[\d,]+\.?\d*', value_str)
    if numbers:
        try:
            return int(float(numbers[0].replace(',', '')))
        except:
            return 0
    return 0


def categorize_crash_type(row):
    text = ' '.join(str(v).lower() for v in row.values if pd.notna(v))
    if 'anr' in text or 'not responding' in text:
        return 'ANR'
    elif 'fatal' in text and 'non' not in text:
        return 'Fatal'
    elif 'non-fatal' in text or 'nonfatal' in text:
        return 'Non-fatal'
    elif any(net in text for net in ['network', 'applovin', 'unity', 'moloco', 'ironsource']):
        return 'Network'
    return 'Non-fatal'


def process_dataframe(df):
    df.columns = df.columns.str.strip().str.replace('\n', ' ').str.replace('\r', ' ')
    
    if 'Date' in df.columns:
        df['Date'] = df['Date'].apply(parse_date)
        df = df[df['Date'].notna()]
    
    if 'Game' in df.columns:
        df['Game'] = df['Game'].astype(str).str.strip().str.title()
    else:
        df['Game'] = 'Unknown'
    
    if 'Platform' in df.columns:
        df['Platform'] = df['Platform'].astype(str).str.strip().str.title()
        df['Platform'] = df['Platform'].replace({'Ios': 'iOS', 'IOS': 'iOS', 'Nan': 'Unknown'})
    else:
        df['Platform'] = 'Unknown'
    
    df['Game'] = df['Game'].fillna('Unknown').replace('Nan', 'Unknown')
    df['Platform'] = df['Platform'].fillna('Unknown').replace('Nan', 'Unknown')
    
    crash_count_col = None
    for col in df.columns:
        if 'crash count' in col.lower():
            crash_count_col = col
            break
    
    if crash_count_col:
        df['Crash_Count_Numeric'] = df[crash_count_col].apply(extract_crash_count)
    else:
        df['Crash_Count_Numeric'] = 0
    
    df['Crash_Type'] = df.apply(categorize_crash_type, axis=1)
    
    if 'Network' in df.columns:
        df['Network_Name'] = df['Network'].apply(lambda x: str(x).strip() if pd.notna(x) else 'Unknown')
    else:
        df['Network_Name'] = 'Unknown'
    
    if 'Date' in df.columns and df['Date'].notna().any():
        df['Year'] = df['Date'].dt.year
        df['Month'] = df['Date'].dt.month
        df['Year_Month'] = df['Date'].dt.to_period('M')
        df['Year_Month_Str'] = df['Year_Month'].astype(str)
    
    return df


def render_metric_card(icon, value, label):
    return f"""
    <div class="metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """


# ==================== MAIN APP ====================

def main():
    # Initialize session state
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = None
    
    # Welcome Banner
    st.markdown("""
        <div class="welcome-banner">
            <h1>🎮 Game Crash Dashboard</h1>
            <p>Track, analyze, and understand app crashes across all your games</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Data Upload Section
    st.markdown("""
    <div class="upload-box">
        <h3 style="color: #f8fafc; margin: 0 0 0.5rem 0;">📊 Upload Your Crash Data</h3>
        <p style="color: #94a3b8; margin: 0;">
            Download CSV from your Google Sheet → Upload here → Dashboard updates instantly!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # File uploader
    uploaded_file = st.file_uploader(
        "📁 Drop your CSV file here",
        type=['csv'],
        help="Download CSV from Google Sheets: File → Download → CSV"
    )
    
    # Process uploaded file
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            df = process_dataframe(df)
            st.session_state.df = df
            st.session_state.last_refresh = datetime.now()
            st.success(f"✅ Loaded **{len(df)}** crash reports!")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    # Check if we have data
    df = st.session_state.df
    
    if df is None or len(df) == 0:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: rgba(30, 32, 44, 0.5); border-radius: 16px; margin-top: 2rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📤</div>
            <h2 style="color: #f8fafc;">Upload a CSV to Get Started</h2>
            <p style="color: #94a3b8; max-width: 400px; margin: 0 auto;">
                Go to your Google Sheet → File → Download → CSV<br>
                Then drag & drop the file above!
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    # ==================== SIDEBAR ====================
    st.sidebar.markdown("""
        <div class="filter-header">
            <h2>🎛️ Filters</h2>
        </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.last_refresh:
        st.sidebar.success(f"✅ Data loaded")
        st.sidebar.caption(f"📅 Loaded: {st.session_state.last_refresh.strftime('%I:%M %p')}")
        st.sidebar.caption(f"📊 Rows: {len(df):,}")
    
    st.sidebar.markdown("---")
    
    # Date Filter
    st.sidebar.markdown("### 📅 Time Period")
    date_range = None
    if 'Date' in df.columns and df['Date'].notna().any():
        min_date = df['Date'].min().date()
        max_date = df['Date'].max().date()
        
        preset = st.sidebar.radio(
            "Quick select:",
            ["📊 All Time", "📆 Last 7 Days", "📆 Last 30 Days", "📆 Last 90 Days"],
            index=0
        )
        
        if preset == "📆 Last 7 Days":
            date_range = (pd.to_datetime(max_date - timedelta(days=7)), pd.to_datetime(max_date))
        elif preset == "📆 Last 30 Days":
            date_range = (pd.to_datetime(max_date - timedelta(days=30)), pd.to_datetime(max_date))
        elif preset == "📆 Last 90 Days":
            date_range = (pd.to_datetime(max_date - timedelta(days=90)), pd.to_datetime(max_date))
        else:
            date_range = (pd.to_datetime(min_date), pd.to_datetime(max_date))
    
    st.sidebar.markdown("---")
    
    # Game Filter
    st.sidebar.markdown("### 🎮 Games")
    games = sorted([str(g) for g in df['Game'].dropna().unique().tolist() if str(g).strip() and str(g) != 'Unknown'])
    if not games:
        games = ['Unknown']
    selected_games = st.sidebar.multiselect("Choose games:", games, default=games)
    
    # Platform Filter
    st.sidebar.markdown("### 📱 Platforms")
    platforms = sorted([str(p) for p in df['Platform'].dropna().unique().tolist() if str(p).strip() and str(p) != 'Unknown'])
    if not platforms:
        platforms = ['Unknown']
    selected_platforms = st.sidebar.multiselect("Choose platforms:", platforms, default=platforms)
    
    # Apply Filters
    filtered_df = df.copy()
    if selected_games:
        filtered_df = filtered_df[filtered_df['Game'].isin(selected_games)]
    if selected_platforms:
        filtered_df = filtered_df[filtered_df['Platform'].isin(selected_platforms)]
    if date_range and 'Date' in filtered_df.columns:
        filtered_df = filtered_df[(filtered_df['Date'] >= date_range[0]) & (filtered_df['Date'] <= date_range[1])]
    
    if len(filtered_df) == 0:
        st.warning("⚠️ No data matches your filters. Try adjusting the filters in the sidebar.")
        st.stop()
    
    # ==================== METRICS ====================
    st.markdown("<br>", unsafe_allow_html=True)
    
    total_crashes = filtered_df['Crash_Count_Numeric'].sum()
    unique_games = filtered_df['Game'].nunique()
    unique_platforms = filtered_df['Platform'].nunique()
    total_reports = len(filtered_df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(render_metric_card("💥", f"{total_crashes:,}", "Total Crashes"), unsafe_allow_html=True)
    with col2:
        st.markdown(render_metric_card("🎮", unique_games, "Games"), unsafe_allow_html=True)
    with col3:
        st.markdown(render_metric_card("📱", unique_platforms, "Platforms"), unsafe_allow_html=True)
    with col4:
        st.markdown(render_metric_card("📋", total_reports, "Reports"), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Quick Insight
    if len(filtered_df) > 0 and filtered_df['Crash_Count_Numeric'].sum() > 0:
        top_game = filtered_df.groupby('Game')['Crash_Count_Numeric'].sum().idxmax()
        top_crashes = filtered_df.groupby('Game')['Crash_Count_Numeric'].sum().max()
        st.markdown(f"""
        <div class="insight-box">
            <div style="color: #3b82f6; font-weight: 600; font-size: 0.9rem; margin-bottom: 0.5rem;">💡 Quick Insight</div>
            <div style="color: #f8fafc; font-size: 1rem;"><strong>{top_game}</strong> has the most crashes with <strong>{top_crashes:,}</strong> total crashes.</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ==================== TABS ====================
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎮 Games", "📅 Trends", "🥧 Types", "🌐 Networks", "📋 Data"
    ])
    
    # TAB 1: Games
    with tab1:
        st.markdown("### Crashes by Game")
        
        game_totals = filtered_df.groupby('Game')['Crash_Count_Numeric'].sum().reset_index()
        game_totals.columns = ['Game', 'Crashes']
        game_totals = game_totals.sort_values('Crashes', ascending=False)
        
        fig = px.bar(game_totals, x='Game', y='Crashes',
                     color='Crashes', color_continuous_scale=['#6366f1', '#8b5cf6', '#d946ef'],
                     text='Crashes')
        fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig.update_layout(
            height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#94a3b8'), xaxis=dict(tickangle=-45), showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Platform comparison
        st.markdown("### Android vs iOS")
        game_plat = filtered_df.groupby(['Game', 'Platform'])['Crash_Count_Numeric'].sum().reset_index()
        
        fig2 = px.bar(game_plat, x='Game', y='Crash_Count_Numeric', color='Platform',
                      barmode='group', color_discrete_map={'Android': '#10b981', 'iOS': '#3b82f6'})
        fig2.update_layout(
            height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#94a3b8'), xaxis=dict(tickangle=-45)
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # TAB 2: Trends
    with tab2:
        st.markdown("### Crashes Over Time")
        
        if 'Year_Month_Str' in filtered_df.columns:
            monthly = filtered_df.groupby('Year_Month_Str')['Crash_Count_Numeric'].sum().reset_index()
            monthly.columns = ['Month', 'Crashes']
            monthly = monthly.sort_values('Month')
            
            fig = px.area(monthly, x='Month', y='Crashes')
            fig.update_traces(fill='tozeroy', line=dict(color='#8b5cf6', width=3),
                            fillcolor='rgba(139, 92, 246, 0.2)')
            fig.update_layout(
                height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94a3b8')
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📅 Date information not available for trend analysis")
    
    # TAB 3: Crash Types
    with tab3:
        st.markdown("### Crash Type Distribution")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("""
            **What Each Type Means:**
            - 🌐 **Network:** Ad network issues
            - ⚠️ **Non-fatal:** Errors that don't close app
            - 💥 **Fatal:** App crashes
            - ⏳ **ANR:** App frozen
            """)
        
        with col2:
            type_dist = filtered_df.groupby('Crash_Type').size().reset_index(name='Count')
            colors = {'Network': '#3b82f6', 'Non-fatal': '#f59e0b', 'Fatal': '#ef4444', 'ANR': '#8b5cf6'}
            
            fig = px.pie(type_dist, values='Count', names='Crash_Type',
                        color='Crash_Type', color_discrete_map=colors, hole=0.5)
            fig.update_traces(textinfo='percent+label')
            fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # TAB 4: Networks
    with tab4:
        st.markdown("### Ad Network Issues")
        
        network_data = filtered_df.groupby('Network_Name').size().reset_index(name='Count')
        network_data = network_data[network_data['Network_Name'] != 'Unknown']
        network_data = network_data.sort_values('Count', ascending=True).tail(10)
        
        if len(network_data) > 0:
            fig = px.bar(network_data, x='Count', y='Network_Name', orientation='h',
                        color='Count', color_continuous_scale=['#3b82f6', '#8b5cf6', '#d946ef'])
            fig.update_layout(
                height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94a3b8'), showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No network issues found in the data")
    
    # TAB 5: All Data
    with tab5:
        st.markdown("### All Crash Reports")
        
        display_cols = ['Date', 'Game', 'Platform', 'Crash_Count_Numeric', 'Crash_Type', 'Network_Name']
        available = [c for c in display_cols if c in filtered_df.columns]
        display_df = filtered_df[available].copy()
        
        if 'Date' in display_df.columns:
            display_df['Date'] = pd.to_datetime(display_df['Date']).dt.strftime('%Y-%m-%d')
        
        display_df = display_df.sort_values('Date', ascending=False) if 'Date' in display_df.columns else display_df
        
        st.dataframe(display_df, use_container_width=True, height=500, hide_index=True)
        
        csv = filtered_df.to_csv(index=False)
        st.download_button("⬇️ Download CSV", csv,
                          f"crash_report_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")


if __name__ == "__main__":
    main()
