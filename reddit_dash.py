import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
import openai

# Configure Streamlit page
st.set_page_config(
    page_title="Shorthand Studios - Reddit Content Intelligence",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS for Shorthand Studios branding
st.markdown("""
<style>
    :root {
        --shorthand-blue: #b5def2;
        --shorthand-cream: #e5dec8;
        --shorthand-dark: #322e25;
    }
    
    .main-header {
        background-color: var(--shorthand-blue);
        padding: 2rem 0;
        margin: -1rem -1rem 2rem -1rem;
        text-align: center;
        border-bottom: 3px solid var(--shorthand-dark);
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
    
    .css-1d391kg {
        background-color: var(--shorthand-cream) !important;
    }
    
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
    }
    
    .footer {
        background: var(--shorthand-dark);
        color: white;
        padding: 2rem;
        margin: 2rem -1rem -1rem -1rem;
        text-align: center;
        border-top: 3px solid var(--shorthand-blue);
    }
    
    .ai-analysis {
        background-color: #f0f8ff;
        border-left: 4px solid var(--shorthand-blue);
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .risk-low { color: #2e7d32; font-weight: bold; }
    .risk-medium { color: #ed6c02; font-weight: bold; }
    .risk-high { color: #d32f2f; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <div class="logo-text">SHORTHAND STUDIOS</div>
    <div class="subtitle">AI-Powered Reddit Content Intelligence Platform</div>
</div>
""", unsafe_allow_html=True)

# Reddit API headers
HEADERS = {
    'User-Agent': 'web:shorthand-reddit-analyzer:v1.0.0 (by /u/Ruhtorikal)',
    'Accept': 'application/json',
}

def get_reddit_posts(subreddit, category="hot", limit=5):
    """Get posts from specified subreddit and category with enhanced cloud compatibility"""
    urls_to_try = [
        f"https://www.reddit.com/r/{subreddit}/{category}.json",
        f"https://old.reddit.com/r/{subreddit}/{category}.json", 
        f"https://np.reddit.com/r/{subreddit}/{category}.json",
        f"https://gateway.reddit.com/desktopapi/v1/subreddits/{subreddit}",
        f"https://api.reddit.com/r/{subreddit}/{category}",
    ]
    
    # Enhanced headers for cloud deployment
    headers_variants = [
        {
            'User-Agent': 'web:shorthand-reddit-analyzer:v1.0.0 (by /u/Ruhtorikal)',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        },
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.reddit.com/',
        },
        {
            'User-Agent': 'RedditAnalyzer/1.0 (by /u/Ruhtorikal)',
            'Accept': 'application/json',
        }
    ]
    
    for url in urls_to_try:
        for headers in headers_variants:
            try:
                time.sleep(4)  # Longer delay for cloud
                params = {'limit': limit, 'raw_json': 1, 't': 'day'}
                
                # Try with session for better connection handling
                import requests
                session = requests.Session()
                session.headers.update(headers)
                
                response = session.get(url, params=params, timeout=25, allow_redirects=True)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if 'data' in data and 'children' in data['data'] and data['data']['children']:
                            return data['data']['children']
                    except:
                        # Try parsing as different format
                        continue
                        
                elif response.status_code == 403:
                    continue  # Try next combination
                elif response.status_code == 429:
                    time.sleep(15)  # Rate limited, wait longer
                    continue
                elif response.status_code == 503:
                    time.sleep(10)  # Service unavailable
                    continue
                    
            except Exception as e:
                continue
    
    return []

def get_top_comments(subreddit, post_id, limit=3):
    """Get top comments for a specific post with enhanced cloud compatibility"""
    urls_to_try = [
        f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json",
        f"https://old.reddit.com/r/{subreddit}/comments/{post_id}.json",
        f"https://np.reddit.com/r/{subreddit}/comments/{post_id}.json"
    ]
    
    headers_variants = [
        {
            'User-Agent': 'web:shorthand-reddit-analyzer:v1.0.0 (by /u/Ruhtorikal)',
            'Accept': 'application/json',
        },
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }
    ]
    
    for url in urls_to_try:
        for headers in headers_variants:
            try:
                time.sleep(3)
                response = requests.get(url, headers=headers, timeout=20)
                
                if response.status_code == 200:
                    data = response.json()
                    if len(data) > 1 and 'data' in data[1] and 'children' in data[1]['data']:
                        comments = []
                        for comment in data[1]['data']['children'][:limit]:
                            if comment['kind'] == 't1' and 'body' in comment['data']:
                                comments.append({
                                    'body': comment['data']['body'],
                                    'score': comment['data']['score'],
                                    'author': comment['data'].get('author', '[deleted]')
                                })
                        return comments
            except:
                continue
    return []

