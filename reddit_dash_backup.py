import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
import openai
import os

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
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <div class="logo-text">SHORTHAND STUDIOS</div>
    <div class="subtitle">AI-Powered Reddit Content Intelligence Platform</div>
</div>
""", unsafe_allow_html=True)

# Add deployment detection
IS_CLOUD = os.getenv('RENDER') or os.getenv('HEROKU') or os.getenv('VERCEL')

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
    
    # Check if already saved
    existing_ids = [p['id'] for p in st.session_state.saved_posts]
    if saved_post['id'] not in existing_ids:
        st.session_state.saved_posts.append(saved_post)
        return True
    return False

def search_reddit_by_keywords(query, subreddits, limit=5):
    """Search Reddit for posts containing specific keywords"""
    all_results = []
    
    # Handle "All of Reddit" search
    if subreddits == ["all"]:
        try:
            # Search across all of Reddit
            search_url = "https://www.reddit.com/search.json"
            params = {
                'q': query,
                'sort': 'top',
                't': 'day',  # Top posts of the day
                'limit': limit * 2,  # Get more results since we're searching all
                'type': 'link'
            }
            
            time.sleep(2)
            response = requests.get(search_url, headers=HEADERS, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'children' in data['data']:
                    posts = data['data']['children']
                    # Add source subreddit info
                    for post in posts:
                        post['data']['source_subreddit'] = post['data']['subreddit']
                    all_results.extend(posts)
        except:
            # If all-Reddit search fails, fall back to popular subreddits
            subreddits = ["Conservative", "Politics", "News", "WorldNews", "AskReddit", "PublicFreakout"]
    
    # Search specific subreddits
    if subreddits != ["all"]:
        for subreddit in subreddits:
            try:
                # Reddit search API
                search_url = f"https://www.reddit.com/r/{subreddit}/search.json"
                params = {
                    'q': query,
                    'restrict_sr': 'true',
                    'sort': 'top',
                    't': 'day',  # Top posts of the day
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
    return all_results[:limit * 3]  # Return more results for better variety

def search_subreddits(query, limit=10):
    """Search for subreddits matching the query"""
    try:
        search_url = "https://www.reddit.com/subreddits/search.json"
        params = {
            'q': query,
            'limit': limit,
            'sort': 'relevance'
        }
        
        response = requests.get(search_url, headers=HEADERS, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'children' in data['data']:
                return data['data']['children']
    except:
        pass
    
    return []

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

def analyze_with_legacy_openai(post_title, post_content, comments, creator_name, image_url=None):
    """Fallback for older OpenAI library versions"""
    import openai
    
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
    
def analyze_with_ai(post_title, post_content, comments, api_key, creator_name="Daily Wire", image_url=None):
    """Analyze post and comments with OpenAI - using legacy method for Railway compatibility"""
    if not api_key:
        return None
    
    # Use legacy method since Railway has proxy conflicts with new OpenAI client
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
        
        # Check if this is an image post
        image_url = None
        is_image = False
        if url and any(url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
            image_url = url
            is_image = True
        elif 'preview' in post_data and 'images' in post_data['preview']:
            try:
                image_url = post_data['preview']['images'][0]['source']['url'].replace('&amp;', '&')
                is_image = True
            except:
                pass
        
        post_data['image_url'] = image_url
        
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
                    analysis = analyze_with_ai(title, selftext, comments, api_key, creator_name, image_url if is_image else None)
                    if analysis and not analysis.startswith("AI Analysis Error"):
                        st.markdown('<div class="ai-analysis">', unsafe_allow_html=True)
                        
                        # Add save button
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

# Sidebar
st.sidebar.header("🔑 AI Configuration")
api_key = st.sidebar.text_input("OpenAI API Key", type="password", placeholder="sk-...", key="api_key_input")

if api_key:
    st.sidebar.success("✅ AI analysis enabled")
else:
    st.sidebar.warning("⚠️ Enter your OpenAI API key to enable AI analysis")

st.sidebar.markdown("---")

# Podcast Production Tools
st.sidebar.header("🎙️ Podcast Production")

saved_count = len(st.session_state.saved_posts)
show_count = len(st.session_state.show_concepts)

col1, col2 = st.sidebar.columns(2)
with col1:
    st.metric("Saved Posts", saved_count)
with col2:
    st.metric("Show Concepts", show_count)

if st.sidebar.button("📋 View Saved Posts", use_container_width=True, key="view_saved_btn"):
    st.session_state.show_saved_posts = True

if st.sidebar.button("🎬 Show Planner", use_container_width=True, key="show_planner_btn"):
    st.session_state.show_planner = True

if st.sidebar.button("🗑️ Clear All Saved", use_container_width=True, key="clear_all_btn"):
    st.session_state.confirm_clear = True

if st.session_state.get('confirm_clear', False):
    st.sidebar.warning("⚠️ This will delete all saved posts and show concepts!")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("✅ Confirm", use_container_width=True, key="confirm_clear_btn"):
            st.session_state.saved_posts = []
            st.session_state.show_concepts = []
            st.session_state.confirm_clear = False
            st.success("🗑️ All data cleared!")
            st.rerun()
    with col2:
        if st.button("❌ Cancel", use_container_width=True, key="cancel_clear_btn"):
            st.session_state.confirm_clear = False
            st.rerun()

st.sidebar.markdown("---")

# Settings
st.sidebar.header("⚙️ Analysis Settings")

creator_name = st.sidebar.text_input(
    "🎙️ Creator/Show", 
    value="Ben Shapiro",
    placeholder="e.g., Ben Shapiro, Matt Walsh, Kid Rock",
    key="creator_name_input"
)

categories = ["Hot Posts Only", "Top Posts Only", "Rising Posts Only", "All Categories (Slower)"]
selected_category = st.sidebar.selectbox("Post Category", categories, key="category_select")

post_limit = st.sidebar.slider("Posts per category", 2, 10, 5, key="post_limit_slider")

st.sidebar.markdown("---")

# Search functionality
st.sidebar.header("🔍 Search Features")

search_type = st.sidebar.selectbox("Search Type", ["Search by Keywords", "Search Subreddits"], key="search_type_select")

if search_type == "Search by Keywords":
    search_query = st.sidebar.text_input(
        "🔍 Search Keywords", 
        placeholder="e.g., 'biden speech', 'trump rally'",
        key="keyword_search_input"
    )
    
    # Search scope options
    search_scope = st.sidebar.radio(
        "Search Scope",
        ["All of Reddit", "Specific Subreddits"],
        key="search_scope_radio"
    )
    
    if search_scope == "Specific Subreddits":
        search_subreddits = st.sidebar.multiselect(
            "Select Subreddits",
            ["Conservative", "Politics", "News", "WorldNews", "PublicFreakout", "Conspiracy", "AskReddit", "Technology", "Movies", "Television"],
            default=["Conservative", "Politics"],
            key="search_subreddits_multi"
        )
    else:
        # Default popular subreddits for "All of Reddit" search
        search_subreddits = ["all"]  # Reddit's r/all equivalent
        
else:
    search_query = st.sidebar.text_input(
        "🔍 Search Subreddits", 
        placeholder="e.g., 'conservative political'",
        key="subreddit_search_input"
    )

if st.sidebar.button("🔍 Run Search", use_container_width=True, key="run_search_btn") and search_query:
    st.session_state.run_search = True
    st.session_state.search_query = search_query
    st.session_state.search_type = search_type
    if search_type == "Search by Keywords":
        st.session_state.search_scope = search_scope
        st.session_state.search_subreddits = search_subreddits

st.sidebar.markdown("---")

# Popular Subreddits
st.sidebar.header("📊 Popular Subreddits")

popular_subreddits = [
    ("Conservative", "🏛️"), ("Politics", "🗳️"), ("Movies", "🎬"), ("Television", "📺"),
    ("News", "📰"), ("WorldNews", "🌍"), ("Technology", "💻"), ("AskReddit", "🤷"),
    ("Conspiracy", "🕵️"), ("PublicFreakout", "😤"), ("UnpopularOpinion", "🤔")
]

cols = st.sidebar.columns(2)
for i, (subreddit, emoji) in enumerate(popular_subreddits):
    col = cols[i % 2]
    with col:
        if st.button(f"{emoji} {subreddit}", key=f"btn_{subreddit}_{i}", use_container_width=True):
            st.session_state.selected_subreddit = subreddit

# Check for search results
if st.session_state.get('run_search', False):
    search_query = st.session_state.search_query
    search_type = st.session_state.search_type
    
    if search_type == "Search by Keywords":
        st.header(f"🔍 Search Results for: '{search_query}'")
        search_scope = st.session_state.get('search_scope', 'Specific Subreddits')
        search_subreddits = st.session_state.get('search_subreddits', ['Conservative', 'Politics'])
        
        if search_scope == "All of Reddit":
            st.info(f"🌐 Searching across all of Reddit for '{search_query}'...")
            with st.spinner(f"Searching all of Reddit for '{search_query}'..."):
                search_results = search_reddit_by_keywords(search_query, ["all"], 5)
        else:
            st.info(f"🎯 Searching in {len(search_subreddits)} specific subreddits for '{search_query}'...")
            with st.spinner(f"Searching for '{search_query}' in {len(search_subreddits)} subreddits..."):
                search_results = search_reddit_by_keywords(search_query, search_subreddits, 3)
        
        if search_results:
            st.success(f"✅ Found {len(search_results)} posts matching '{search_query}'")
            
            # Group by subreddit
            by_subreddit = {}
            for post in search_results:
                sub = post['data']['source_subreddit']
                if sub not in by_subreddit:
                    by_subreddit[sub] = []
                by_subreddit[sub].append(post)
            
            # Display results by subreddit
            for subreddit, posts in by_subreddit.items():
                st.subheader(f"📊 r/{subreddit} ({len(posts)} posts)")
                display_posts(posts, subreddit, api_key)
        else:
            st.error(f"❌ No posts found matching '{search_query}'")
            if search_scope == "All of Reddit":
                st.info("Try different keywords or check spelling")
            else:
                st.info("Try different keywords, subreddits, or search 'All of Reddit'")
    
    else:  # Search Subreddits
        st.header(f"🔍 Subreddit Search Results for: '{search_query}'")
        
        with st.spinner(f"Searching for subreddits matching '{search_query}'..."):
            subreddit_results = search_subreddits(search_query, 10)
        
        if subreddit_results:
            st.success(f"✅ Found {len(subreddit_results)} subreddits")
            
            for subreddit in subreddit_results:
                sub_data = subreddit['data']
                sub_name = sub_data.get('display_name', 'Unknown')
                sub_title = sub_data.get('title', 'No title')
                sub_desc = sub_data.get('public_description', 'No description')
                sub_subscribers = sub_data.get('subscribers', 0)
                
                with st.expander(f"r/{sub_name} - {sub_title} ({sub_subscribers:,} members)", expanded=False):
                    st.write(f"**Description:** {sub_desc}")
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Members:** {sub_subscribers:,}")
                        st.write(f"**Over 18:** {'Yes' if sub_data.get('over18', False) else 'No'}")
                    with col2:
                        if st.button(f"📊 Analyze r/{sub_name}", key=f"analyze_{sub_name}_{i}"):
                            st.session_state.selected_subreddit = sub_name
                            st.session_state.run_search = False
                            st.rerun()
        else:
            st.error(f"❌ No subreddits found matching '{search_query}'")
    
    if st.button("🔙 Back to Main Analysis", key="back_from_search_btn"):
        st.session_state.run_search = False
        st.rerun()

# Check for saved posts or show planner views
elif st.session_state.get('show_saved_posts', False):
    st.header("📋 Saved Posts for Podcast Production")
    
    if not st.session_state.saved_posts:
        st.info("No saved posts yet. Analyze some posts and click the 💾 Save button!")
    else:
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
                for j, post in enumerate(posts):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.write(f"**{post['title'][:60]}{'...' if len(post['title']) > 60 else ''}**")
                        st.write(f"r/{post['subreddit']} • {post['score']} upvotes • {post['saved_at']}")
                    
                    with col2:
                        if st.button("📖 View", key=f"view_{post['id']}_{j}"):
                            st.session_state.viewing_post = post
                    
                    with col3:
                        if st.button("🗑️", key=f"delete_{post['id']}_{j}", help="Remove"):
                            st.session_state.saved_posts = [p for p in st.session_state.saved_posts if p['id'] != post['id']]
                            st.rerun()
    
    if st.button("🔙 Back to Analysis", key="back_from_saved_btn"):
        st.session_state.show_saved_posts = False
        st.rerun()

elif st.session_state.get('show_planner', False):
    st.header("🎬 Show Concept Planner")
    
    # Create new show concept
    with st.expander("➕ Create New Show Concept", expanded=True):
        show_title = st.text_input("Show Title", placeholder="e.g., 'The Weekly Woke Roundup'", key="show_title_input")
        show_creator = st.text_input("Creator/Host", value=creator_name, key="show_creator_input")
        show_theme = st.text_area("Show Theme/Description", placeholder="What's this show about?", key="show_theme_textarea")
        
        # Select posts to include
        if st.session_state.saved_posts:
            st.write("**Select posts to include:**")
            selected_posts = []
            for k, post in enumerate(st.session_state.saved_posts):
                if st.checkbox(f"{post['title'][:50]}... (r/{post['subreddit']})", key=f"select_{post['id']}_{k}"):
                    selected_posts.append(post)
            
            if st.button("🎬 Create Show Concept", key="create_concept_btn") and show_title:
                new_concept = {
                    'id': f"show_{len(st.session_state.show_concepts)}_{show_title.replace(' ', '_')}",
                    'title': show_title,
                    'creator': show_creator,
                    'theme': show_theme,
                    'posts': selected_posts,
                    'created_at': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'estimated_duration': len(selected_posts) * 8
                }
                st.session_state.show_concepts.append(new_concept)
                st.success(f"✅ Created show concept: {show_title}")
                st.rerun()
    
    # Display existing show concepts
    if st.session_state.show_concepts:
        st.write("### 🎭 Your Show Concepts")
        for l, concept in enumerate(st.session_state.show_concepts):
            with st.expander(f"🎬 {concept['title']} ({len(concept['posts'])} segments)", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Host:** {concept['creator']}")
                    st.write(f"**Duration:** {concept['estimated_duration']} minutes")
                    if concept['theme']:
                        st.write(f"**Theme:** {concept['theme']}")
                    
                    st.write("**Segments:**")
                    for i, post in enumerate(concept['posts'], 1):
                        st.write(f"{i}. {post['title']} (r/{post['subreddit']})")
                
                with col2:
                    # Create exportable show notes
                    show_notes = f"""# {concept['title']}
