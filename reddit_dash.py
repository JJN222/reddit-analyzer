import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import openai
import os

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
    max-width: 1400px;
    padding-left: 3rem;
    padding-right: 3rem;
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
    st.session_state.selected_subreddit = "TrueCrime"

# Reddit API headers
HEADERS = {
    'User-Agent': 'web:shorthand-reddit-analyzer:v1.0.0 (by /u/Ruhtorikal)',
    'Accept': 'application/json',
}

# ============ API KEY MANAGEMENT ============

def get_api_keys():
    """Get API keys from environment variables"""
    openai_key = os.getenv('OPENAI_API_KEY', '')
    youtube_key = os.getenv('YOUTUBE_API_KEY', '')
    return openai_key, youtube_key

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

def calculate_trending_score(upvotes, comments, created_utc):
    """Calculate a trending score based on upvotes, comments, and recency"""
    # Convert created_utc to hours ago
    hours_ago = (datetime.now() - datetime.fromtimestamp(created_utc)).total_seconds() / 3600
    
    # Prevent division by zero and give recent posts a boost
    time_factor = 1 / (hours_ago + 2)  # +2 to prevent extreme values for very new posts
    
    # Engagement score
    engagement = upvotes + (comments * 2)  # Comments weighted more heavily
    
    # Calculate trending score
    trending_score = engagement * time_factor
    
    return int(trending_score)


def analyze_with_ai(post_title, post_content, comments, api_key, creator_name, image_url=None):
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

def generate_hashtags(title, subreddit, creator_name):
    """Generate relevant hashtags for social media"""
    # Clean creator name for hashtag
    creator_tag = creator_name.replace(" ", "")
    
    # Extract key words from title (simple approach)
    words = title.lower().split()
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'is', 'are', 'was', 'were'}
    key_words = [w for w in words if w not in stop_words and len(w) > 3][:3]
    
    hashtags = [
        f"#{creator_tag}",
        f"#{subreddit}",
        "#reaction",
        "#commentary"
    ]
    
    for word in key_words:
        hashtags.append(f"#{word}")
    
    return " ".join(hashtags[:8])  # Limit to 8 hashtags

def display_posts(posts, subreddit, api_key=None, creator_name="Bailey Sarian"):
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
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Score", f"{score:,}")
            with col2:
                st.metric("Comments", f"{num_comments:,}")
            with col3:
                st.metric("Hours ago", f"{int((datetime.now() - created).total_seconds() / 3600)}")
            with col4:
                trending = calculate_trending_score(score, num_comments, post_data.get('created_utc', 0))
                st.metric("🔥 Trending", f"{trending:,}")            
            
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
                    
                    with col2:
                        # Add trending score to export data
                        trending = calculate_trending_score(score, num_comments, post_data.get('created_utc', 0))
                        hashtags = generate_hashtags(title, subreddit, creator_name)

                        export_data = f"""# {creator_name} Analysis for Reddit Post

                        **Post:** {title}
                        **Subreddit:** r/{subreddit}
                        **Score:** {score:,} upvotes
                        **Comments:** {num_comments:,}
                        **Trending Score:** 🔥 {trending:,}
                        **Author:** u/{author}
                        **Reddit Link:** https://reddit.com{permalink}
                        **Hashtags:** {hashtags}

                        ## AI Analysis:
                        {analysis}

                        ## Post Content:
                        {selftext[:500] if selftext else 'No text content'}

                        Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}
                        """

                        # Add to session state for batch export
                        if 'analyzed_posts' not in st.session_state:
                            st.session_state.analyzed_posts = []
                        if export_data not in st.session_state.analyzed_posts:
                            st.session_state.analyzed_posts.append(export_data)
                        
                        st.download_button(
                            label="📄 Export",
                            data=export_data,
                            file_name=f"{creator_name.replace(' ', '_')}_{title[:30].replace(' ', '_')}_analysis.txt",
                            mime="text/plain",
                            key=f"export_{post_id}_{i}",
                            help="Download this analysis as a text file"
                        )
                    
                    if is_image:
                        st.info("🖼️ Image analysis included")
                    
                    st.write(analysis)

                    # Add hashtags
                    hashtags = generate_hashtags(title, subreddit, creator_name)
                    st.markdown(f"**#️⃣ Suggested Hashtags:** `{hashtags}`")

                    # Add copy helper section
                    st.markdown("**📋 Quick Copy:**")
                    col1, col2 = st.columns(2)

                    with col1:
                        st.text_area("Hashtags:", hashtags, height=50, key=f"copy_hashtags_{post_id}_{i}")

                    with col2:
                        # Try to extract a hot take from the analysis
                        if "🔥 HOT TAKE:" in analysis:
                            hot_take_start = analysis.find("🔥 HOT TAKE:") + len("🔥 HOT TAKE:")
                            hot_take_end = analysis.find("\n", hot_take_start)
                            if hot_take_end != -1:
                                hot_take = analysis[hot_take_start:hot_take_end].strip()
                                st.text_area("Hot Take:", hot_take, height=50, key=f"copy_hot_take_{post_id}_{i}")

                    

                    st.markdown('</div>', unsafe_allow_html=True)
                elif analysis:
                    st.error(analysis)
            else:
                st.markdown('<div class="ai-analysis">', unsafe_allow_html=True)
                st.markdown(f"### 🤖 AI Analysis for {creator_name}")
                st.info("⚠️ AI analysis unavailable - configure API keys in environment variables")
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.write(f"[View on Reddit](https://reddit.com{permalink})")