def analyze_with_ai(post_title, post_content, comments, api_key, image_url=None):
    """Analyze post and comments with OpenAI, including image analysis"""
    if not api_key:
        return None
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Prepare content for analysis
        content = f"Post Title: {post_title}\n"
        if post_content and post_content != post_title:
            content += f"Post Content: {post_content[:500]}...\n"
        
        content += "Top Comments:\n"
        for i, comment in enumerate(comments[:3], 1):
            content += f"{i}. {comment['body'][:200]}...\n"
        
        # Create messages array
        messages = []
        
        if image_url:
            # If there's an image, use vision model
            prompt = f"""Analyze this Reddit post (including the image) and comments for Daily Wire content strategy. Focus on creating content that would work for Ben Shapiro and Matt Walsh's shows:

{content}

First, describe what you see in the image, then provide analysis in this format:
🖼️ IMAGE DESCRIPTION: What the image shows and its relevance
📝 SUMMARY: What this post is really about (1-2 sentences)
💭 CONSERVATIVE SENTIMENT: How conservatives are feeling about this topic based on comments
🎯 BEN SHAPIRO ANGLE: Facts, logic, constitutional/legal perspective for Ben's show
📺 MATT WALSH ANGLE: Traditional values, cultural commentary angle for Matt's show  
📈 TREND POTENTIAL: High/Medium/Low - will this topic gain momentum?
⚠️ CONTENT RISK: Low/Medium/High controversy potential for Daily Wire
📱 VIRAL OPPORTUNITY: Specific social media content ideas (quotes, memes, clips)

Be specific about how Daily Wire can frame this story to resonate with their conservative audience."""
            
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            })
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=600,
                timeout=30
            )
        else:
            # No image, use regular text model
            prompt = f"""Analyze this Reddit post and comments for Daily Wire content strategy. Focus on creating content that would work for Ben Shapiro and Matt Walsh's shows:

{content}

Provide analysis in this format:
📝 SUMMARY: What this post is really about (1-2 sentences)
💭 CONSERVATIVE SENTIMENT: How conservatives are feeling about this topic based on comments
🎯 BEN SHAPIRO ANGLE: Facts, logic, constitutional/legal perspective for Ben's show
📺 MATT WALSH ANGLE: Traditional values, cultural commentary angle for Matt's show  
📈 TREND POTENTIAL: High/Medium/Low - will this topic gain momentum?
⚠️ CONTENT RISK: Low/Medium/High controversy potential for Daily Wire
📱 VIRAL OPPORTUNITY: Specific social media content ideas (quotes, memes, clips)

Be specific about how Daily Wire can frame this story to resonate with their conservative audience."""

            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                timeout=20
            )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"AI Analysis Error: {str(e)}"

