import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import openai
import os
from pytrends.request import TrendReq

# Configure Streamlit page
st.set_page_config(
    page_title="Shorthand Studios - Content Intelligence Platform",
    page_icon="🎯",
    layout="wide"
)

# Enhanced CSS for Shorthand Studios website styling
st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    :root {
        --shorthand-blue: #b5def2;
        --shorthand-cream: #e5dec8;
        --shorthand-dark: #322e25;
        --shorthand-white: #ffffff;
        --shorthand-gray: #f8f9fa;
        --shorthand-accent: #4a90e2;
    }
    
    /* Global styling */
    .main .block-container {
        padding-top: 1rem;
        max-width: 1200px;
    }
    
    /* Modern header */
    .main-header {
        background: linear-gradient(135deg, var(--shorthand-blue) 0%, var(--shorthand-accent) 100%);
        padding: 3rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
        text-align: center;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .logo-text {
        font-family: 'Inter', sans-serif;
        font-size: 3rem;
        font-weight: 900;
        color: var(--shorthand-white);
        letter-spacing: -1px;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        font-family: 'Inter', sans-serif;
        color: var(--shorthand-white);
        font-size: 1.3rem;
        font-weight: 400;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    /* Modern sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, var(--shorthand-cream) 0%, #f0f4f8 100%);
        border-right: 1px solid #e0e6ed;
    }
    
    .css-1d391kg .element-container {
        font-family: 'Inter', sans-serif;
    }
    
    /* Modern buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--shorthand-cream) 0%, #d6e8f5 100%);
        color: var(--shorthand-dark);
        border: 2px solid var(--shorthand-dark);
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        border-radius: 12px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, var(--shorthand-dark) 0%, #1a1612 100%);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    }
    
    /* Modern tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: var(--shorthand-gray);
        border-radius: 12px;
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        color: var(--shorthand-dark);
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--shorthand-white) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Modern cards */
    .ai-analysis {
        background: linear-gradient(135deg, #f8fafc 0%, #e3f2fd 100%);
        border: 1px solid var(--shorthand-blue);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        font-family: 'Inter', sans-serif;
    }
    
    .trend-card {
        background: var(--shorthand-white);
        border: 1px solid #e0e6ed;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
    }
    
    .trend-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.12);
    }
    
    /* Modern metrics */
    .stMetric {
        background: var(--shorthand-white);
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    /* Platform tabs styling */
    .platform-header {
        background: linear-gradient(135deg, var(--shorthand-dark) 0%, #4a4a4a 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px 12px 0 0;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        text-align: center;
        margin-bottom: 0;
    }
    
    /* Footer */
    .footer {
        background: linear-gradient(135deg, var(--shorthand-dark) 0%, #1a1612 100%);
        color: white;
        padding: 3rem 2rem;
        margin: 3rem -1rem -1rem -1rem;
        text-align: center;
        border-radius: 20px 20px 0 0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Custom expander styling */
    .streamlit-expanderHeader {
        background: var(--shorthand-gray);
        border-radius: 8px;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Enhanced Header
st.markdown("""
<div class="main-header">
    <div class="logo-text">SHORTHAND STUDIOS</div>
    <div class="subtitle">AI-Powered Content Intelligence Platform</div>
    <div style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.8;">
        🚀 Real-time trends • 🎯 Creator insights • 📊 Multi-platform analysis
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'saved_posts' not in st.session_state:
    st.session_state.saved_posts = []
if 'show_concepts' not in st.session_state:
    st.session_state.show_concepts = []
if 'selected_subreddit' not in st.session_state:
    st.session_state.selected_subreddit = "Conservative"
if 'trending_keywords' not in st.session_state:
    st.session_state.trending_keywords = []

# Reddit API headers
HEADERS = {
    'User-Agent': 'web:shorthand-reddit-analyzer:v1.0.0 (by /u/Ruhtorikal)',
    'Accept': 'application/json',
}

# Google Trends functions
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_trending_topics(region='US', category=0):
    """Get current trending topics from Google Trends"""
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        trending_searches = pytrends.trending_searches(pn=region)
        return trending_searches[0].head(20).tolist()
    except Exception as e:
        st.error(f"Error fetching trending topics: {str(e)}")
        return []

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_keyword_trends(keywords, timeframe='today 7-d', region='US'):
    """Get Google Trends data for specific keywords"""
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo=region, gprop='')
        
        # Interest over time
        interest_over_time = pytrends.interest_over_time()
        
        # Related queries
        related_queries = pytrends.related_queries()
        
        # Interest by region
        interest_by_region = pytrends.interest_by_region(resolution='COUNTRY')
        
        return {
            'interest_over_time': interest_over_time,
            'related_queries': related_queries,
            'interest_by_region': interest_by_region
        }
    except Exception as e:
        st.error(f"Error fetching keyword trends: {str(e)}")
        return None

def analyze_trends_with_ai(trending_data, creator_name, api_key):
    """Analyze trending topics with AI for content opportunities"""
    if not api_key or not trending_data:
        return None
    
    import openai
    openai.api_key = api_key
    
    trends_text = "\n".join([f"- {trend}" for trend in trending_data[:10]])
    
    prompt = f"""Analyze these current Google Trends for {creator_name}'s content strategy:

{trends_text}

For each trend, provide:
📈 TREND ANALYSIS: What this trend means and why it's popular
🎯 {creator_name.upper()} ANGLE: How {creator_name} could cover this topic authentically
🔥 CONTENT IDEA: Specific video/post title that would get clicks
📱 PLATFORM STRATEGY: Best platform for this content (YouTube, Twitter, TikTok, etc.)
⏰ TIMING: How urgent this content opportunity is (1-10)

Focus on trends that align with {creator_name}'s audience and style."""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            timeout=30
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Analysis Error: {str(e)}"

# [Include all your existing Reddit functions here - get_reddit_posts, analyze_with_ai, etc.]
# For brevity, I'll show the key additions and modifications

# Enhanced sidebar with platform selection
st.sidebar.header("🎯 Content Intelligence Hub")

# Platform tabs in sidebar
platform = st.sidebar.selectbox(
    "📊 Choose Platform",
    ["🌊 Reddit Analysis", "📈 Google Trends", "🎬 Show Planner", "💾 Saved Content"],
    key="platform_select"
)

# AI Configuration
st.sidebar.markdown("---")
st.sidebar.header("🔑 AI Configuration")
api_key = st.sidebar.text_input("OpenAI API Key", type="password", placeholder="sk-...", key="api_key_input")

if api_key:
    st.sidebar.success("✅ AI analysis enabled")
else:
    st.sidebar.warning("⚠️ Enter your OpenAI API key to enable AI analysis")

# Creator settings
st.sidebar.markdown("---")
st.sidebar.header("⚙️ Creator Settings")

creator_name = st.sidebar.text_input(
    "🎙️ Creator/Show", 
    value="Ben Shapiro",
    placeholder="e.g., Ben Shapiro, Matt Walsh, Kid Rock",
    key="creator_name_input"
)

# Main content based on platform selection
if platform == "📈 Google Trends":
    st.header("📈 Google Trends Intelligence")
    
    # Trends analysis tabs
    trend_tab1, trend_tab2, trend_tab3 = st.tabs(["🔥 Trending Now", "📊 Keyword Analysis", "🎯 Content Opportunities"])
    
    with trend_tab1:
        st.subheader("🔥 What's Trending Right Now")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            region = st.selectbox("🌍 Region", ["US", "GB", "CA", "AU"], key="region_select")
        with col2:
            if st.button("🔄 Refresh Trends", key="refresh_trends"):
                st.cache_data.clear()
        
        with st.spinner("Fetching trending topics..."):
            trending_topics = get_trending_topics(region=region)
        
        if trending_topics:
            st.success(f"✅ Found {len(trending_topics)} trending topics")
            
            # Display trending topics in cards
            for i, topic in enumerate(trending_topics, 1):
                with st.container():
                    st.markdown(f"""
                    <div class="trend-card">
                        <strong>#{i}</strong> &nbsp;&nbsp; 
                        <span style="font-size: 1.1rem; font-weight: 500;">{topic}</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            # AI Analysis of trends
            if api_key:
                st.markdown("### 🤖 AI Content Opportunity Analysis")
                with st.spinner("🤖 Analyzing trends for content opportunities..."):
                    trend_analysis = analyze_trends_with_ai(trending_topics, creator_name, api_key)
                    if trend_analysis:
                        st.markdown('<div class="ai-analysis">', unsafe_allow_html=True)
                        st.write(trend_analysis)
                        st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("❌ Could not fetch trending topics. Try again later.")
    
    with trend_tab2:
        st.subheader("📊 Custom Keyword Analysis")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            custom_keywords = st.text_input(
                "Enter keywords (comma-separated)",
                placeholder="e.g., Trump, Biden, cryptocurrency, AI",
                key="custom_keywords"
            )
        with col2:
            timeframe = st.selectbox(
                "Timeframe",
                ["today 1-d", "today 7-d", "today 1-m", "today 3-m"],
                key="timeframe_select"
            )
        
        if st.button("📊 Analyze Keywords", key="analyze_keywords") and custom_keywords:
            keywords_list = [k.strip() for k in custom_keywords.split(',')[:5]]  # Limit to 5
            
            with st.spinner(f"Analyzing trends for: {', '.join(keywords_list)}"):
                trends_data = get_keyword_trends(keywords_list, timeframe=timeframe)
            
            if trends_data and not trends_data['interest_over_time'].empty:
                st.success("✅ Trends analysis complete!")
                
                # Plot trends
                st.line_chart(trends_data['interest_over_time'].drop('isPartial', axis=1, errors='ignore'))
                
                # Related queries
                st.subheader("🔍 Related Queries & Rising Topics")
                for keyword in keywords_list:
                    if keyword in trends_data['related_queries']:
                        st.write(f"**{keyword}:**")
                        
                        related = trends_data['related_queries'][keyword]
                        if related['top'] is not None:
                            st.write("Top related:")
                            st.dataframe(related['top'].head(5), use_container_width=True)
                        
                        if related['rising'] is not None:
                            st.write("Rising:")
                            st.dataframe(related['rising'].head(5), use_container_width=True)
                        
                        st.markdown("---")
            else:
                st.error("❌ No trends data found for these keywords.")
    
    with trend_tab3:
        st.subheader("🎯 Content Opportunities")
        st.info("💡 This section combines trending topics with your Reddit analysis to suggest timely content ideas.")
        
        if st.session_state.trending_keywords:
            st.write("**Trending keywords from your analysis:**")
            for keyword in st.session_state.trending_keywords:
                st.write(f"- {keyword}")
        
        if api_key and trending_topics:
            st.markdown("### 🚀 AI-Powered Content Strategy")
            
            content_strategy_prompt = f"""Based on current Google Trends and {creator_name}'s style, create a content calendar for the next 7 days:

Trending Topics: {', '.join(trending_topics[:5])}

For each day, suggest:
📅 DAY: [Day of week]
🎯 MAIN TOPIC: [Primary focus]
📱 CONTENT TYPE: [Video/Tweet/Post/etc.]
🔥 HOOK: [Attention-grabbing opener]
📊 PREDICTED PERFORMANCE: [High/Medium/Low engagement]

Make suggestions that feel authentic to {creator_name}'s voice and audience."""

            if st.button("🎯 Generate Content Calendar", key="generate_calendar"):
                with st.spinner("🤖 Creating personalized content calendar..."):
                    content_calendar = analyze_trends_with_ai([content_strategy_prompt], creator_name, api_key)
                    if content_calendar:
                        st.markdown('<div class="ai-analysis">', unsafe_allow_html=True)
                        st.write(content_calendar)
                        st.markdown('</div>', unsafe_allow_html=True)

elif platform == "🌊 Reddit Analysis":
    # Your existing Reddit analysis code goes here
    st.header("🌊 Reddit Content Analysis")
    st.info("Your existing Reddit analysis features - keeping all current functionality")
    
elif platform == "🎬 Show Planner":
    # Your existing show planner code
    st.header("🎬 Show Concept Planner")
    st.info("Your existing show planning features")
    
elif platform == "💾 Saved Content":
    # Your existing saved content features
    st.header("💾 Saved Content Library")
    st.info("Your existing saved posts and show concepts")

# Enhanced Footer
st.markdown("""
<div class="footer">
    <div style="color: white; font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem;">SHORTHAND STUDIOS</div>
    <div style="color: #b5def2; font-size: 1.1rem; margin-bottom: 1rem;">AI-Powered Content Intelligence Platform</div>
    <div style="font-size: 0.9rem; opacity: 0.8;">
        🚀 Built for creators • 📊 Powered by AI • 🎯 Optimized for engagement
    </div>
</div>
""", unsafe_allow_html=True)