# ============ YOUTUBE API FUNCTIONS ============

def get_youtube_trending(api_key=None, region='US', max_results=15):
    """Get trending videos from YouTube"""
    if not api_key:
        # Return sample trending topics without API
        sample_trending = [
            {
                "title": "BREAKING: Major Political Development Shakes Washington", 
                "channel": "Political News Network", 
                "views": "2.3M views", 
                "published": "2 hours ago", 
                "description": "Latest updates on the developing political situation that could change everything...",
                "video_id": "sample1",
                "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/mqdefault.jpg"
            },
            {
                "title": "SHOCKING Truth About Latest Government Scandal EXPOSED", 
                "channel": "Truth Commentary", 
                "views": "1.8M views", 
                "published": "4 hours ago", 
                "description": "Deep dive investigation reveals concerning details about recent government actions...",
                "video_id": "sample2",
                "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/mqdefault.jpg"
            },
            {
                "title": "This Changes EVERYTHING - Full Analysis & Breakdown", 
                "channel": "Conservative Analysis", 
                "views": "956K views", 
                "published": "1 day ago", 
                "description": "Complete breakdown of recent events and their long-term implications...",
                "video_id": "sample3",
                "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/mqdefault.jpg"
            }
        ]
        st.info("📺 Showing sample trending videos (Configure YouTube API key for live data)")
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
                    'description': snippet.get('description', '')[:200] + '...' if snippet.get('description') else '',
                    'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', '')
                }
                trending_videos.append(video_data)
            
            st.success("✅ Retrieved live YouTube trending data")
            return trending_videos
        elif response.status_code == 403:
            st.warning("⚠️ YouTube API key invalid or quota exceeded. Showing sample data.")
            return get_youtube_trending()
        elif response.status_code == 400:
            st.warning("⚠️ YouTube API request error. Check your API key permissions.")
            return get_youtube_trending()
        else:
            st.warning(f"⚠️ YouTube API error {response.status_code}. Using sample data.")
            return get_youtube_trending()
            
    except Exception as e:
        st.warning(f"⚠️ YouTube API temporarily unavailable: {str(e)[:50]}... Using sample data.")
        return get_youtube_trending()