def display_posts(posts, subreddit, api_key=None):
    """Display posts with analysis"""
    if not posts:
        st.warning("⚠️ No posts found. This could be because:")
        st.write("• The subreddit is private or banned")
        st.write("• Reddit is experiencing issues")
        st.write("• Try a different subreddit from the list")
        return
    
    for i, post in enumerate(posts):
        post_data = post['data']
        
        # Extract post info
        title = post_data.get('title', 'No title')
        score = post_data.get('score', 0)
        num_comments = post_data.get('num_comments', 0)
        author = post_data.get('author', '[deleted]')
        created = datetime.fromtimestamp(post_data.get('created_utc', 0))
        permalink = post_data.get('permalink', '')
        post_id = post_data.get('id', '')
        selftext = post_data.get('selftext', '')
        url = post_data.get('url', '')
        flair = post_data.get('link_flair_text', '')
        
        # Check if this is an image post
        image_url = None
        is_image = False
        if url and any(url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
            image_url = url
            is_image = True
        elif 'preview' in post_data and 'images' in post_data['preview']:
            # Reddit hosted image
            try:
                image_url = post_data['preview']['images'][0]['source']['url'].replace('&amp;', '&')
                is_image = True
            except:
                pass
        
        with st.expander(f"#{i+1}: {title[:80]}{'...' if len(title) > 80 else ''}", expanded=False):
            # Basic post info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Score", f"{score:,}")
            with col2:
                st.metric("Comments", f"{num_comments:,}")
            with col3:
                st.metric("Hours ago", f"{int((datetime.now() - created).total_seconds() / 3600)}")
            
            st.write(f"**Author:** u/{author}")
            if flair:
                st.write(f"**Flair:** {flair}")
            
            # Post content
            if is_image and image_url:
                st.write("**Image Post:**")
                st.image(image_url, width=400)
            elif selftext and len(selftext) > 50:
                st.write("**Post Content:**")
                st.write(selftext[:400] + "..." if len(selftext) > 400 else selftext)
            elif url and url != f"https://www.reddit.com{permalink}":
                st.write(f"**Link:** {url}")
            
            # Get and display comments
            with st.spinner("Fetching comments..."):
                comments = get_top_comments(subreddit, post_id, 3)
            
            if comments:
                st.write("**Top Comments:**")
                for j, comment in enumerate(comments, 1):
                    st.write(f"{j}. **{comment['author']}** ({comment['score']} points):")
                    st.write(f"   {comment['body'][:200]}{'...' if len(comment['body']) > 200 else ''}")
            
            # AI Analysis
            if api_key:
                with st.spinner("🤖 AI analyzing content..."):
                    analysis = analyze_with_ai(title, selftext, comments, api_key, image_url if is_image else None)
                    if analysis and not analysis.startswith("AI Analysis Error"):
                        st.markdown('<div class="ai-analysis">', unsafe_allow_html=True)
                        st.markdown("### 🤖 AI Analysis")
                        if is_image:
                            st.info("🖼️ Image analysis included using GPT-4 Vision")
                        st.write(analysis)
                        st.markdown('</div>', unsafe_allow_html=True)
                    elif analysis:
                        st.error(analysis)
            
            st.write(f"[View on Reddit](https://reddit.com{permalink})")
            st.markdown("---")

# Add deployment detection
import os
IS_CLOUD = os.getenv('RENDER') or os.getenv('HEROKU') or os.getenv('VERCEL')

# Sidebar
st.sidebar.header("🔑 AI Configuration")
api_key = st.sidebar.text_input("OpenAI API Key", type="password", placeholder="sk-...")

if api_key:
    st.sidebar.success("✅ AI analysis enabled")
    analysis_mode = "🤖 AI Analysis (Full Intelligence)"
else:
    st.sidebar.warning("⚠️ Enter your OpenAI API key to enable AI analysis")
    analysis_mode = "📊 Basic Analysis (No AI)"

st.sidebar.write(f"**Current Mode:** {analysis_mode}")

# Show deployment status
if IS_CLOUD:
    st.sidebar.info("🌐 Running on cloud deployment")
    st.sidebar.write("Reddit may block some requests from cloud IPs. If posts don't load, try different subreddits.")
else:
    st.sidebar.info("💻 Running locally")

st.sidebar.markdown("---")

# Settings
st.sidebar.header("⚙️ Analysis Settings")
categories = ["Hot Posts Only", "Top Posts Only", "Rising Posts Only", "All Categories (Slower)"]
selected_category = st.sidebar.selectbox("Post Category", categories)

post_limit = st.sidebar.slider("Posts per category", 2, 10, 5)

st.sidebar.markdown("---")

# Main content
st.header("📊 Reddit Content Analysis")

# Subreddit input
col1, col2 = st.columns([3, 2])

with col1:
    subreddit_input = st.text_input(
        "Enter Subreddit Name", 
        value="Conservative",
        placeholder="e.g., Conservative, Politics, Movies"
    )

with col2:
    st.write("**Quick Select:**")
    suggested_subs = [
        "Conservative", "Politics", "Movies", "Television", 
        "NoStupidQuestions", "OutOfTheLoop", "PopCultureChat", 
        "PublicFreakout", "UnpopularOpinion", "Conspiracy"
    ]
    selected_sub = st.selectbox("Popular subreddits:", [""] + suggested_subs)
    if selected_sub:
        subreddit_input = selected_sub

# Analysis button
if st.button("🔍 Analyze Subreddit", type="primary"):
    if not subreddit_input:
        st.warning("Please enter a subreddit name")
    else:
        st.info(f"🔍 Analyzing r/{subreddit_input}...")
        
        # Determine which categories to fetch
        if selected_category == "Hot Posts Only":
            categories_to_fetch = [("hot", "🔥 Hot Posts")]
        elif selected_category == "Top Posts Only":
            categories_to_fetch = [("top", "👑 Top Posts")]
        elif selected_category == "Rising Posts Only":
            categories_to_fetch = [("rising", "📈 Rising Posts")]
        else:
            categories_to_fetch = [("hot", "🔥 Hot Posts"), ("top", "👑 Top Posts"), ("rising", "📈 Rising Posts")]
        
        # Fetch and display posts
        all_posts_found = False
        
        for category, category_name in categories_to_fetch:
            with st.spinner(f"Fetching {category} posts from r/{subreddit_input}..."):
                posts = get_reddit_posts(subreddit_input, category, post_limit)
            
            if posts:
                all_posts_found = True
                st.subheader(f"{category_name} - r/{subreddit_input}")
                display_posts(posts, subreddit_input, api_key if api_key else None)
            else:
                st.error(f"❌ Could not fetch {category} posts from r/{subreddit_input}")
        
        if not all_posts_found:
            st.error(f"❌ Could not fetch any posts from r/{subreddit_input}. Try a different subreddit.")
            st.info("**Suggested alternatives:** Politics, Movies, Television, AskReddit, WorldNews")

# Footer
st.markdown("""
<div class="footer">
    <div style="color: white; font-size: 1.5rem; font-weight: 700;">SHORTHAND STUDIOS</div>
    <div style="color: #b5def2;">AI-Powered Content Intelligence Platform</div>
</div>
""", unsafe_allow_html=True)
