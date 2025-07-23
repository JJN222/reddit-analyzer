import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
import openai
import base64

# Configure Streamlit page
st.set_page_config(
    page_title="Shorthand Studios - Reddit Content Intelligence",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS for Shorthand Studios branding
st.markdown("""
<style>
    /* Main color scheme */
    :root {
        --shorthand-blue: #b5def2;
        --shorthand-cream: #e5dec8;
        --shorthand-dark: #322e25;
    }
    
    /* Header styling */
    .main-header {
        background-color: var(--shorthand-blue);
        padding: 2rem 0;
        margin: -1rem -1rem 2rem -1rem;
        text-align: center;
        border-bottom: 3px solid var(--shorthand-dark);
    }
    
    .logo-container {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1rem;
    }
    
    .logo-text {
        font-size: 2.5rem;
        font-weight: 900;
        color: var(--shorthand-dark);
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    
    .subtitle {
        color: var(--shorthand-dark);
        font-size: 1.2rem;
        font-weight: 500;
        margin-top: 0.5rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: var(--shorthand-cream) !important;
    }
    
    .css-1d391kg .css-10trblm {
        background-color: var(--shorthand-cream) !important;
    }
    
    .css-1lcbmhc {
        background-color: var(--shorthand-cream) !important;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: var(--shorthand-cream);
        color: var(--shorthand-dark);
        border: 2px solid var(--shorthand-dark);
        font-weight: 600;
        border-radius: 8px;
    }
    
    .stButton > button:hover {
        background-color: var(--shorthand-dark);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(50, 46, 37, 0.3);
    }
    
    /* Metrics styling */
    .metric-container {
        background: var(--shorthand-cream);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid var(--shorthand-blue);
    }
    
    /* Success/info boxes */
    .stSuccess {
        background-color: var(--shorthand-blue);
        color: var(--shorthand-dark);
    }
    
    .stInfo {
        background-color: var(--shorthand-cream);
        color: var(--shorthand-dark);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: var(--shorthand-cream);
        color: var(--shorthand-dark);
        font-weight: 600;
    }
    
    /* AI Analysis section styling */
    .ai-analysis {
        background: var(--shorthand-cream);
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid var(--shorthand-blue);
        margin: 1rem 0;
    }
    
    /* Footer styling */
    .footer {
        background: var(--shorthand-dark);
        color: white;
        padding: 2rem;
        margin: 2rem -1rem -1rem -1rem;
        text-align: center;
        border-top: 3px solid var(--shorthand-blue);
    }
</style>
""", unsafe_allow_html=True)

# Create the header with logo
st.markdown("""
<div class="main-header">
    <div class="logo-container">
        <div class="logo-text">SHORTHAND STUDIOS</div>
    </div>
    <div class="subtitle">AI-Powered Reddit Content Intelligence Platform</div>
</div>
""", unsafe_allow_html=True)

# Reddit API headers
HEADERS = {
    'User-Agent': 'AI-Content-Ideation-Tool/1.0 (Daily Wire Content Discovery)'
}

def get_reddit_posts(subreddit, category="hot", limit=5):
    """Get posts from specified subreddit and category"""
    url = f"https://www.reddit.com/r/{subreddit}/{category}.json"
    params = {'limit': limit}
    
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'children' in data['data']:
                return data['data']['children']
        elif response.status_code == 404:
            st.error(f"Subreddit r/{subreddit} not found or is private")
        elif response.status_code == 403:
            st.error(f"Access denied to r/{subreddit} - subreddit may be private or banned")
        else:
            st.error(f"Error {response.status_code} accessing r/{subreddit}")
        return []
    except Exception as e:
        st.error(f"Error fetching posts from r/{subreddit}: {e}")
        return []

def get_post_content(post_id, subreddit):
    """Get full post content including body text and additional context"""
    url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json"
    
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if len(data) > 0 and 'data' in data[0] and 'children' in data[0]['data']:
                post_data = data[0]['data']['children'][0]['data']
                
                # Get link information if it's a link post
                additional_context = {}
                
                # If it's a link post, get the domain and URL
                if post_data.get('url') and not post_data['url'].startswith('https://www.reddit.com'):
                    additional_context['link_url'] = post_data['url']
                    additional_context['domain'] = post_data.get('domain', '')
                
                # Get the post flair for context
                if post_data.get('link_flair_text'):
                    additional_context['flair'] = post_data['link_flair_text']
                
                # Get post body text if it exists
                if post_data.get('selftext'):
                    additional_context['body_text'] = post_data['selftext']
                
                return additional_context
        return {}
    except Exception as e:
        return {}

def get_top_comments(post_id, subreddit, limit=3):
    """Get top 3 comments instead of just 1 for more context"""
    url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json"
    
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1 and 'data' in data[1] and 'children' in data[1]['data']:
                comments = data[1]['data']['children']
                
                top_comments = []
                for comment in comments[:limit*2]:  # Get extra in case some are deleted
                    if comment['kind'] == 't1':  # Comment type
                        comment_data = comment['data']
                        if (comment_data.get('body', '') not in ['[deleted]', '[removed]', ''] and 
                            comment_data.get('score', 0) > 0 and
                            len(top_comments) < limit):
                            top_comments.append({
                                'body': comment_data['body'],
                                'score': comment_data.get('score', 0),
                                'author': comment_data.get('author', 'Unknown')
                            })
                
                return top_comments
        return []
    except Exception as e:
        return []

def format_time_ago(created_utc):
    """Convert UTC timestamp to time ago"""
    now = datetime.now().timestamp()
    diff = now - created_utc
    
    if diff < 3600:  # Less than 1 hour
        return f"{int(diff // 60)}m ago"
    elif diff < 86400:  # Less than 1 day
        return f"{int(diff // 3600)}h ago"
    else:
        return f"{int(diff // 86400)}d ago"

def ai_analyze_post(title, post_content, comments, api_key):
    """Use OpenAI to analyze a post with multiple insights"""
    
    # Prepare combined text for analysis - keep it shorter to avoid timeouts
    comments_text = "\n".join([f"Comment: {c['body'][:100]}" for c in comments[:3]])  # Reduced
    
    full_context = f"""
    TITLE: {title}
    POST CONTENT: {post_content[:400]}
    TOP COMMENTS: {comments_text[:500]}
    """
    
    try:
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Switch to faster, cheaper model
            messages=[
                {"role": "system", "content": """You are a content strategist for The Daily Wire analyzing Reddit posts. 

Provide analysis in this EXACT format:

SUMMARY: [One clear sentence explaining what this post is actually about]

SENTIMENT: [How conservatives feel about this - include nuances]

DAILY_WIRE_ANGLE: [Specific framing recommendation for Daily Wire audience]

TREND_PREDICTION: [Momentum and timing recommendations]

SHOW_PREP: [Angles for Ben Shapiro, Matt Walsh, Michael Knowles]

RISK_ASSESSMENT: [Low/Medium/High risk with reasoning]

SOCIAL_CONTENT: [Meme/social media opportunities]"""},
                {"role": "user", "content": full_context}
            ],
            max_tokens=400,  # Reduced from 600
            temperature=0.3,
            timeout=20  # 20 second timeout
        )
        
        analysis = response.choices[0].message.content.strip()
        
        # Parse the response into structured data
        sections = {}
        current_section = None
        
        for line in analysis.split('\n'):
            line = line.strip()
            if line.startswith('SUMMARY:'):
                current_section = 'summary'
                sections[current_section] = line.replace('SUMMARY:', '').strip()
            elif line.startswith('SENTIMENT:'):
                current_section = 'sentiment'
                sections[current_section] = line.replace('SENTIMENT:', '').strip()
            elif line.startswith('DAILY_WIRE_ANGLE:'):
                current_section = 'angle'
                sections[current_section] = line.replace('DAILY_WIRE_ANGLE:', '').strip()
            elif line.startswith('TREND_PREDICTION:'):
                current_section = 'trend'
                sections[current_section] = line.replace('TREND_PREDICTION:', '').strip()
            elif line.startswith('SHOW_PREP:'):
                current_section = 'show_prep'
                sections[current_section] = line.replace('SHOW_PREP:', '').strip()
            elif line.startswith('RISK_ASSESSMENT:'):
                current_section = 'risk'
                sections[current_section] = line.replace('RISK_ASSESSMENT:', '').strip()
            elif line.startswith('SOCIAL_CONTENT:'):
                current_section = 'social'
                sections[current_section] = line.replace('SOCIAL_CONTENT:', '').strip()
            elif current_section and line:
                sections[current_section] += ' ' + line
        
        return sections
        
    except Exception as e:
        error_msg = str(e)
        if "timeout" in error_msg.lower():
            return {
                'summary': 'Analysis timed out - try again',
                'sentiment': 'Request took too long to process',
                'angle': 'Manual analysis recommended',
                'trend': 'Unknown due to timeout',
                'show_prep': 'Analyze manually',
                'risk': 'Unable to assess',
                'social': 'No recommendations due to timeout'
            }
        else:
            st.error(f"AI Analysis Error: {e}")
            return {
                'summary': 'AI analysis failed',
                'sentiment': 'Please check connection and try again',
                'angle': 'Manual analysis required',
                'trend': 'Unknown',
                'show_prep': 'Manual research needed',
                'risk': 'Manual assessment required',
                'social': 'No recommendations available'
            }

