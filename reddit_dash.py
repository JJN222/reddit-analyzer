import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import openai
import os

# Try to import pytrends, but don't fail if it's not available
try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False

# Configure Streamlit page
st.set_page_config(
    page_title="Shorthand Studios - Content Intelligence Platform",
    page_icon="🎯",
    layout="wide"
)

# Enhanced CSS for Shorthand Studios website styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

:root {
    --shorthand-blue: #b5def2;
    --shorthand-cream: #e5dec8;
    --shorthand-dark: #322e25;
    --shorthand-white: #ffffff;
    --shorthand-gray: #f8f9fa;
    --shorthand-accent: #4a90e2;
}

.main .block-container {
    padding-top: 1rem;
    max-width: 1200px;
}

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

.css-1d391kg {
    background: linear-gradient(180deg, var(--shorthand-cream) 0%, #f0f4f8 100%);
    border-right: 1px solid #e0e6ed;
}

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

.footer {
    background: linear-gradient(135deg, var(--shorthand-dark) 0%, #1a1612 100%);
    color: white;
    padding: 3rem 2rem;
    margin: 3rem -1rem -1rem -1rem;
    text-align: center;
    border-radius: 20px 20px 0 0;
    font-family: 'Inter', sans-serif;
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

# Reddit API headers
HEADERS = {
    'User-Agent': 'web:shorthand-reddit-analyzer:v1.0.0 (by /u/Ruhtorikal)',
    'Accept': 'application/json',
}

# ============ REDDIT FUNCTIONS ============

def save_post(post_data, analysis, creator_name, subreddit):
    """Save a post with its analysis for show planning"""
    saved_post = {
        'id': f"{post_data['id']}_{creator_name}",
        'title': post_data['title'],
        'score': post_data['score'],
        'num_comments': post_data['num_comments'],
        'subreddit': subreddit,
        'creator': creator_name,
        'analysis': analysis,
        'permalink': post_data['permalink'],
        'saved_at': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'image_url': post_data.get('image_url', ''),
        'content': post_data.get('selftext', '')[:200] + '...' if post_data.get('selftext') else ''
    }
    
    existing_ids = [p['id'] for p in st.session_state.saved_posts]
    if saved_post['id'] not in existing_ids:
        st.session_state.saved_posts.append(saved_post)
        return True
    return False

def get_reddit_posts(subreddit, category="hot", limit=5):
    """Get posts from specified subreddit and category"""
    urls_to_try = [
        f"https://www.reddit.com/r/{subreddit}/{category}.json",
        f"https://old.reddit.com/r/{subreddit}/{category}.json",
        f"https://np.reddit.com/r/{subreddit}/{category}.json",
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
                time.sleep(2)
                params = {'limit': limit, 'raw_json': 1}
                response = requests.get(url, headers=headers, params=params, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data and 'children' in data['data'] and data['data']['children']:
                        return data['data']['children']
                elif response.status_code == 429:
                    time.sleep(5)
                    continue
            except:
                continue
    
    return []

def get_top_comments(subreddit, post_id, limit=3):
    """Get top comments for a specific post"""
    url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json"
    
    try:
        time.sleep(2)
        response = requests.get(url, headers=HEADERS, timeout=15)
        
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
        pass
    
    return []

def search_reddit_by_keywords(query, subreddits, limit=5):
    """Search Reddit for posts containing specific keywords"""
    all_results = []
    
    # Search all of Reddit if specified
    if subreddits == ["all"]:
        try:
            search_url = "https://www.reddit.com/search.json"
            params = {
                'q': query,
                'sort': 'top',
                't': 'day',
                'limit': limit * 2,
                'type': 'link'
            }
            time.sleep(2)
            response = requests.get(search_url, headers=HEADERS, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'children' in data['data']:
                    posts = data['data']['children']
                    for post in posts:
                        post['data']['source_subreddit'] = post['data']['subreddit']
                    all_results.extend(posts)
        except:
            # Fallback to popular subreddits if all Reddit search fails
            subreddits = ["Conservative", "Politics", "News", "WorldNews", "AskReddit", "PublicFreakout"]
    
    # Search specific subreddits
    if subreddits != ["all"]:
        for subreddit in subreddits:
            try:
                search_url = f"https://www.reddit.com/r/{subreddit}/search.json"
                params = {
                    'q': query,
                    'restrict_sr': 'true',
                    'sort': 'top',
                    't': 'day',
                    'limit': limit
                }
                time.sleep(2)
                response = requests.get(search_url, headers=HEADERS, params=params, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data and 'children' in data['data']:
                        posts = data['data']['children']
                        for post in posts:
                            post['data']['source_subreddit'] = subreddit
                        all_results.extend(posts)
            except:
                continue
    
    # Sort by score and return top results
    all_results.sort(key=lambda x: x['data']['score'], reverse=True)
    return all_results[:limit * 3]

def analyze_with_ai(post_title, post_content, comments, api_key, creator_name="Daily Wire", image_url=None):
    """Analyze post and comments with OpenAI"""
    if not api_key:
        return None
    
    # Use legacy OpenAI method for Railway compatibility
    import openai
    openai.api_key = api_key
    
    # Prepare content for analysis
    content = f"Post Title: {post_title}\n"
    if post_content and post_content != post_title:
        content += f"Post Content: {post_content[:500]}...\n"
    
    content += "Top Comments:\n"
    for i, comment in enumerate(comments[:3], 1):
        content += f"{i}. {comment['body'][:200]}...\n"
    
    creator_prompt = f"""Analyze this Reddit post for {creator_name}'s content strategy. First, consider what you know about {creator_name}'s personality, political positions, communication style, and typical takes. Then analyze the content accordingly:

{content}

Provide analysis in this format:

📝 SUMMARY: What this post is really about (1-2 sentences)

💭 COMMENTER SENTIMENT: How the commenters in this thread are feeling (angry, excited, confused, etc.)

📰 NEWS CONTEXT: Connect this to current events, trending topics, or recent news stories

📊 NORMAL TAKE: What {creator_name} would typically say about this topic, based on their known positions and style

🔥 HOT TAKE: {creator_name}'s most provocative, exaggerated take designed for viral content - stay true to their personality but make it bold and shareable

📱 SOCIAL CONTENT: Specific YouTube titles and social media content ideas that {creator_name} would actually use

⚠️ CONTROVERSY LEVEL: How polarizing this content would be for {creator_name} (1-10 scale)

Important: Base your analysis on {creator_name}'s actual known personality, political positions, and communication style."""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": creator_prompt}],
            max_tokens=600,
            timeout=20
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Analysis Error: {str(e)}"

def display_posts(posts, subreddit, api_key=None):
    """Display posts with analysis"""
    if not posts:
        st.warning("⚠️ No posts found. Try a different subreddit.")
        return
    
    for i, post in enumerate(posts):
        post_data = post['data']
        title = post_data.get('title', 'No title')
        score = post_data.get('score', 0)
        num_comments = post_data.get('num_comments', 0)
        author = post_data.get('author', '[deleted]')
        created = datetime.fromtimestamp(post_data.get('created_utc', 0))
        permalink = post_data.get('permalink', '')
        post_id = post_data.get('id', '')
        selftext = post_data.get('selftext', '')
        url = post_data.get('url', '')
        
        # Check if this is an image post
        image_url = None
        is_image = False
        if url and any(url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
            image_url = url
            is_image = True
        elif 'preview' in post_data and post_data['preview'] is not None and 'images' in post_data['preview']:
            try:
                image_url = post_data['preview']['images'][0]['source']['url'].replace('&amp;', '&')
                is_image = True
            except:
                pass
        
        post_data['image_url'] = image_url
        
        with st.expander(f"#{i+1}: {title[:80]}{'...' if len(title) > 80 else ''}", expanded=False):
            # Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Score", f"{score:,}")
            with col2:
                st.metric("Comments", f"{num_comments:,}")
            with col3:
                st.metric("Hours ago", f"{int((datetime.now() - created).total_seconds() / 3600)}")
            
            st.write(f"**Author:** u/{author}")
            
            # Display content based on type
            if is_image and image_url:
                st.write("**Image Post:**")
                st.image(image_url, width=400)
            elif selftext and len(selftext) > 50:
                st.write("**Post Content:**")
                st.write(selftext[:400] + "..." if len(selftext) > 400 else selftext)
            elif url and url != f"https://www.reddit.com{permalink}":
                st.write(f"**Link:** {url}")
            
            # Get comments
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
                    analysis = analyze_with_ai(title, selftext, comments, api_key, creator_name, image_url if is_image else None)
                
                if analysis and not analysis.startswith("AI Analysis Error"):
                    st.markdown('<div class="ai-analysis">', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"### 🤖 AI Analysis for {creator_name}")
                    with col2:
                        if st.button("💾 Save", key=f"save_{post_id}_{i}", help="Save this post for show planning"):
                            if save_post(post_data, analysis, creator_name, subreddit):
                                st.success("✅ Saved!")
                            else:
                                st.info("Already saved")
                    
                    if is_image:
                        st.info("🖼️ Image analysis included")
                    
                    st.write(analysis)
                    st.markdown('</div>', unsafe_allow_html=True)
                elif analysis:
                    st.error(analysis)
            else:
                st.markdown('<div class="ai-analysis">', unsafe_allow_html=True)
                st.markdown(f"### 🤖 AI Analysis for {creator_name}")
                st.info("🔑 Enter your OpenAI API key in the sidebar to enable AI analysis")
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.write(f"[View on Reddit](https://reddit.com{permalink})")

# ============ YOUTUBE API FUNCTIONS ============

def get_youtube_trending(api_key=None, region='US', max_results=15):
    """Get trending videos from YouTube"""
    if not api_key:
        # Return sample trending topics without API
        sample_trending = [
            {"title": "Breaking: Major Political Development", "channel": "News Channel", "views": "2.3M views", "published": "2 hours ago"},
            {"title": "SHOCKING Truth About Latest Scandal", "channel": "Commentary Channel", "views": "1.8M views", "published": "4 hours ago"},
            {"title": "This Changes Everything - Full Analysis", "channel": "Political Commentary", "views": "956K views", "published": "1 day ago"},
            {"title": "EXPOSED: What They Don't Want You to Know", "channel": "Investigative News", "views": "743K views", "published": "6 hours ago"},
            {"title": "LIVE: Breaking News Coverage", "channel": "Live News", "views": "2.1M views", "published": "3 hours ago"},
            {"title": "The Truth About Recent Events", "channel": "Truth Seekers", "views": "1.2M views", "published": "8 hours ago"},
            {"title": "Why This Matters More Than You Think", "channel": "Deep Dive", "views": "892K views", "published": "12 hours ago"},
            {"title": "URGENT: Important Update Everyone Needs", "channel": "News Updates", "views": "1.5M views", "published": "5 hours ago"}
        ]
        return sample_trending
    
    try:
        # YouTube API v3 trending videos endpoint
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            'part': 'snippet,statistics',
            'chart': 'mostPopular',
            'regionCode': region,
            'maxResults': max_results,
            'key': api_key,
            'videoCategoryId': '25'  # News & Politics category
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            trending_videos = []
            
            for item in data.get('items', []):
                snippet = item.get('snippet', {})
                stats = item.get('statistics', {})
                
                video_data = {
                    'title': snippet.get('title', 'No title'),
                    'channel': snippet.get('channelTitle', 'Unknown Channel'),
                    'views': f"{int(stats.get('viewCount', 0)):,} views" if stats.get('viewCount') else 'No views',
                    'published': snippet.get('publishedAt', 'Unknown'),
                    'video_id': item.get('id', ''),
                    'description': snippet.get('description', '')[:200] + '...' if snippet.get('description') else ''
                }
                trending_videos.append(video_data)
            
            return trending_videos
        else:
            st.warning(f"YouTube API error: {response.status_code}")
            return get_youtube_trending()  # Return sample data
            
    except Exception as e:
        st.warning(f"YouTube API temporarily unavailable: {str(e)}")
        return get_youtube_trending()  # Return sample data

def search_youtube_videos(query, api_key=None, max_results=10):
    """Search YouTube for videos by topic/keywords"""
    if not api_key:
        # Return sample search results
        sample_results = [
            {"title": f"Latest Analysis: {query}", "channel": "Political Commentary", "views": "523K views", "published": "1 day ago"},
            {"title": f"BREAKING: {query} Update", "channel": "News Channel", "views": "1.2M views", "published": "3 hours ago"},
            {"title": f"The Truth About {query}", "channel": "Deep Dive Analysis", "views": "876K views", "published": "2 days ago"},
            {"title": f"Why {query} Matters", "channel": "Commentary", "views": "432K views", "published": "1 day ago"},
            {"title": f"{query}: Full Breakdown", "channel": "News Analysis", "views": "654K views", "published": "5 hours ago"}
        ]
        return sample_results
    
    try:
        # YouTube API v3 search endpoint
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'order': 'relevance',
            'maxResults': max_results,
            'key': api_key,
            'publishedAfter': (datetime.now() - timedelta(days=7)).isoformat() + 'Z'  # Last 7 days
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            search_results = []
            
            for item in data.get('items', []):
                snippet = item.get('snippet', {})
                
                video_data = {
                    'title': snippet.get('title', 'No title'),
                    'channel': snippet.get('channelTitle', 'Unknown Channel'),
                    'published': snippet.get('publishedAt', 'Unknown'),
                    'video_id': item.get('id', {}).get('videoId', ''),
                    'description': snippet.get('description', '')[:200] + '...' if snippet.get('description') else '',
                    'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', '')
                }
                search_results.append(video_data)
            
            return search_results
        else:
            st.warning(f"YouTube API error: {response.status_code}")
            return search_youtube_videos(query)  # Return sample data
            
    except Exception as e:
        st.warning(f"YouTube search temporarily unavailable: {str(e)}")
        return search_youtube_videos(query)  # Return sample data

def analyze_youtube_trends_with_ai(trending_videos, creator_name, api_key):
    """Analyze YouTube trending videos for content opportunities"""
    if not api_key:
        return None
    
    import openai
    openai.api_key = api_key
    
    # Prepare trending video data for analysis
    video_titles = []
    for i, video in enumerate(trending_videos[:8], 1):
        video_titles.append(f"{i}. \"{video['title']}\" by {video['channel']} ({video['views']})")
    
    videos_text = "\n".join(video_titles)
    
    prompt = f"""Analyze these trending YouTube videos for {creator_name}'s content opportunities:

{videos_text}

For the top 3 most relevant trends, provide:

📺 TRENDING VIDEO TOPIC: [Main topic/theme]
🎯 {creator_name.upper()} ANGLE: How {creator_name} could respond, react, or create similar content
🔥 CONTENT IDEA: Specific video title for {creator_name}'s channel
📱 FORMAT: Best format (Reaction, Analysis, Response, Original Take)
⏰ URGENCY: How time-sensitive this trend is (1-10)
💡 HOOK: Opening line or angle to grab attention
🎬 SERIES POTENTIAL: Could this become multiple videos?"""
    
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

# ============ SIDEBAR CONFIGURATION ============

st.sidebar.header("🎯 Content Intelligence Hub")

platform = st.sidebar.selectbox(
    "📊 Choose Platform",
    ["🌊 Reddit Analysis", "📺 YouTube Intelligence", "🎬 Show Planner", "💾 Saved Content"],
    key="platform_select"
)

st.sidebar.markdown("---")

st.sidebar.header("🔑 AI Configuration")
api_key = st.sidebar.text_input("OpenAI API Key", type="password", placeholder="sk-...", key="api_key_input")

if api_key:
    st.sidebar.success("✅ AI analysis enabled")
else:
    st.sidebar.warning("⚠️ Enter your OpenAI API key to enable AI analysis")

st.sidebar.markdown("---")

st.sidebar.header("🎬 YouTube API (Optional)")
youtube_api_key = st.sidebar.text_input("YouTube API Key", type="password", placeholder="AIza...", key="youtube_api_input", help="Optional: For live YouTube data")

if youtube_api_key:
    st.sidebar.success("✅ YouTube API enabled")
else:
    st.sidebar.info("💡 YouTube API key enables live trending data")

st.sidebar.markdown("---")

st.sidebar.header("⚙️ Creator Settings")
creator_name = st.sidebar.text_input(
    "🎙️ Creator/Show",
    value="Ben Shapiro",
    placeholder="e.g., Ben Shapiro, Matt Walsh, Kid Rock",
    key="creator_name_input"
)

st.sidebar.markdown("---")

# Show metrics
if st.session_state.saved_posts:
    st.sidebar.metric("💾 Saved Posts", len(st.session_state.saved_posts))
if st.session_state.show_concepts:
    st.sidebar.metric("🎬 Show Concepts", len(st.session_state.show_concepts))

# ============ MAIN CONTENT ============

if platform == "📺 YouTube Intelligence":
    st.header("📺 YouTube Intelligence Center")
    
    st.info("💡 **YouTube Intelligence:** Analyze trending videos and search for content opportunities. YouTube API key is optional - works with sample data too!")
    
    tab1, tab2, tab3 = st.tabs(["🔥 Trending Videos", "🔍 Video Search", "🎯 Content Ideas"])
    
    with tab1:
        st.subheader("🔥 What's Trending on YouTube")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            if st.button("🔄 Get Trending Videos", key="get_youtube_trending"):
                with st.spinner("Fetching trending YouTube videos..."):
                    trending_videos = get_youtube_trending(youtube_api_key)
                    st.session_state.trending_videos = trending_videos
        
        with col2:
            region = st.selectbox("Region", ["US", "CA", "GB", "AU", "DE", "FR"], key="youtube_region")
        
        if 'trending_videos' in st.session_state:
            trending_videos = st.session_state.trending_videos
            
            if trending_videos:
                st.success(f"✅ Found {len(trending_videos)} trending videos")
                
                for i, video in enumerate(trending_videos, 1):
                    st.markdown(f"""
                    <div class="trend-card">
                        <strong>#{i}</strong> &nbsp;&nbsp;
                        <span style="font-size: 1.1rem; font-weight: 500;">{video['title']}</span><br>
                        <small style="color: #666;">by {video['channel']} • {video['views']} • {video['published']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if video.get('video_id') and youtube_api_key:
                        st.video(f"https://www.youtube.com/watch?v={video['video_id']}")
                
                if api_key:
                    st.markdown("### 🤖 AI Content Analysis")
                    if st.button("🎯 Analyze for Content Opportunities", key="analyze_youtube_trends"):
                        with st.spinner("🤖 Analyzing trending videos..."):
                            analysis = analyze_youtube_trends_with_ai(trending_videos, creator_name, api_key)
                            
                            if analysis and not analysis.startswith("AI Analysis Error"):
                                st.markdown('<div class="ai-analysis">', unsafe_allow_html=True)
                                st.write(analysis)
                                st.markdown('</div>', unsafe_allow_html=True)
                            elif analysis:
                                st.error(analysis)
    
    with tab2:
        st.subheader("🔍 YouTube Video Search")
        st.info("💡 Search YouTube for videos by topic or keywords")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            search_query = st.text_input("Search YouTube:", placeholder="e.g., 'Biden speech', 'Trump rally', 'AI technology'")
        with col2:
            search_timeframe = st.selectbox("Timeframe", ["Last Week", "Last Month", "Last Year"], key="youtube_timeframe")
        
        if st.button("🔍 Search Videos", key="search_youtube") and search_query:
            with st.spinner(f"🔍 Searching YouTube for '{search_query}'..."):
                search_results = search_youtube_videos(search_query, youtube_api_key)
                
                if search_results:
                    st.success(f"✅ Found {len(search_results)} videos for '{search_query}'")
                    
                    for i, video in enumerate(search_results, 1):
                        with st.expander(f"#{i}: {video['title'][:60]}{'...' if len(video['title']) > 60 else ''}", expanded=False):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.write(f"**Channel:** {video['channel']}")
                                st.write(f"**Published:** {video['published']}")
                                if video.get('description'):
                                    st.write(f"**Description:** {video['description']}")
                            
                            with col2:
                                if video.get('thumbnail'):
                                    st.image(video['thumbnail'], width=120)
                            
                            if video.get('video_id') and youtube_api_key:
                                st.video(f"https://www.youtube.com/watch?v={video['video_id']}")
                            
                            # AI Analysis for individual videos
                            if api_key:
                                if st.button(f"🤖 Analyze This Video", key=f"analyze_video_{i}"):
                                    with st.spinner("🤖 Analyzing video for content opportunities..."):
                                        video_prompt = f"""Analyze this YouTube video for {creator_name}'s content strategy:

Title: {video['title']}
Channel: {video['channel']}
Description: {video.get('description', 'No description')}

Provide analysis:

📝 VIDEO TOPIC: What this video is about
🎯 {creator_name.upper()} OPPORTUNITY: How {creator_name} could respond, react, or create related content
🔥 CONTENT IDEAS: 3 specific video ideas inspired by this
📱 FORMAT: Best approach (Reaction, Response, Original Take, Debate)
💡 UNIQUE ANGLE: What {creator_name} could add that's different"""
                                        
                                        try:
                                            import openai
                                            openai.api_key = api_key
                                            
                                            response = openai.ChatCompletion.create(
                                                model="gpt-3.5-turbo",
                                                messages=[{"role": "user", "content": video_prompt}],
                                                max_tokens=600,
                                                timeout=30
                                            )
                                            
                                            st.markdown('<div class="ai-analysis">', unsafe_allow_html=True)
                                            st.write(response.choices[0].message.content)
                                            st.markdown('</div>', unsafe_allow_html=True)
                                        except Exception as e:
                                            st.error(f"AI Analysis Error: {str(e)}")
                else:
                    st.error(f"❌ No videos found for '{search_query}'. Try different keywords.")
    
    with tab3:
        st.subheader("🎯 AI Video Content Generator")
        st.info("💡 Generate video content ideas for any topic")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            content_topic = st.text_input("Video Topic:", placeholder="e.g., AI, Politics, Current Events")
        with col2:
            video_style = st.selectbox("Video Style", ["Reaction", "Analysis", "Commentary", "Debate", "Breakdown", "Response"], key="video_style")
        
        if st.button("🚀 Generate Video Ideas", key="generate_video_ideas") and content_topic and api_key:
            with st.spinner("🤖 Generating video content ideas..."):
                import openai
                openai.api_key = api_key
                
                prompt = f"""Create 5 YouTube video ideas for {creator_name} about "{content_topic}" in {video_style} style:

For each video idea, provide:

🎬 TITLE: YouTube-optimized title (under 60 characters, clickable)
📝 CONCEPT: 2-sentence video description
🎯 {creator_name.upper()} ANGLE: How {creator_name} would uniquely approach this
🎥 STRUCTURE: Basic video outline (intro, main points, conclusion)
🔥 HOOK: Opening 15 seconds to grab attention
📊 THUMBNAIL IDEA: What the thumbnail should show
⏰ OPTIMAL LENGTH: Recommended video duration
💡 SERIES POTENTIAL: Could this become multiple videos?
🎭 CALL TO ACTION: How to end the video"""
                
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=1200,
                        timeout=30
                    )
                    
                    st.markdown('<div class="ai-analysis">', unsafe_allow_html=True)
                    st.write(response.choices[0].message.content)
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"AI Analysis Error: {str(e)}")

elif platform == "🌊 Reddit Analysis":
    st.header("🌊 Reddit Content Analysis")
    
    # Main Reddit interface with all your original functionality
    col1, col2 = st.columns([2, 1])
    
    with col1:
        subreddit_input = st.text_input(
            "Enter Subreddit Name",
            value=st.session_state.selected_subreddit,
            placeholder="e.g., Conservative, Politics, Movies",
            key="main_subreddit_input"
        )
    
    # Settings
    categories = ["Hot Posts Only", "Top Posts Only", "Rising Posts Only", "All Categories (Slower)"]
    selected_category = st.selectbox("Post Category", categories, key="category_select")
    post_limit = st.slider("Posts per category", 2, 10, 5, key="post_limit_slider")
    
    # Search functionality
    with st.expander("🔍 Advanced Search"):
        search_type = st.selectbox("Search Type", ["Search by Keywords", "Browse Subreddit"], key="search_type_select")
        
        if search_type == "Search by Keywords":
            search_query = st.text_input("🔍 Search Keywords", placeholder="e.g., 'biden speech', 'trump rally'", key="keyword_search_input")
            
            search_scope = st.radio("Search Scope", ["All of Reddit", "Specific Subreddits"], key="search_scope_radio")
            
            if search_scope == "Specific Subreddits":
                search_subreddits = st.multiselect(
                    "Select Subreddits",
                    ["Conservative", "Politics", "News", "WorldNews", "PublicFreakout", "Conspiracy", "AskReddit", "Technology", "Movies", "Television"],
                    default=["Conservative", "Politics"],
                    key="search_subreddits_multi"
                )
            else:
                search_subreddits = ["all"]
            
            if st.button("🔍 Search Reddit", key="run_search_btn") and search_query:
                with st.spinner(f"🔍 Searching for '{search_query}'..."):
                    search_results = search_reddit_by_keywords(search_query, search_subreddits, post_limit)
                    
                    if search_results:
                        st.success(f"✅ Found {len(search_results)} posts matching '{search_query}'")
                        
                        # Group results by subreddit if multiple subreddits
                        if len(search_subreddits) > 1 or search_subreddits == ["all"]:
                            grouped_results = {}
                            for post in search_results:
                                subreddit = post['data']['source_subreddit']
                                if subreddit not in grouped_results:
                                    grouped_results[subreddit] = []
                                grouped_results[subreddit].append(post)
                            
                            for subreddit, posts in grouped_results.items():
                                st.subheader(f"📊 r/{subreddit} ({len(posts)} posts)")
                                display_posts(posts, subreddit, api_key)
                        else:
                            display_posts(search_results, search_subreddits[0], api_key)
                    else:
                        st.error(f"❌ No posts found for '{search_query}'. Try different keywords or subreddits.")
    
    # Popular Subreddits
    st.write("**📊 Popular Subreddits:**")
    popular_subreddits = [
        ("Conservative", "🏛️"), ("Politics", "🗳️"), ("Movies", "🎬"), ("Television", "📺"),
        ("News", "📰"), ("WorldNews", "🌍"), ("Technology", "💻"), ("AskReddit", "🤷"),
        ("Conspiracy", "🕵️"), ("PublicFreakout", "😤"), ("UnpopularOpinion", "🤔")
    ]
    
    cols = st.columns(4)
    for i, (subreddit, emoji) in enumerate(popular_subreddits):
        col = cols[i % 4]
        with col:
            if st.button(f"{emoji} {subreddit}", key=f"btn_{subreddit}_{i}"):
                st.session_state.selected_subreddit = subreddit
                subreddit_input = subreddit
    
    # Analysis button
    if st.button("🔍 Analyze Subreddit", type="primary", key="analyze_main_btn"):
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
                st.info("💡 **Tip:** Try these usually accessible subreddits: AskReddit, Technology, Movies")

elif platform == "💾 Saved Content":
    st.header("💾 Saved Content")
    
    if not st.session_state.saved_posts:
        st.info("📝 No saved posts yet. Analyze some Reddit content and save posts to get started!")
    else:
        st.success(f"✅ You have {len(st.session_state.saved_posts)} saved posts")
        
        # Group by creator
        creators = {}
        for post in st.session_state.saved_posts:
            creator = post['creator']
            if creator not in creators:
                creators[creator] = []
            creators[creator].append(post)
        
        # Display by creator
        for creator, posts in creators.items():
            with st.expander(f"🎙️ {creator} ({len(posts)} posts)", expanded=True):
                for i, post in enumerate(posts):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.write(f"**{post['title'][:60]}{'...' if len(post['title']) > 60 else ''}**")
                        st.caption(f"r/{post['subreddit']} • {post['score']} upvotes • {post['saved_at']}")
                    
                    with col2:
                        if st.button("📖 View", key=f"view_{post['id']}_{i}"):
                            st.session_state.viewing_post = post
                    
                    with col3:
                        if st.button("🗑️ Delete", key=f"delete_{post['id']}_{i}"):
                            st.session_state.saved_posts = [p for p in st.session_state.saved_posts if p['id'] != post['id']]
                            st.rerun()
        
        # Clear all button
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🗑️ Clear All", key="clear_all_btn"):
                if st.sidebar.button("⚠️ Confirm Clear All", key="confirm_clear"):
                    st.session_state.saved_posts = []
                    st.session_state.show_concepts = []
                    st.success("✅ All content cleared!")
                    st.rerun()
    
    # Show individual post viewer if selected
    if 'viewing_post' in st.session_state:
        post = st.session_state.viewing_post
        st.header(f"📖 Viewing Saved Post")
        
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("🔙 Back to List", key="back_to_list"):
                del st.session_state.viewing_post
                st.rerun()
        
        with col1:
            st.subheader(post['title'])
        
        # Post details
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Score", f"{post['score']:,}")
        with col2:
            st.metric("Comments", f"{post['num_comments']:,}")
        with col3:
            st.metric("Creator", post['creator'])
        
        st.write(f"**Subreddit:** r/{post['subreddit']}")
        st.write(f"**Saved:** {post['saved_at']}")
        
        if post['content']:
            st.write("**Content:**")
            st.write(post['content'])
        
        if post['image_url']:
            st.write("**Image:**")
            st.image(post['image_url'], width=400)
        
        # Analysis
        st.markdown('<div class="ai-analysis">', unsafe_allow_html=True)
        st.markdown(f"### 🤖 AI Analysis for {post['creator']}")
        st.write(post['analysis'])
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.write(f"[View on Reddit](https://reddit.com{post['permalink']})")

elif platform == "🎬 Show Planner":
    st.header("🎬 Show Planner")
    
    if not st.session_state.saved_posts:
        st.info("📝 Save some Reddit posts first to create show concepts!")
    else:
        tab1, tab2 = st.tabs(["➕ Create Show", "📋 My Shows"])
        
        with tab1:
            st.subheader("🎬 Create New Show Concept")
            
            show_title = st.text_input("Show Title", placeholder="e.g., 'Ben Shapiro Destroys Woke Reddit'", key="show_title_input")
            show_creator = st.selectbox("Host/Creator", list(set([post['creator'] for post in st.session_state.saved_posts])), key="show_creator_input")
            show_theme = st.text_area("Show Theme/Description", placeholder="Brief description of the show concept...", key="show_theme_textarea")
            
            st.write("**Select Posts for This Show:**")
            creator_posts = [post for post in st.session_state.saved_posts if post['creator'] == show_creator]
            
            selected_posts = []
            for i, post in enumerate(creator_posts):
                if st.checkbox(f"{post['title'][:50]}{'...' if len(post['title']) > 50 else ''}", key=f"show_post_{i}"):
                    selected_posts.append(post)
            
            if selected_posts:
                estimated_duration = len(selected_posts) * 8  # 8 minutes per segment
                st.info(f"📊 Estimated Duration: {estimated_duration} minutes ({len(selected_posts)} segments)")
                
                if st.button("🎬 Create Show Concept", key="create_show_btn") and show_title:
                    show_concept = {
                        'id': f"show_{int(time.time())}",
                        'title': show_title,
                        'creator': show_creator,
                        'theme': show_theme,
                        'posts': selected_posts,
                        'duration': estimated_duration,
                        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    
                    st.session_state.show_concepts.append(show_concept)
                    st.success(f"✅ Created show concept: '{show_title}'")
                    st.balloons()
        
        with tab2:
            if not st.session_state.show_concepts:
                st.info("📺 No show concepts yet. Create your first show!")
            else:
                for i, show in enumerate(st.session_state.show_concepts):
                    with st.expander(f"🎬 {show['title']} ({show['duration']} min)", expanded=False):
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            st.write(f"**Host:** {show['creator']}")
                            st.write(f"**Created:** {show['created_at']}")
                            if show['theme']:
                                st.write(f"**Theme:** {show['theme']}")
                        
                        with col2:
                            if st.button("📄 Export Notes", key=f"export_{show['id']}"):
                                # Generate show notes
                                notes = f"# {show['title']}\n\n"
                                notes += f"**Host:** {show['creator']}\n"
                                notes += f"**Duration:** {show['duration']} minutes\n"
                                notes += f"**Segments:** {len(show['posts'])}\n\n"
                                
                                if show['theme']:
                                    notes += f"**Show Theme:**\n{show['theme']}\n\n"
                                
                                notes += "## Segments\n\n"
                                
                                for j, post in enumerate(show['posts'], 1):
                                    notes += f"### Segment {j}: {post['title']}\n\n"
                                    notes += f"**Source:** r/{post['subreddit']}\n"
                                    notes += f"**Engagement:** {post['score']} upvotes, {post['num_comments']} comments\n\n"
                                    notes += f"**AI Analysis:**\n{post['analysis']}\n\n"
                                    notes += f"**Reddit Link:** https://reddit.com{post['permalink']}\n\n"
                                    notes += "---\n\n"
                                
                                st.download_button(
                                    label="💾 Download Show Notes",
                                    data=notes,
                                    file_name=f"{show['title'].replace(' ', '_')}_show_notes.md",
                                    mime="text/markdown",
                                    key=f"download_{show['id']}"
                                )
                        
                        with col3:
                            if st.button("🗑️ Delete", key=f"delete_show_{show['id']}"):
                                st.session_state.show_concepts = [s for s in st.session_state.show_concepts if s['id'] != show['id']]
                                st.rerun()
                        
                        # Show segments
                        st.write(f"**{len(show['posts'])} Segments:**")
                        for j, post in enumerate(show['posts'], 1):
                            st.write(f"{j}. {post['title'][:60]}{'...' if len(post['title']) > 60 else ''}")

# Footer
st.markdown("""
<div class="footer">
    <div style="color: white; font-size: 1.5rem; font-weight: 700;">SHORTHAND STUDIOS</div>
    <div style="color: #b5def2;">AI-Powered Content Intelligence Platform</div>
    <div style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.8;">
        🚀 Multi-platform analysis • 🎯 Creator-focused insights • 📊 Real-time trends
    </div>
</div>
""", unsafe_allow_html=True)