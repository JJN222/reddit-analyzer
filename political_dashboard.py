import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta
import time

# Configure Streamlit page
st.set_page_config(
    page_title="Wikipedia Political Interest Tracker",
    page_icon="📚",
    layout="wide"
)

# Political figures with their Wikipedia page titles
POLITICAL_FIGURES = {
    # Trump Administration
    'Donald Trump': 'Donald_Trump',
    'Pete Hegseth': 'Pete_Hegseth',
    'Tulsi Gabbard': 'Tulsi_Gabbard', 
    'Robert F. Kennedy Jr.': 'Robert_F._Kennedy_Jr.',
    'Elon Musk': 'Elon_Musk',
    'Vivek Ramaswamy': 'Vivek_Ramaswamy',
    
    # Other Politicians
    'Joe Biden': 'Joe_Biden',
    'Kamala Harris': 'Kamala_Harris',
    'Ron DeSantis': 'Ron_DeSantis',
    'Gavin Newsom': 'Gavin_Newsom',
    'JD Vance': 'J._D._Vance',
    
    # Conservative Commentators  
    'Tucker Carlson': 'Tucker_Carlson',
    'Ben Shapiro': 'Ben_Shapiro',
    'Charlie Kirk': 'Charlie_Kirk',
    'Tim Pool': 'Tim_Pool',
    'Candace Owens': 'Candace_Owens',
    'Matt Walsh': 'Matt_Walsh_(political_commentator)',
    'Michael Knowles': 'Michael_J._Knowles',
    'Glenn Beck': 'Glenn_Beck',
    'Dan Bongino': 'Dan_Bongino',
    'Steven Crowder': 'Steven_Crowder'
}

# Wikipedia requires proper User-Agent header
HEADERS = {
    'User-Agent': 'Political-Interest-Tracker/1.0 (https://github.com/example/political-tracker; contact@example.com)'
}

def get_page_views(page_title, days=30):
    """Get Wikipedia page views for the last N days"""
    end_date = datetime.now() - timedelta(days=1)  # Wikipedia data has 1-day delay
    start_date = end_date - timedelta(days=days)
    
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/{page_title}/daily/{start_date.strftime('%Y%m%d')}/{end_date.strftime('%Y%m%d')}"
    
    try:
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            if 'items' in data and data['items']:
                return data['items']
            else:
                st.warning(f"No data found for {page_title}")
        else:
            st.error(f"HTTP {response.status_code} for {page_title}")
        return None
    except Exception as e:
        st.error(f"Exception for {page_title}: {e}")
        return None