def search_youtube_videos(query, api_key=None, max_results=10, timeframe="week", search_type="video"):
    """Search YouTube for videos by topic/keywords with timeframe, or search by channel"""
    if not api_key:
        # Return sample search results with timeframe context
        timeframe_text = {
            "2days": "last 2 days",
            "week": "last week", 
            "month": "last month"
        }.get(timeframe, "recent")
        
        if search_type == "channel":
            sample_results = [
                {
                    "title": f"Latest Upload from {query}", 
                    "channel": query, 
                    "views": "523K views", 
                    "published": "1 day ago", 
                    "description": f"Recent content from {query} channel...",
                    "video_id": "sample1",
                    "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/mqdefault.jpg"
                },
                {
                    "title": f"Popular Video from {query}", 
                    "channel": query, 
                    "views": "1.2M views", 
                    "published": "3 days ago", 
                    "description": f"Top performing content from {query}...",
                    "video_id": "sample2",
                    "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/mqdefault.jpg"
                }
            ]
            st.info(f"📺 Showing sample videos from '{query}' channel (Configure YouTube API key for live search)")
        else:
            sample_results = [
                {
                    "title": f"BREAKING: Latest Analysis on {query}", 
                    "channel": "Political Commentary Pro", 
                    "views": "523K views", 
                    "published": "1 day ago", 
                    "description": f"In-depth analysis of {query} and its implications from {timeframe_text}...",
                    "video_id": "sample1",
                    "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/mqdefault.jpg"
                },
                {
                    "title": f"URGENT UPDATE: {query} - What You Need to Know", 
                    "channel": "News Analysis Channel", 
                    "views": "1.2M views", 
                    "published": "3 hours ago", 
                    "description": f"Breaking developments regarding {query} from {timeframe_text}...",
                    "video_id": "sample2",
                    "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/mqdefault.jpg"
                }
            ]
            st.info(f"📺 Showing sample search results for '{query}' from {timeframe_text} (Configure YouTube API key for live search)")
        
        return sample_results
    
    try:
        if search_type == "channel":
            # First, search for the channel
            search_url = "https://www.googleapis.com/youtube/v3/search"
            channel_params = {
                'part': 'snippet',
                'q': query,
                'type': 'channel',
                'maxResults': 1,
                'key': api_key
            }
            
            channel_response = requests.get(search_url, params=channel_params, timeout=15)
            
            if channel_response.status_code == 200:
                channel_data = channel_response.json()
                if channel_data.get('items'):
                    channel_id = channel_data['items'][0]['id']['channelId']
                    
                    # Now get videos from this channel
                    video_params = {
                        'part': 'snippet',
                        'channelId': channel_id,
                        'type': 'video',
                        'order': 'date',
                        'maxResults': max_results,
                        'key': api_key
                    }
                    
                    # Add timeframe filter
                    if timeframe == "2days":
                        published_after = (datetime.now() - timedelta(days=2)).isoformat() + 'Z'
                    elif timeframe == "week":
                        published_after = (datetime.now() - timedelta(days=7)).isoformat() + 'Z'
                    elif timeframe == "month":
                        published_after = (datetime.now() - timedelta(days=30)).isoformat() + 'Z'
                    else:
                        published_after = (datetime.now() - timedelta(days=7)).isoformat() + 'Z'
                    
                    video_params['publishedAfter'] = published_after
                    
                    video_response = requests.get(search_url, params=video_params, timeout=15)
                    
                    if video_response.status_code == 200:
                        video_data = video_response.json()
                        search_results = []
                        
                        for item in video_data.get('items', []):
                            snippet = item.get('snippet', {})
                            
                            video_data_item = {
                                'title': snippet.get('title', 'No title'),
                                'channel': snippet.get('channelTitle', 'Unknown Channel'),
                                'published': snippet.get('publishedAt', 'Unknown'),
                                'video_id': item.get('id', {}).get('videoId', ''),
                                'description': snippet.get('description', '')[:200] + '...' if snippet.get('description') else '',
                                'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', '')
                            }
                            search_results.append(video_data_item)
                        
                        st.success(f"✅ Found live videos from '{query}' channel from {timeframe}")
                        return search_results
        else:
            # Calculate publishedAfter based on timeframe
            if timeframe == "2days":
                published_after = (datetime.now() - timedelta(days=2)).isoformat() + 'Z'
            elif timeframe == "week":
                published_after = (datetime.now() - timedelta(days=7)).isoformat() + 'Z'
            elif timeframe == "month":
                published_after = (datetime.now() - timedelta(days=30)).isoformat() + 'Z'
            else:
                published_after = (datetime.now() - timedelta(days=7)).isoformat() + 'Z'
            
            # YouTube API v3 search endpoint
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'order': 'relevance',
                'maxResults': max_results,
                'key': api_key,
                'publishedAfter': published_after
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
                
                st.success(f"✅ Found live YouTube results for '{query}' from {timeframe}")
                return search_results
        
        # Fallback for API errors
        if search_type == "channel":
            st.warning("⚠️ Channel search failed. Showing sample results.")
            return search_youtube_videos(query, search_type=search_type)
        else:
            st.warning("⚠️ Video search failed. Showing sample results.")
            return search_youtube_videos(query, timeframe=timeframe)
            
    except Exception as e:
        st.warning(f"⚠️ YouTube search temporarily unavailable: {str(e)[:50]}... Using sample data.")
        return search_youtube_videos(query, timeframe=timeframe, search_type=search_type)