def analyze_content_opportunities(posts_data):
    """Analyze posts for content opportunities"""
    opportunities = []
    
    # Handle the case where posts_data might be a dict with categories
    if isinstance(posts_data, dict):
        for category, posts in posts_data.items():
            if category == 'subreddit':  # Skip the subreddit name key
                continue
            if not posts:
                continue
                
            for post in posts:
                score = post['score']
                comments = post['num_comments']
                title = post['title']
                
                # High engagement content
                if score > 1000 and comments > 100:
                    opportunities.append(f"🔥 HIGH ENGAGEMENT: '{title[:60]}...' ({score:,} upvotes, {comments} comments) - Consider similar content")
                
                # Controversial content (high comments relative to upvotes)
                elif comments > score / 5 and score > 100:
                    opportunities.append(f"🌶️ CONTROVERSIAL: '{title[:60]}...' - High debate potential for content")
                
                # Rising trends
                elif category == "rising" and score > 100:
                    opportunities.append(f"📈 TRENDING: '{title[:60]}...' - Emerging topic to cover early")
    
    return opportunities

def display_posts(posts, subreddit):
    """Display posts with AI analysis if available"""
    if not posts:
        st.info("No posts found in this category")
        return
    
    for i, post in enumerate(posts):
        # Create expandable section with AI insight in title if available
        title_preview = post['title'][:80] + "..." if len(post['title']) > 80 else post['title']
        
        if post.get('ai_analysis') and post['ai_analysis'].get('summary'):
            expander_title = f"#{i+1}: {title_preview} | AI: {post['ai_analysis']['summary'][:60]}..."
        else:
            expander_title = f"#{i+1}: {title_preview}"
        
        with st.expander(expander_title):
            
            # AI Analysis Section (if available)
            if post.get('ai_analysis'):
                ai = post['ai_analysis']
                
                st.markdown('<div class="ai-analysis">', unsafe_allow_html=True)
                st.markdown("### 🤖 AI Analysis")
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    if ai.get('summary'):
                        st.write(f"**📝 What This Is Really About:**")
                        st.write(ai['summary'])
                    
                    if ai.get('sentiment'):
                        st.write(f"**💭 Conservative Sentiment:**")
                        st.write(ai['sentiment'])
                    
                    if ai.get('angle'):
                        st.write(f"**🎯 Daily Wire Angle:**")
                        st.write(ai['angle'])
                
                with col2:
                    if ai.get('trend'):
                        st.write(f"**📈 Trend Prediction:**")
                        st.write(ai['trend'])
                    
                    if ai.get('risk'):
                        risk_level = ai['risk']
                        if 'high' in risk_level.lower():
                            st.error(f"⚠️ **Risk Assessment:** {risk_level}")
                        elif 'medium' in risk_level.lower():
                            st.warning(f"⚡ **Risk Assessment:** {risk_level}")
                        else:
                            st.success(f"✅ **Risk Assessment:** {risk_level}")
                
                # Show prep and social content
                if ai.get('show_prep'):
                    st.write(f"**📺 Show Prep Ideas:**")
                    st.write(ai['show_prep'])
                
                if ai.get('social'):
                    st.write(f"**📱 Social Content Ideas:**")
                    st.write(ai['social'])
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("---")
            
            # Original Post Content Section
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown("### 📋 Post Details")
                st.write(f"**Title:** {post['title']}")
                
                # Show additional context
                if post.get('post_context'):
                    context = post['post_context']
                    
                    if context.get('flair'):
                        st.write(f"**Topic/Flair:** {context['flair']}")
                    
                    if context.get('domain') and context.get('link_url'):
                        st.write(f"**Link:** [{context['domain']}]({context['link_url']})")
                    
                    if context.get('body_text') and len(context['body_text']) > 0:
                        st.write(f"**Post Text:** {context['body_text'][:400]}..." if len(context['body_text']) > 400 else context['body_text'])
                
                elif post['selftext'] and len(post['selftext']) > 0:
                    st.write(f"**Post Text:** {post['selftext'][:300]}..." if len(post['selftext']) > 300 else post['selftext'])
                
                # Show top comments
                if post.get('top_comments'):
                    st.write("**💬 Top Comments:**")
                    for j, comment in enumerate(post['top_comments']):
                        comment_text = comment['body']
                        if len(comment_text) > 150:
                            st.write(f"**{j+1}.** {comment_text[:150]}...")
                        else:
                            st.write(f"**{j+1}.** {comment_text}")
                        st.write(f"   *By u/{comment['author']} ({comment['score']} points)*")
                        st.write("")
                
                st.write(f"[View Full Discussion on Reddit]({post['url']})")
            
            with col2:
                st.markdown("### 📊 Engagement")
                st.metric("Upvotes", f"{post['score']:,}")
                st.metric("Comments", post['num_comments'])
                st.write(f"**Posted:** {post['time_ago']}")
                st.write(f"**By:** u/{post['author']}")
                
                # Content opportunity indicator
                if post['score'] > 1000:
                    st.success("🔥 High Engagement")
                elif post['num_comments'] > post['score'] / 5:
                    st.warning("🌶️ Controversial")
                elif post['score'] > 500:
                    st.info("📈 Popular")