**Host:** {concept['creator']}
**Duration:** ~{concept['estimated_duration']} minutes

## Show Theme
{concept['theme']}

## Segments
"""
                    for i, post in enumerate(concept['posts'], 1):
                        show_notes += f"""
### Segment {i}: {post['title']}
- **Source:** r/{post['subreddit']}
- **Engagement:** {post['score']} upvotes, {post['num_comments']} comments
- **Reddit:** https://reddit.com{post['permalink']}

**AI Analysis:**
{post['analysis']}

---
"""
                    st.download_button(
                        "📄 Download Show Notes",
                        show_notes,
                        file_name=f"{concept['title'].replace(' ', '_')}_show_notes.md",
                        mime="text/markdown",
                        key=f"download_{concept['id']}_{l}"
                    )
    
    if st.button("🔙 Back to Analysis", key="back_from_planner_btn"):
        st.session_state.show_planner = False
        st.rerun()

elif st.session_state.get('viewing_post'):
    post = st.session_state.viewing_post
    st.header("📖 Viewing Saved Post")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.subheader(post['title'])
    with col2:
        if st.button("🔙 Back", key="back_from_viewing_btn"):
            del st.session_state.viewing_post
            st.rerun()
    
    st.write(f"**r/{post['subreddit']}** • {post['score']} upvotes • {post['num_comments']} comments")
    st.write(f"**Saved:** {post['saved_at']} for {post['creator']}")
    
    if post['image_url']:
        st.image(post['image_url'], width=400)
    
    if post['content']:
        st.write("**Content:**")
        st.write(post['content'])
    
    st.write("**AI Analysis:**")
    st.write(post['analysis'])
    
    st.write(f"[View on Reddit](https://reddit.com{post['permalink']})")

else:
    # Main content
    st.header("📊 Reddit Content Analysis")

    # Subreddit input
    subreddit_input = st.text_input(
        "Enter Subreddit Name", 
        value=st.session_state.selected_subreddit,
        placeholder="e.g., Conservative, Politics, Movies",
        key="main_subreddit_input"
    )

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

# Footer
st.markdown("""
<div class="footer">
    <div style="color: white; font-size: 1.5rem; font-weight: 700;">SHORTHAND STUDIOS</div>
    <div style="color: #b5def2;">AI-Powered Content Intelligence Platform</div>
</div>
""", unsafe_allow_html=True)