def get_youtube_comments(video_id, api_key=None, max_results=20):
    """Get comments from a YouTube video"""
    if not api_key:
        # Return sample comments
        sample_comments = [
            {"author": "TruthSeeker2024", "text": "This is exactly what I've been saying! Finally someone gets it.", "likes": 127},
            {"author": "SkepticalViewer", "text": "I disagree with this take. Here's why this analysis is flawed...", "likes": 89},
            {"author": "CasualObserver", "text": "Great breakdown! Really helps me understand the situation better.", "likes": 45},
            {"author": "ControversialTakes", "text": "This is going to trigger so many people but it's the truth", "likes": 203},
            {"author": "ThoughtfulCritic", "text": "While I appreciate the perspective, I think there are some nuances missing here", "likes": 67}
        ]
        st.info("📝 Showing sample comments (Configure YouTube API key for live comment data)")
        return sample_comments
    
    try:
        url = "https://www.googleapis.com/youtube/v3/commentThreads"
        params = {
            'part': 'snippet',
            'videoId': video_id,
            'maxResults': max_results,
            'order': 'relevance',
            'key': api_key
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            comments = []
            
            for item in data.get('items', []):
                snippet = item.get('snippet', {}).get('topLevelComment', {}).get('snippet', {})
                
                comment_data = {
                    'author': snippet.get('authorDisplayName', 'Unknown'),
                    'text': snippet.get('textDisplay', 'No text'),
                    'likes': int(snippet.get('likeCount', 0))
                }
                comments.append(comment_data)
            
            st.success(f"✅ Retrieved {len(comments)} live comments")
            return comments
        elif response.status_code == 403:
            st.warning("⚠️ Comments disabled or API quota exceeded. Showing sample comments.")
            return [
                {"author": "TruthSeeker2024", "text": "This is exactly what I've been saying! Finally someone gets it.", "likes": 127},
                {"author": "SkepticalViewer", "text": "I disagree with this take. Here's why this analysis is flawed...", "likes": 89},
                {"author": "CasualObserver", "text": "Great breakdown! Really helps me understand the situation better.", "likes": 45},
                {"author": "ControversialTakes", "text": "This is going to trigger so many people but it's the truth", "likes": 203},
                {"author": "ThoughtfulCritic", "text": "While I appreciate the perspective, I think there are some nuances missing here", "likes": 67}
            ]
        else:
            st.warning(f"⚠️ Comments API error {response.status_code}. Using sample comments.")
            return [
                {"author": "TruthSeeker2024", "text": "This is exactly what I've been saying! Finally someone gets it.", "likes": 127},
                {"author": "SkepticalViewer", "text": "I disagree with this take. Here's why this analysis is flawed...", "likes": 89},
                {"author": "CasualObserver", "text": "Great breakdown! Really helps me understand the situation better.", "likes": 45},
                {"author": "ControversialTakes", "text": "This is going to trigger so many people but it's the truth", "likes": 203},
                {"author": "ThoughtfulCritic", "text": "While I appreciate the perspective, I think there are some nuances missing here", "likes": 67}
            ]
            
    except Exception as e:
        st.warning(f"⚠️ Comments temporarily unavailable: {str(e)[:50]}... Using sample data.")
        return [
            {"author": "TruthSeeker2024", "text": "This is exactly what I've been saying! Finally someone gets it.", "likes": 127},
            {"author": "SkepticalViewer", "text": "I disagree with this take. Here's why this analysis is flawed...", "likes": 89},
            {"author": "CasualObserver", "text": "Great breakdown! Really helps me understand the situation better.", "likes": 45},
            {"author": "ControversialTakes", "text": "This is going to trigger so many people but it's the truth", "likes": 203},
            {"author": "ThoughtfulCritic", "text": "While I appreciate the perspective, I think there are some nuances missing here", "likes": 67}
        ]

def analyze_video_comments_with_ai(comments, video_title, creator_name, api_key):
    """Analyze YouTube video comments for creator insights"""
    if not api_key:
        return None
    
    import openai
    openai.api_key = api_key
    
    # Prepare top comments for analysis
    comment_texts = []
    for i, comment in enumerate(comments[:10], 1):
        comment_texts.append(f"{i}. {comment['author']} ({comment['likes']} likes): {comment['text'][:150]}...")
    
    comments_text = "\n".join(comment_texts)
    
    prompt = f"""Analyze these YouTube video comments for {creator_name}'s content strategy:

Video: "{video_title}"
Top Comments:
{comments_text}

Provide analysis for {creator_name}:

💭 AUDIENCE SENTIMENT: Overall mood and feelings in the comments (angry, supportive, confused, etc.)
🔥 CONTROVERSIAL POINTS: What aspects are people most divided on?
🎯 {creator_name.upper()} OPPORTUNITY: How {creator_name} could address these comments or create follow-up content
📱 COMMENT THEMES: Top 3 recurring themes or talking points in the comments
🗣️ AUDIENCE QUESTIONS: What questions are viewers asking that {creator_name} could answer?
📊 ENGAGEMENT STRATEGY: How {creator_name} could respond to maximize engagement
💡 CONTENT IDEAS: 2-3 video ideas based on what the audience is discussing

Focus on what the audience is actually saying and how {creator_name} could use these insights."""
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            timeout=30
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Comment Analysis Error: {str(e)}"

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
    ["🌊 Reddit Analysis", "📺 YouTube Intelligence"],
    key="platform_select"
)