# Streamlit UI - Remove old title since we have header
# st.title and st.markdown for subtitle removed - now in header

# Sidebar for API key and settings
st.sidebar.header("🔑 AI Configuration")

api_key = st.sidebar.text_input(
    "OpenAI API Key", 
    type="password",
    help="Enter your OpenAI API key. It will only be used for this session and not stored anywhere.",
    placeholder="sk-..."
)

if not api_key:
    st.sidebar.warning("⚠️ Enter your OpenAI API key to enable AI analysis")
    ai_enabled = False
else:
    st.sidebar.success("✅ AI analysis enabled")
    ai_enabled = True

analysis_mode = st.sidebar.radio(
    "Analysis Mode",
    options=["🤖 AI Analysis (Full Intelligence)", "📊 Basic Analysis (No AI)"],
    help="AI analysis provides deep insights, basic analysis is faster but less sophisticated"
)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Subreddit Settings")

# Input section
col1, col2 = st.columns([2, 1])

with col1:
    subreddit_input = st.text_input(
        "Enter Subreddit Name", 
        value="Conservative",
        placeholder="e.g., Conservative, politics, news, technology",
        help="Enter just the subreddit name without 'r/'"
    )

with col2:
    st.write("**Quick Select:**")
    suggested_subs = ["Conservative", "politics", "news", "worldnews", "technology", "business"]
    
    selected_sub = st.selectbox("Popular subreddits:", [""] + suggested_subs)
    if selected_sub:
        subreddit_input = selected_sub