def get_page_summary(page_title):
    """Get Wikipedia page summary"""
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_title}"
    
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def get_recent_edits(page_title, limit=10):
    """Get recent edits to a Wikipedia page"""
    url = f"https://en.wikipedia.org/w/api.php"
    params = {
        'action': 'query',
        'format': 'json',
        'prop': 'revisions',
        'titles': page_title.replace('_', ' '),
        'rvlimit': limit,
        'rvprop': 'timestamp|comment|user|size'
    }
    
    try:
        response = requests.get(url, params=params, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if 'query' in data and 'pages' in data['query']:
                page_data = list(data['query']['pages'].values())[0]
                if 'revisions' in page_data:
                    return page_data['revisions']
        return None
    except:
        return None

# Streamlit UI
st.title("📚 Wikipedia Political Interest Tracker")
st.markdown("*Tracking public interest through Wikipedia page views and activity*")

# Sidebar
st.sidebar.header("Settings")
selected_figures = st.sidebar.multiselect(
    "Select figures to analyze:",
    list(POLITICAL_FIGURES.keys()),
    default=list(POLITICAL_FIGURES.keys())[:8]
)

days_back = st.sidebar.slider("Days to analyze:", 7, 90, 30)

# Test with a simple, reliable page first
if st.sidebar.button("🧪 Test API with Donald Trump"):
    st.write("Testing Wikipedia API with proper User-Agent...")
    
    # Test the simplest case
    test_url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/Donald_Trump/daily/20241201/20241220"
    
    try:
        response = requests.get(test_url, headers=HEADERS)
        st.write(f"Test URL: {test_url}")
        st.write(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            st.write("✅ API working!")
            if 'items' in data and data['items']:
                st.write(f"Found {len(data['items'])} data points")
                st.write("Sample data:")
                st.json(data['items'][:3])  # Show first 3 items
            else:
                st.write("No items in response")
        else:
            st.write("❌ API Error")
            st.write(response.text[:500])  # First 500 chars only
            
    except Exception as e:
        st.write(f"❌ Exception: {e}")

# Main analysis
if st.button("📊 Analyze Wikipedia Interest") or 'wiki_data' not in st.session_state:
    
    st.info(f"Fetching Wikipedia data for {len(selected_figures)} figures...")
    
    analysis_results = []
    progress_bar = st.progress(0)
    
    for i, (name, page_title) in enumerate([(name, POLITICAL_FIGURES[name]) for name in selected_figures]):
        st.text(f"Analyzing: {name}")
        
        # Get page views
        page_views = get_page_views(page_title, days_back)
        
        if page_views:
            # Calculate metrics
            total_views = sum(item['views'] for item in page_views)
            avg_daily_views = total_views / len(page_views)
            recent_views = sum(item['views'] for item in page_views[-7:]) / 7  # Last week average
            
            # Get peak day
            peak_day = max(page_views, key=lambda x: x['views'])
            
            analysis_results.append({
                'name': name,
                'page_title': page_title,
                'total_views': total_views,
                'avg_daily_views': avg_daily_views,
                'recent_avg_views': recent_views,
                'peak_views': peak_day['views'],
                'peak_date': peak_day['timestamp'],
                'view_data': page_views
            })
        
        progress_bar.progress((i + 1) / len(selected_figures))
        time.sleep(0.1)  # Small delay to be respectful
    
    progress_bar.empty()
    st.session_state['wiki_data'] = analysis_results
    st.success(f"✅ Analysis complete! Got data for {len(analysis_results)} figures.")

# Display results
if 'wiki_data' in st.session_state and st.session_state['wiki_data']:
    data = st.session_state['wiki_data']
    
    # Sort by total views
    data.sort(key=lambda x: x['total_views'], reverse=True)
    
    st.header(f"📈 Wikipedia Interest Rankings ({days_back} days)")
    
    # Create summary table
    summary_data = []
    for person in data:
        summary_data.append({
            'Name': person['name'],
            'Total Views': f"{person['total_views']:,}",
            'Daily Average': f"{person['avg_daily_views']:,.0f}",
            'Recent Average': f"{person['recent_avg_views']:,.0f}",
            'Peak Views': f"{person['peak_views']:,}",
            'Peak Date': person['peak_date'][:10]  # Just the date
        })
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    # Detailed analysis
    st.header("🔍 Detailed Analysis")
    
    person_names = [person['name'] for person in data]
    selected_person_name = st.selectbox("Select person for detailed view:", person_names)
    
    if selected_person_name:
        selected_person = next(person for person in data if person['name'] == selected_person_name)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Create time series chart
            view_data = selected_person['view_data']
            chart_data = pd.DataFrame([
                {
                    'Date': datetime.strptime(item['timestamp'], '%Y%m%d00'),
                    'Views': item['views']
                }
                for item in view_data
            ])
            
            fig = px.line(
                chart_data,
                x='Date',
                y='Views', 
                title=f"Wikipedia Page Views: {selected_person_name}",
                labels={'Views': 'Daily Page Views'}
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Key metrics
            st.metric("Total Views", f"{selected_person['total_views']:,}")
            st.metric("Daily Average", f"{selected_person['avg_daily_views']:,.0f}")
            st.metric("Peak Day", f"{selected_person['peak_views']:,}")
            
            # Trend indicator
            recent_vs_overall = selected_person['recent_avg_views'] / selected_person['avg_daily_views']
            if recent_vs_overall > 1.2:
                st.success(f"📈 Trending Up ({recent_vs_overall:.1f}x)")
            elif recent_vs_overall < 0.8:
                st.warning(f"📉 Trending Down ({recent_vs_overall:.1f}x)")
            else:
                st.info("📊 Stable Interest")
        
        # Additional insights
        st.subheader("📋 Page Information")
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.write("**Recent Activity**")
            recent_edits = get_recent_edits(selected_person['page_title'])
            
            if recent_edits:
                for edit in recent_edits[:5]:
                    edit_date = edit['timestamp'][:10]
                    comment = edit.get('comment', 'No comment')[:50]
                    st.write(f"• {edit_date}: {comment}...")
            else:
                st.info("No recent edit data available")
        
        with col4:
            st.write("**Page Summary**")
            summary = get_page_summary(selected_person['page_title'])
            
            if summary and 'extract' in summary:
                st.write(summary['extract'][:200] + "...")
                if 'content_urls' in summary:
                    st.markdown(f"[Read full article →]({summary['content_urls']['desktop']['page']})")
            else:
                st.info("Summary not available")

else:
    st.info("👆 Click 'Analyze Wikipedia Interest' to start")

# Footer
st.markdown("---")
st.markdown("*Data from Wikipedia Pageviews API*")
st.markdown("*Wikipedia page views are a strong indicator of public interest and news activity*")
st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")