st.sidebar.markdown("---")

st.sidebar.header("⚙️ Creator Settings")
creator_name = st.sidebar.text_input(
    "🎙️ Creator/Show",
    value="Bailey Sarian",
    placeholder="e.g., Bailey Sarian, True Crime Creator, YouTuber",
    key="creator_name_input"
)

st.sidebar.markdown("---")


st.sidebar.markdown("---")

# Get API keys from environment variables
api_key, youtube_api_key = get_api_keys()

# API status - lower priority, less emphasized
with st.sidebar.expander("🔑 API Status", expanded=False):
    if api_key:
        st.success("✅ AI analysis enabled")
    else:
        st.error("❌ AI analysis unavailable")
    
    if youtube_api_key:
        st.success("✅ YouTube live data enabled")
    else:
        st.info("📺 Using sample data")

# ============ MAIN CONTENT ============

if platform == "📺 YouTube Intelligence":
    st.header("📺 YouTube Intelligence Center")
    
    
    tab1, tab2 = st.tabs(["🔥 Trending Videos", "🔍 Video Search"])
    
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
                    with st.expander(f"#{i}: {video['title'][:60]}{'...' if len(video['title']) > 60 else ''}", expanded=False):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**Channel:** {video['channel']}")
                            st.write(f"**Views:** {video['views']}")
                            st.write(f"**Published:** {video['published']}")
                            if video.get('description'):
                                st.write(f"**Description:** {video['description']}")
                        
                        with col2:
                            if video.get('thumbnail'):
                                st.image(video['thumbnail'], width=100)
                        
                        # Creator reaction analysis for each video
                        if api_key:
                            if st.button(f"🎯 {creator_name} Reaction Ideas", key=f"reaction_trending_{i}"):
                                with st.spinner(f"🤖 Analyzing reaction opportunities for {creator_name}..."):
                                    reaction_prompt = f"""Analyze this trending YouTube video for {creator_name}'s reaction content:

Title: {video['title']}
Channel: {video['channel']}
Views: {video['views']}
Description: {video.get('description', 'No description')}

Provide {creator_name}'s reaction strategy:

🎬 REACTION VIDEO TITLE: Catchy title for {creator_name}'s reaction video
🎯 {creator_name.upper()} ANGLE: How {creator_name} would uniquely react based on their personality/brand
🔥 HOT TAKES: 3 specific points {creator_name} would likely make during the reaction
💡 OPENING HOOK: How {creator_name} should start the reaction to grab attention
⏰ BEST MOMENTS: Which parts of the original video to focus on for maximum impact
📱 SOCIAL CLIPS: 2-3 short clips perfect for TikTok/Instagram from the reaction
🎭 ENGAGEMENT STRATEGY: How to get viewers commenting and sharing"""
                                    
                                    try:
                                        import openai
                                        openai.api_key = api_key
                                        
                                        response = openai.ChatCompletion.create(
                                            model="gpt-3.5-turbo",
                                            messages=[{"role": "user", "content": reaction_prompt}],
                                            max_tokens=700,
                                            timeout=30
                                        )
                                        
                                        st.markdown('<div class="ai-analysis">', unsafe_allow_html=True)
                                        st.write(response.choices[0].message.content)
                                        st.markdown('</div>', unsafe_allow_html=True)
                                    except Exception as e:
                                        st.error(f"AI Analysis Error: {str(e)}")
                        
                        if video.get('video_id') and youtube_api_key and not video['video_id'].startswith('sample'):
                            st.video(f"https://www.youtube.com/watch?v={video['video_id']}")
    
    with tab2:
        st.subheader("🔍 YouTube Video Search")
        st.info("💡 Search YouTube for videos by topic/keywords or find videos from specific channels")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search_query = st.text_input("Search YouTube:", placeholder="e.g., 'Biden speech', 'Sydney Sweeney', or channel name")
        with col2:
            search_type = st.selectbox("Search Type", ["Videos by Topic", "Videos by Channel"], key="search_type")
        with col3:
            search_timeframe = st.selectbox("Timeframe", ["Last 2 Days", "Last Week", "Last Month"], key="youtube_timeframe")
        
        # Convert timeframe to API parameter
        timeframe_map = {
            "Last 2 Days": "2days",
            "Last Week": "week", 
            "Last Month": "month"
        }
        timeframe_param = timeframe_map.get(search_timeframe, "week")
        search_type_param = "channel" if search_type == "Videos by Channel" else "video"
        
        if st.button("🔍 Search Videos", key="search_youtube") and search_query:
            with st.spinner(f"🔍 Searching YouTube for '{search_query}' from {search_timeframe.lower()}..."):
                search_results = search_youtube_videos(search_query, youtube_api_key, timeframe=timeframe_param, search_type=search_type_param)
                
                if search_results:
                    # Store search results in session state
                    st.session_state.youtube_search_results = search_results
                    st.session_state.youtube_search_query = search_query
                    st.session_state.youtube_search_timeframe = search_timeframe
                    st.session_state.youtube_search_type = search_type
                else:
                    search_context = f"channel '{search_query}'" if search_type == "Videos by Channel" else f"'{search_query}'"
                    st.error(f"❌ No videos found for {search_context} from {search_timeframe.lower()}. Try different keywords or timeframe.")
        
        # Display search results if they exist in session state
        if 'youtube_search_results' in st.session_state and st.session_state.youtube_search_results:
            search_results = st.session_state.youtube_search_results
            search_query = st.session_state.youtube_search_query
            search_timeframe = st.session_state.youtube_search_timeframe
            search_type = st.session_state.youtube_search_type
            
            search_context = f"channel '{search_query}'" if search_type == "Videos by Channel" else f"'{search_query}'"
            st.success(f"✅ Found {len(search_results)} videos for {search_context} from {search_timeframe.lower()}")
            
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
                            st.image(video['thumbnail'], width=80)
                    
                    if video.get('video_id') and youtube_api_key and not video['video_id'].startswith('sample'):
                        st.video(f"https://www.youtube.com/watch?v={video['video_id']}")
                    
                    # Action buttons
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        # Creator reaction analysis for individual videos
                        if api_key:
                            if st.button(f"🎯 {creator_name} Reaction Ideas", key=f"analyze_video_{i}"):
                                with st.spinner(f"🤖 Analyzing reaction opportunities for {creator_name}..."):
                                    reaction_prompt = f"""Analyze this YouTube video for {creator_name}'s reaction content:

Title: {video['title']}
Channel: {video['channel']}
Description: {video.get('description', 'No description')}
Search Context: Found when searching for "{search_query}" from {search_timeframe.lower()}

Provide {creator_name}'s reaction strategy:

🎬 REACTION VIDEO TITLE: Catchy title for {creator_name}'s reaction video
🎯 {creator_name.upper()} ANGLE: How {creator_name} would uniquely react based on their personality/brand
🔥 HOT TAKES: 3 specific points {creator_name} would likely make during the reaction
💡 OPENING HOOK: How {creator_name} should start the reaction to grab attention
⏰ BEST MOMENTS: Which parts of the original video to focus on for maximum impact
📱 SOCIAL CLIPS: 2-3 short clips perfect for TikTok/Instagram from the reaction
🎭 ENGAGEMENT STRATEGY: How to get viewers commenting and sharing"""
                                    
                                    try:
                                        import openai
                                        openai.api_key = api_key
                                        
                                        response = openai.ChatCompletion.create(
                                            model="gpt-3.5-turbo",
                                            messages=[{"role": "user", "content": reaction_prompt}],
                                            max_tokens=700,
                                            timeout=30
                                        )
                                        
                                        # Store analysis in session state
                                        analysis_key = f"reaction_analysis_{i}"
                                        st.session_state[analysis_key] = response.choices[0].message.content
                                        
                                    except Exception as e:
                                        st.session_state[f"reaction_analysis_{i}"] = f"AI Analysis Error: {str(e)}"
                        else:
                            st.info("⚠️ AI analysis unavailable - configure OpenAI API key")
                    
                    with col_b:
                        # Comment analysis
                        if api_key and video.get('video_id'):
                            if st.button(f"💬 Analyze Comments", key=f"comments_{i}"):
                                with st.spinner(f"🤖 Analyzing comments for {creator_name}..."):
                                    comments = get_youtube_comments(video['video_id'], youtube_api_key)
                                    
                                    if comments:
                                        # Store comments in session state
                                        st.session_state[f"comments_data_{i}"] = comments
                                        
                                        # AI analysis of comments
                                        comment_analysis = analyze_video_comments_with_ai(comments, video['title'], creator_name, api_key)
                                        st.session_state[f"comment_analysis_{i}"] = comment_analysis
                                    else:
                                        st.session_state[f"comment_analysis_{i}"] = "No comments available for analysis"
                        else:
                            st.info("⚠️ Comment analysis unavailable - configure API keys")
                    
                    # Display stored reaction analysis
                    if f"reaction_analysis_{i}" in st.session_state:
                        st.markdown('<div class="ai-analysis">', unsafe_allow_html=True)
                        st.markdown(f"### 🎯 {creator_name} Reaction Strategy")
                        st.write(st.session_state[f"reaction_analysis_{i}"])
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Display stored comment analysis
                    if f"comment_analysis_{i}" in st.session_state:
                        analysis = st.session_state[f"comment_analysis_{i}"]
                        
                        if f"comments_data_{i}" in st.session_state:
                            comments = st.session_state[f"comments_data_{i}"]
                            st.write("**📝 Top Comments:**")
                            if isinstance(comments, list) and comments:
                                for j, comment in enumerate(comments[:5], 1):
                                    st.write(f"{j}. **{comment['author']}** ({comment['likes']} ❤️): {comment['text'][:100]}...")
                            else:
                                st.write("No comments available to display")
                        
                        if analysis and not analysis.startswith("Comment Analysis Error"):
                            st.markdown('<div class="ai-analysis">', unsafe_allow_html=True)
                            st.markdown(f"### 💬 Comment Analysis for {creator_name}")
                            st.write(analysis)
                            st.markdown('</div>', unsafe_allow_html=True)
                        elif analysis:
                            st.error(analysis)