# Speed optimization options
st.markdown("### ⚡ Speed Settings")
col3, col4 = st.columns([1, 1])

with col3:
    category_choice = st.selectbox(
        "Choose Category to Analyze",
        options=["All (Slower)", "Hot Posts Only", "Top Posts Only", "Rising Posts Only"],
        index=1,  # Default to "Hot Posts Only" 
        help="Analyzing one category is much faster"
    )

with col4:
    num_posts = st.slider("Posts per category", 2, 10, 5, help="Fewer posts = faster analysis")

# AI Analysis Settings
if ai_enabled:
    st.info(f"🤖 AI Analysis will analyze {num_posts} posts from {category_choice.lower()}")
else:
    st.info(f"📊 Basic analysis will show {num_posts} posts from {category_choice.lower()}")

# Analysis button
if st.button("🔍 Analyze Subreddit", type="primary") or 'reddit_analysis' not in st.session_state:
    
    if not subreddit_input:
        st.warning("Please enter a subreddit name")
        st.stop()
    
    st.info(f"Analyzing r/{subreddit_input} - Fetching top, hot, and rising posts...")
    
    # Initialize results
    analysis_results = {
        'subreddit': subreddit_input,
        'top': [],
        'hot': [],
        'rising': []
    }
    
    progress_bar = st.progress(0)
    
    # Determine which categories to fetch based on user choice
    if category_choice == "Hot Posts Only":
        categories = ['hot']
    elif category_choice == "Top Posts Only":
        categories = ['top']
    elif category_choice == "Rising Posts Only":
        categories = ['rising']
    else:
        categories = ['top', 'hot', 'rising']
    
    # Fetch data for selected categories
    for i, category in enumerate(categories):
        st.text(f"Fetching {category} posts from r/{subreddit_input}...")
        
        posts = get_reddit_posts(subreddit_input, category, num_posts)
        
        if posts:
            category_posts = []
            
            for j, post in enumerate(posts):
                post_data = post['data']
                post_id = post_data['id']
                
                # Show progress for AI analysis
                if ai_enabled and analysis_mode.startswith("🤖"):
                    st.text(f"🤖 AI analyzing post {j+1}/{len(posts)}: {post_data['title'][:50]}...")
                
                # Get additional context and top comments
                post_context = get_post_content(post_id, subreddit_input)
                top_comments = get_top_comments(post_id, subreddit_input, 3)
                
                # Prepare content for AI analysis
                post_content_full = post_data.get('selftext', '') or post_context.get('body_text', '')
                if post_context.get('domain') and not post_content_full:
                    post_content_full = f"Link post to: {post_context.get('domain')} - {post_context.get('link_url', '')}"
                
                # AI Analysis if enabled
                ai_analysis = None
                if ai_enabled and analysis_mode.startswith("🤖"):
                    ai_analysis = ai_analyze_post(
                        post_data['title'], 
                        post_content_full, 
                        top_comments,
                        api_key
                    )
                
                category_posts.append({
                    'title': post_data['title'],
                    'score': post_data['score'],
                    'num_comments': post_data['num_comments'],
                    'author': post_data['author'],
                    'url': f"https://reddit.com{post_data['permalink']}",
                    'created_utc': post_data['created_utc'],
                    'selftext': post_data.get('selftext', ''),
                    'top_comments': top_comments,
                    'post_context': post_context,
                    'ai_analysis': ai_analysis,
                    'time_ago': format_time_ago(post_data['created_utc'])
                })
            
            analysis_results[category] = category_posts
        
        progress_bar.progress((i + 1) / len(categories))
        time.sleep(0.5)  # Reduced delay
    
    progress_bar.empty()
    st.session_state['reddit_analysis'] = analysis_results
    
    total_posts = sum(len(analysis_results[cat]) for cat in categories)
    if total_posts > 0:
        st.success(f"✅ Successfully analyzed {total_posts} posts from r/{subreddit_input}")
    else:
        st.error(f"❌ Could not fetch posts from r/{subreddit_input}. Check subreddit name and try again.")