elif platform == "🌊 Reddit Analysis":
    st.header("🌊 Reddit Content Analysis")
    
    # Initialize batch export session state
    if 'analyzed_posts' not in st.session_state:
        st.session_state.analyzed_posts = []
    
    # Create a single column layout for all controls
    col1, _ = st.columns([2, 1])
    
    with col1:
        subreddit_input = st.text_input(
            "Enter Subreddit Name",
            value=st.session_state.selected_subreddit,
            placeholder="e.g., TrueCrime, serialkillers, UnresolvedMysteries",
            key="main_subreddit_input"
        )
        
        # Settings - match width of subreddit input
        selected_category = st.selectbox("Post Category", ["Hot Posts Only", "Top Posts Only", "Rising Posts Only", "All Categories (Slower)"], key="category_select")
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
                        ["TrueCrime", "serialkillers", "UnresolvedMysteries", "MorbidReality", "Mystery", "ColdCases", "RBI", "LetsNotMeet", "nosleep", "creepy"],
                        default=["TrueCrime", "serialkillers"],
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
                                    display_posts(posts, subreddit, api_key, creator_name)
                            else:
                                display_posts(search_results, search_subreddits[0], api_key, creator_name)
                        else:
                            st.error(f"❌ No posts found for '{search_query}'. Try different keywords or subreddits.")
        
        # Analyze button right after Advanced Search
        if st.button("🔍 ANALYZE SUBREDDIT", type="primary", key="analyze_main_btn", use_container_width=True):
            if not subreddit_input:
                st.warning("Please enter a subreddit name")
            else:
                st.session_state.should_analyze = True
                st.session_state.subreddit_to_analyze = subreddit_input
    
    # Popular Subreddits
    st.write("**📊 Popular Subreddits:**")
    popular_subreddits = [
        ("TrueCrime", "🔍"), ("AskReddit", "🤷"), ("funny", "😂"), ("todayilearned", "🧠"),
        ("worldnews", "🌍"), ("technology", "💻"), ("movies", "🎬"), ("television", "📺"),
        ("music", "🎵"), ("gaming", "🎮"), ("sports", "⚽"), ("news", "📰"),
        ("science", "🔬"), ("politics", "🗳️"), ("relationships", "💕"), ("food", "🍕"),
        ("fitness", "💪"), ("travel", "✈️"), ("books", "📚"), ("photography", "📸")
    ]
    
    cols = st.columns(4)
    for i, (subreddit, emoji) in enumerate(popular_subreddits):
        col = cols[i % 4]
        with col:
            if st.button(f"{emoji} {subreddit}", key=f"btn_{subreddit}_{i}"):
                st.session_state.selected_subreddit = subreddit
                st.rerun()
    
    # Batch export section
    if 'analyzed_posts' in st.session_state and st.session_state.analyzed_posts:
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 2, 1])
        with col3:
            all_analyses = "\n\n" + "="*50 + "\n\n".join(st.session_state.analyzed_posts)
            st.download_button(
                label=f"📦 Export All ({len(st.session_state.analyzed_posts)} posts)",
                data=all_analyses,
                file_name=f"{creator_name}_batch_export_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                help="Download all analyzed posts in one file"
            )

    # Post Analysis section - full width
    st.markdown("---")
    st.markdown("### 📊 Post Analysis")
    
    # Check if we should analyze
    if hasattr(st.session_state, 'should_analyze') and st.session_state.should_analyze:
        st.session_state.should_analyze = False
        subreddit_to_analyze = st.session_state.subreddit_to_analyze
        
        st.info(f"🔍 Analyzing r/{subreddit_to_analyze}...")
        
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
            with st.spinner(f"Fetching {category} posts from r/{subreddit_to_analyze}..."):
                posts = get_reddit_posts(subreddit_to_analyze, category, post_limit)
                
                if posts:
                    all_posts_found = True
                    
                    st.subheader(f"{category_name} - r/{subreddit_to_analyze}")
                    display_posts(posts, subreddit_to_analyze, api_key if api_key else None, creator_name)
                else:
                    st.error(f"❌ Could not fetch {category} posts from r/{subreddit_to_analyze}")

        if not all_posts_found:
            st.error(f"❌ Could not fetch any posts from r/{subreddit_to_analyze}. Try a different subreddit.")
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

elif platform == "🎬 Show Planner":
    st.header("🎬 Show Planner")
    
    if not st.session_state.saved_posts:
        st.info("📝 Save some Reddit posts first to create show concepts!")
    else:
        tab1, tab2 = st.tabs(["➕ Create Show", "📋 My Shows"])
        
        with tab1:
            st.subheader("🎬 Create New Show Concept")
            
            show_title = st.text_input("Show Title", placeholder="e.g., 'Bailey Sarian True Crime Deep Dive'", key="show_title_input")
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