# Display results
if 'reddit_analysis' in st.session_state and st.session_state['reddit_analysis']:
    data = st.session_state['reddit_analysis']
    subreddit = data['subreddit']
    
    # Overview metrics
    st.header(f"📊 r/{subreddit} Analysis Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    all_posts = data['top'] + data['hot'] + data['rising']
    if all_posts:
        total_upvotes = sum(post['score'] for post in all_posts)
        total_comments = sum(post['num_comments'] for post in all_posts)
        avg_score = total_upvotes / len(all_posts)
        
        with col1:
            st.metric("Total Posts Analyzed", len(all_posts))
        with col2:
            st.metric("Total Upvotes", f"{total_upvotes:,}")
        with col3:
            st.metric("Total Comments", f"{total_comments:,}")
        with col4:
            st.metric("Avg Score", f"{avg_score:.0f}")
    
    # Content opportunities
    opportunities = analyze_content_opportunities(data)
    if opportunities:
        st.header("🎯 Content Opportunities")
        for opp in opportunities[:5]:
            st.write(opp)
    
    # Detailed analysis by category
    st.header("📝 Detailed Post Analysis")
    
    # Create tabs for each category (only show tabs that have data)
    available_tabs = []
    if data.get('hot'):
        available_tabs.append(("🔥 Hot Posts", "hot", "Currently Popular"))
    if data.get('top'):
        available_tabs.append(("⭐ Top Posts", "top", "Most Upvoted"))
    if data.get('rising'):
        available_tabs.append(("📈 Rising Posts", "rising", "Gaining Momentum"))
    
    if len(available_tabs) == 1:
        # Only one category - no need for tabs
        tab_name, category_key, description = available_tabs[0]
        st.subheader(f"{tab_name} ({description})")
        display_posts(data[category_key], subreddit)
    else:
        # Multiple categories - use tabs
        tab_objects = st.tabs([tab[0] for tab in available_tabs])
        
        for i, (tab_name, category_key, description) in enumerate(available_tabs):
            with tab_objects[i]:
                st.subheader(f"{description}")
                display_posts(data[category_key], subreddit)

else:
    st.info("👆 Enter a subreddit name and click 'Analyze Subreddit' to start discovering content opportunities")

# Footer with Shorthand Studios branding
st.markdown("""
<div class="footer">
    <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 1rem;">
        <div style="color: white; font-size: 1.5rem; font-weight: 700;">SHORTHAND STUDIOS</div>
    </div>
    <div style="color: #b5def2; margin-bottom: 1rem;">AI-Powered Content Intelligence Platform</div>
""", unsafe_allow_html=True)

if ai_enabled:
    st.markdown("""
    <div style="color: white;">
        <strong>🤖 AI-Powered Content Discovery:</strong><br>
        • <strong>Intelligent summaries</strong> decode vague titles and memes<br>
        • <strong>Sentiment analysis</strong> reveals nuanced conservative opinions<br>
        • <strong>Content angles</strong> optimized for Daily Wire audience<br>
        • <strong>Trend predictions</strong> help you get ahead of stories<br>
        • <strong>Show prep</strong> tailored for Ben, Matt, and Michael's styles<br>
        • <strong>Risk assessment</strong> flags potential controversies<br>
        • <strong>Social content</strong> ideas based on comment patterns
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="color: white;">
        <strong>💡 Basic Content Discovery:</strong><br>
        • <strong>Hot posts</strong> show what's currently engaging the community<br>
        • <strong>Top posts</strong> reveal what content performs best overall<br>
        • <strong>Rising posts</strong> help you spot trends early<br>
        • Add your OpenAI API key in the sidebar for AI-powered insights!
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
    <div style="color: #e5dec8; margin-top: 1rem; font-size: 0.9rem;">
        Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
</div>
""", unsafe_allow_html=True)