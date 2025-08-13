import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import openai
import os
import feedparser

# At the very top, after imports
if "password_correct" not in st.session_state:
    st.session_state.password_correct = False
if "current_platform" not in st.session_state:
    st.session_state.current_platform = "Home"

# Modified password check
def check_password():
    """Returns `True` if the user had the correct password."""
    
    # If already authenticated, return True
    if st.session_state.password_correct:
        return True
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == os.getenv('APP_PASSWORD', 'defaultpassword'):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False
            st.session_state["password_attempted"] = True  # Add this flag

    # Show login screen
    st.markdown("""
    <div style="margin-top: 100px; text-align: center;">
        <h1 style="font-family: 'Inter', sans-serif; font-size: 48px; font-weight: 800; text-transform: uppercase;">
            Shorthand Studios <span style="color: #BCE5F7;">Login</span>
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.text_input(
            "Enter Password", type="password", on_change=password_entered, key="password"
        )
        # Only show error if password was attempted
        if st.session_state.get("password_attempted", False):
            st.error("❌ Password incorrect")
    
    return False

# Configure Streamlit page
st.set_page_config(
  page_title="Shorthand Studios - Content Intelligence Platform",
  layout="wide"
)

# Check password before showing any content
if not check_password():
    st.stop()

# Enhanced CSS for Shorthand Studios website styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

:root {
  --primary-text: #221F1F;
  --accent-blue: #BCE5F7;
  --secondary-beige: #E6DDC1;
  --background: #FFFFFF;
  --footer-grey: #666666;
}

/* Global styles */
* {
  color: var(--primary-text);
}

body {
  background-color: var(--background);
}

.main .block-container {
  padding-top: 0.5rem;  /* CHANGED: Further reduced for alignment */
  max-width: 1200px;
  padding-left: 4rem;
  padding-right: 4rem;
}

/* Hero section */
.hero-section {
  min-height: 70vh;  /* CHANGED: Reduced from 90vh */
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  padding: 1rem 0;  /* CHANGED: Further reduced from 2rem 0 */
  background: var(--background);
  margin-bottom: 1rem;  /* ADDED: Reduce space after hero */
  margin-top: 0;  /* ADDED: Align with sidebar top */
}

.hero-headline {
  font-family: 'Inter', sans-serif;
  font-size: 130px;
  font-weight: 900;
  text-transform: uppercase;
  color: var(--primary-text);
  line-height: 0.9;
  letter-spacing: -4px;
  margin-bottom: 1rem;  /* CHANGED: Reduced from 2rem */
}

.hero-headline .accent {
  color: var(--accent-blue);
}

.tagline {
  font-family: 'Inter', sans-serif;
  font-size: 30px;
  font-weight: 300;
  color: var(--primary-text);
  line-height: 1.4;
  margin-bottom: 2rem;  /* CHANGED: Reduced from 3rem */
  max-width: 600px;
}

/* Content Intelligence Platform section */
.content-intelligence-section {
  margin-top: 1rem;  /* ADDED: Control spacing above this section */
  margin-bottom: 2rem;  /* ADDED: Control spacing below */
}

.content-intelligence-header {
  font-family: 'Inter', sans-serif;
  font-size: 48px;
  font-weight: 800;
  text-transform: uppercase;
  color: var(--primary-text);
  letter-spacing: -1px;
  margin-bottom: 1rem;  /* ADDED: Reduce spacing after header */
}

/* CTA Buttons */
.stButton > button {
  background: var(--accent-blue);
  color: var(--primary-text);
  border: none;
  font-family: 'Inter', sans-serif;
  font-weight: 700;
  font-size: 16px;
  text-transform: uppercase;
  letter-spacing: 1px;
  border-radius: 4px;
  padding: 1rem 2rem;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.stButton > button:hover {
  background: var(--primary-text);
  color: var(--accent-blue);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

/* Section headings */
h1, h2, h3 {
  font-family: 'Inter', sans-serif;
  font-weight: 800;
  text-transform: uppercase;
  color: var(--primary-text);
  letter-spacing: -1px;
}

h2 {
  font-size: 48px;
  margin-bottom: 2rem;
}

h3 {
  font-size: 32px;
  margin-bottom: 1.5rem;
}

/* Numbered lists */
.numbered-list {
  counter-reset: section;
  margin: 2rem 0;
}

.numbered-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #e0e0e0;
}

.numbered-item::before {
  counter-increment: section;
  content: "0" counter(section);
  font-family: 'Inter', sans-serif;
  font-size: 44px;
  font-weight: 800;
  color: var(--accent-blue);
  margin-right: 2rem;
  min-width: 80px;
}

/* Body text */
p, .stMarkdown {
  font-family: 'Inter', sans-serif;
  font-size: 19px;
  font-weight: 300;
  line-height: 1.6;
  color: var(--primary-text);
}

/* Two column layout */
.two-column {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  margin: 4rem 0;
  align-items: center;
}

/* Hexagon shapes for ecosystem */
.hexagon {
  width: 120px;
  height: 120px;
  background: var(--secondary-beige);
  position: relative;
  margin: 60px auto;
  display: flex;
  align-items: center;
  justify-content: center;
  clip-path: polygon(30% 0%, 70% 0%, 100% 50%, 70% 100%, 30% 100%, 0% 50%);
}

.hexagon.blue {
  background: var(--accent-blue);
}

/* AI Analysis box - updated style */
.ai-analysis {
  background: #f8f9fa;
  border-left: 4px solid var(--accent-blue);
  border-radius: 0;
  padding: 2rem;
  margin: 2rem 0;
  font-family: 'Inter', sans-serif;
}

/* Expander style */
.stExpander {
  border: 1px solid #e0e0e0;
  border-radius: 0;
  margin-bottom: 1rem;
}

/* Footer */
.footer {
  background: var(--secondary-beige);
  color: var(--footer-grey);
  padding: 4rem 2rem;
  margin: 4rem -4rem -2rem -4rem;
  text-align: left;
  font-family: 'Inter', sans-serif;
}

.footer .brand {
  font-size: 24px;
  font-weight: 800;
  text-transform: uppercase;
  color: var(--primary-text);
  margin-bottom: 1rem;
}

/* Sidebar styling */
.css-1d391kg {
  background-color: #fafafa;
}

/* Input fields */
.stTextInput > div > div > input,
.stSelectbox > div > div > select {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-family: 'Inter', sans-serif;
  font-size: 16px;
}

/* Metrics */
.metric-container {
  background: var(--background);
  border: 1px solid #e0e0e0;
  padding: 1.5rem;
  border-radius: 4px;
  text-align: center;
}

/* Info boxes */
.stInfo {
  background-color: rgba(188, 229, 247, 0.1);
  border: 1px solid var(--accent-blue);
  border-radius: 4px;
}

/* Success messages */
.stSuccess {
  background-color: rgba(188, 229, 247, 0.1);
  color: var(--primary-text);
  border: 1px solid var(--accent-blue);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
  gap: 2rem;
  border-bottom: 2px solid #e0e0e0;
}

.stTabs [data-baseweb="tab"] {
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  font-size: 16px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--primary-text);
  padding: 1rem 0;
}

.stTabs [aria-selected="true"] {
  color: var(--accent-blue);
  border-bottom: 3px solid var(--accent-blue);
}

/* White space and layout */
.section-spacing {
  margin: 6rem 0;
}

.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
}

/* Make subreddit button text smaller */
div[data-testid="column"] button p {
  font-size: 12px !important;
  line-height: 1.2 !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}
</style>
""", unsafe_allow_html=True)

# ============ SIDEBAR CONFIGURATION ============

st.sidebar.markdown("""
<h2 style="font-size: 24px; font-weight: 800; text-transform: uppercase; letter-spacing: -0.5px;">
  Platform <span style="color: #BCE5F7;">Selection</span>
</h2>
""", unsafe_allow_html=True)

platform = st.sidebar.selectbox(
    "Choose Platform",
    ["Home", "Reddit Analysis", "YouTube Intelligence", "Movie & TV Trends", "Podcast Trends"],
    key="platform_select",
    index=["Home", "Reddit Analysis", "YouTube Intelligence", "Movie & TV Trends", "Podcast Trends"].index(
        st.session_state.get("current_platform", "Home")
    )
)
st.session_state.current_platform = platform

st.sidebar.markdown("---")

st.sidebar.markdown("""
<h2 style="font-size: 24px; font-weight: 800; text-transform: uppercase; letter-spacing: -0.5px;">
  Creator <span style="color: #BCE5F7;">Settings</span>
</h2>
""", unsafe_allow_html=True)

creator_name = st.sidebar.text_input(
  "Creator/Show",
  value="Bailey Sarian",
  placeholder="e.g., Bailey Sarian, True Crime Creator, YouTuber",
  key="creator_name_input"
)

st.sidebar.markdown("---")


# ============ API KEY MANAGEMENT ============

def get_api_keys():
  """Get API keys from environment variables"""
  openai_key = os.getenv('OPENAI_API_KEY', '')
  youtube_key = os.getenv('YOUTUBE_API_KEY', '')
  spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID', '')
  spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET', '')
  tmdb_key = os.getenv('TMDB_API_KEY', '')
  return openai_key, youtube_key, spotify_client_id, spotify_client_secret, tmdb_key

def get_relevant_subreddits_for_creator(creator_name, api_key):
    """Use AI to find 12 most relevant subreddits for a creator"""
    if not api_key:
        return None
    
    prompt = f"""Analyze the creator "{creator_name}" and suggest the 12 most relevant subreddits for their content.

Focus on:
1. Subreddits that match their content niche/topic
2. Communities with good audience size (avoid tiny subreddits with <10k members)
3. Active communities where their content would be relevant
4. Mix of primary niche + related/crossover communities
5. Use actual existing subreddit names (check they exist)

For example, if analyzing "Bailey Sarian":
- Primary niche: TrueCrime, serialkillers, UnresolvedMysteries
- Beauty crossover: MakeupAddiction, beauty, SkinCareAddiction  
- Storytelling: nosleep, LetsNotMeet, creepy
- General: AskReddit, todayilearned, videos

Return ONLY a Python list of subreddit names (without r/ prefix), exactly like this format:
["TrueCrime", "serialkillers", "UnresolvedMysteries", "MakeupAddiction", "beauty", "nosleep", "LetsNotMeet", "creepy", "AskReddit", "todayilearned", "videos", "entertainment"]

Creator: {creator_name}"""

    try:
        import openai
        openai.api_key = api_key
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            timeout=30
        )
        
        # Parse the AI response to extract the list
        response_text = response.choices[0].message.content.strip()
        
        # Try to extract the list from the response
        import ast
        try:
            # Look for a list in the response
            start = response_text.find('[')
            end = response_text.find(']') + 1
            if start != -1 and end != 0:
                list_text = response_text[start:end]
                subreddits = ast.literal_eval(list_text)
                if isinstance(subreddits, list) and len(subreddits) <= 12:
                    return subreddits[:12]  # Ensure max 12
        except:
            pass
            
        # Fallback: extract subreddit names manually using regex
        import re
        subreddits = re.findall(r'"([^"]+)"', response_text)
        if subreddits:
            return subreddits[:12]
        
        # Final fallback: try to extract words that look like subreddit names
        words = response_text.replace('[', '').replace(']', '').replace('"', '').split(',')
        clean_subreddits = []
        for word in words:
            clean_word = word.strip()
            if clean_word and len(clean_word) > 2 and len(clean_word) < 25:
                clean_subreddits.append(clean_word)
        
        return clean_subreddits[:12] if clean_subreddits else None
            
    except Exception as e:
        st.error(f"Error getting relevant subreddits: {str(e)}")
        return None

# Get API keys from environment variables
api_key, youtube_api_key, spotify_client_id, spotify_client_secret, tmdb_key = get_api_keys()

# API status - lower priority, less emphasized
with st.sidebar.expander("🔑 API Status", expanded=False):
  if api_key:
    st.success("✅ AI analysis enabled")
  else:
    st.error("❌ AI analysis unavailable")
  
  if youtube_api_key:
    st.success("✅ YouTube live data enabled")
  else:
    st.info("Using sample data")


# Conditional Header - Large for Home, Small for other pages
if platform == "Home":
    # Full hero section for home page
    st.markdown("""
    <div class="hero-section">
      <h1 class="hero-headline">Shorthand<br>Studios<span class="accent">.</span></h1>
      <p class="tagline">Transform trending topics into compelling content with AI-powered insights for creators and publishers.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Compact header for other pages
    st.markdown("""
    <div style="padding: 2rem 0 1rem 0; border-bottom: 2px solid #e0e0e0; margin-bottom: 2rem;">
      <h2 style="font-family: 'Inter', sans-serif; font-size: 36px; font-weight: 800; text-transform: uppercase; margin: 0;">
        Shorthand Studios <span style="color: #BCE5F7;">.</span>
      </h2>
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
    f"https://www.reddit.com/r/{subreddit}/{category}.json",  # Removed ?limit from URL
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
            return data['data']['children'][:limit]  # Force slice to limit
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
  time_factor = 1 / (hours_ago + 2) # +2 to prevent extreme values for very new posts
  
  # Engagement score
  engagement = upvotes + (comments * 2) # Comments weighted more heavily
  
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

SUMMARY: What this post is really about (1-2 sentences)

COMMENTER SENTIMENT: How the commenters in this thread are feeling (angry, excited, confused, etc.)

NEWS CONTEXT: Connect this to current events, trending topics, or recent news stories

NORMAL TAKE: What {creator_name} would typically say about this topic, based on their known positions and style

HOT TAKE: {creator_name}'s most provocative, exaggerated take designed for viral content - stay true to their personality but make it bold and shareable

SOCIAL CONTENT: Specific YouTube titles and social media content ideas that {creator_name} would actually use

CONTROVERSY LEVEL: How polarizing this content would be for {creator_name} (1-10 scale)

Important: Base your analysis on {creator_name}'s actual known personality, political positions, and communication style."""

  try:
    response = openai.ChatCompletion.create(
      model="gpt-4.1-nano",
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
  
  return " ".join(hashtags[:8]) # Limit to 8 hashtags

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
    
    with st.expander(f"{i+1:02d} | {title[:80]}{'...' if len(title) > 80 else ''}", expanded=False):
      # Clean metrics display
      st.markdown(f"""
      <div style="display: flex; gap: 3rem; margin-bottom: 2rem; padding: 1.5rem; background: #f8f9fa; border-radius: 8px;">
        <div style="text-align: center;">
          <p style="font-size: 32px; font-weight: 800; color: #BCE5F7; margin: 0;">{score:,}</p>
          <p style="font-size: 14px; text-transform: uppercase; color: #666;">Upvotes</p>
        </div>
        <div style="text-align: center;">
          <p style="font-size: 32px; font-weight: 800; color: #BCE5F7; margin: 0;">{num_comments:,}</p>
          <p style="font-size: 14px; text-transform: uppercase; color: #666;">Comments</p>
        </div>
        <div style="text-align: center;">
          <p style="font-size: 32px; font-weight: 800; color: #BCE5F7; margin: 0;">{int((datetime.now() - created).total_seconds() / 3600)}</p>
          <p style="font-size: 14px; text-transform: uppercase; color: #666;">Hours Ago</p>
        </div>
      </div>
      """, unsafe_allow_html=True)

      
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
          st.write(f"  {comment['body'][:200]}{'...' if len(comment['body']) > 200 else ''}")
      
      # AI Analysis
      if api_key:
        with st.spinner("🤖 AI analyzing content..."):
          analysis = analyze_with_ai(title, selftext, comments, api_key, creator_name, image_url if is_image else None)
        
        if analysis and not analysis.startswith("AI Analysis Error"):
          st.markdown('<div class="ai-analysis">', unsafe_allow_html=True)
          st.markdown("""
          <h3 style="font-size: 24px; font-weight: 800; text-transform: uppercase; margin-bottom: 1.5rem;">
            AI Analysis <span style="color: #BCE5F7;">Results</span>
          </h3>
          """, unsafe_allow_html=True)
          
          if is_image:
            st.info("Image analysis included")
          
          st.write(analysis)

          # Add hashtags
          hashtags = generate_hashtags(title, subreddit, creator_name)
          st.markdown(f"**Suggested Hashtags:** `{hashtags}`")
          
          # Export button - LEFT ALIGNED
          trending = calculate_trending_score(score, num_comments, post_data.get('created_utc', 0))
          export_data = f"""# {creator_name} Analysis for Reddit Post

**Post:** {title}
**Subreddit:** r/{subreddit}
**Score:** {score:,} upvotes
**Comments:** {num_comments:,}
**Trending Score:** {trending:,}
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
            label="📄 Export Analysis",
            data=export_data,
            file_name=f"{creator_name.replace(' ', '_')}_{title[:30].replace(' ', '_')}_analysis.txt",
            mime="text/plain",
            key=f"export_{post_id}_{i}",
            help="Download this analysis as a text file"
          )

          st.markdown('</div>', unsafe_allow_html=True)
        elif analysis:
          st.error(analysis)
      else:
        st.markdown('<div class="ai-analysis">', unsafe_allow_html=True)
        st.markdown("""
        <h3 style="font-size: 24px; font-weight: 800; text-transform: uppercase; margin-bottom: 1.5rem;">
          AI Analysis <span style="color: #BCE5F7;">Results</span>
        </h3>
        """, unsafe_allow_html=True)
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
    st.info("Showing sample trending videos (Configure YouTube API key for live data)")
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
      'videoCategoryId': '25' # News & Politics category
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
  
def get_relevant_channels_for_creator(creator_name, api_key):
    """Use AI to find 5 most relevant YouTube channels for a creator"""
    if not api_key:
        return None
    
    prompt = f"""Analyze the creator "{creator_name}" and suggest 5 YouTube channels that are most relevant/similar to their content.

Focus on:
1. Channels that create similar content types
2. Channels in the same niche or related niches
3. Channels with good audience overlap
4. Popular channels that the creator's audience would also watch
5. Use actual existing YouTube channel names

For example, if analyzing "Bailey Sarian":
- Similar true crime: Kendall Rae, Eleanor Neale, Stephanie Harlowe
- Beauty crossover: James Charles, Jeffree Star
- Storytelling: MrBallen, That Chapter

Return ONLY a Python list of YouTube channel names, exactly like this format:
["Kendall Rae", "Eleanor Neale", "Stephanie Harlowe", "MrBallen", "That Chapter"]

Make sure these are real, active YouTube channels. Do not include the original creator in the list.

Creator: {creator_name}"""

    try:
        import openai
        openai.api_key = api_key
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            timeout=30
        )
        
        # Parse the AI response to extract the list
        response_text = response.choices[0].message.content.strip()
        
        # Try to extract the list from the response
        import ast
        try:
            # Look for a list in the response
            start = response_text.find('[')
            end = response_text.find(']') + 1
            if start != -1 and end != 0:
                list_text = response_text[start:end]
                channels = ast.literal_eval(list_text)
                if isinstance(channels, list) and len(channels) <= 5:
                    return channels[:5]  # Ensure max 5
        except:
            pass
            
        # Fallback: extract channel names manually using regex
        import re
        channels = re.findall(r'"([^"]+)"', response_text)
        if channels:
            return channels[:5]
        
        # Final fallback: try to extract words that look like channel names
        words = response_text.replace('[', '').replace(']', '').replace('"', '').split(',')
        clean_channels = []
        for word in words:
            clean_word = word.strip()
            if clean_word and len(clean_word) > 2 and len(clean_word) < 30:
                clean_channels.append(clean_word)
        
        return clean_channels[:5] if clean_channels else None
            
    except Exception as e:
        st.error(f"Error getting relevant channels: {str(e)}")
        return None


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
      st.info(f"Showing sample videos from '{query}' channel (Configure YouTube API key for live search)")
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
      st.info(f"Showing sample search results for '{query}' from {timeframe_text} (Configure YouTube API key for live search)")
    
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
                'published': format_youtube_date(snippet.get('publishedAt', 'Unknown')),
                'video_id': item.get('id', {}).get('videoId', ''),
                'description': snippet.get('description', '')[:200] + '...' if snippet.get('description') else '',
                'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
                'views': get_video_views(item.get('id', {}).get('videoId', ''), api_key)
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
            'published': format_youtube_date(snippet.get('publishedAt', 'Unknown')),
            'video_id': item.get('id', {}).get('videoId', ''),
            'description': snippet.get('description', '')[:200] + '...' if snippet.get('description') else '',
            'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
            'views': get_video_views(item.get('id', {}).get('videoId', ''), api_key)
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

def extract_view_count_for_sorting(views_string):
    """Extract numeric view count from formatted string for sorting"""
    if not views_string or views_string == "N/A":
        return 0
    
    try:
        # Remove "views" and any commas
        clean_views = views_string.replace(" views", "").replace(",", "")
        
        # Handle M and K suffixes
        if "M" in clean_views:
            return int(float(clean_views.replace("M", "")) * 1000000)
        elif "K" in clean_views:
            return int(float(clean_views.replace("K", "")) * 1000)
        else:
            return int(clean_views)
    except:
        return 0
    
def get_video_views(video_id, api_key):
    """Get view count for a specific video"""
    if not api_key or not video_id or video_id.startswith('sample'):
        return "N/A"
    
    try:
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            'part': 'statistics',
            'id': video_id,
            'key': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('items') and len(data['items']) > 0:
                stats = data['items'][0].get('statistics', {})
                view_count = stats.get('viewCount')
                if view_count:
                    views = int(view_count)
                    if views >= 1000000:
                        return f"{views/1000000:.1f}M views"
                    elif views >= 1000:
                        return f"{views/1000:.0f}K views"
                    else:
                        return f"{views:,} views"
        return "N/A"
    except:
        return "N/A"

def format_youtube_date(date_string):
    """Convert YouTube API date to MM/DD/YY format"""
    if not date_string or date_string in ['Unknown', 'N/A']:
        return date_string
    
    try:
        from datetime import datetime
        if 'T' in date_string:
            clean_date = date_string.replace('Z', '').split('T')[0]
            dt = datetime.strptime(clean_date, '%Y-%m-%d')
        else:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return dt.strftime('%m/%d/%y')
    except:
        return date_string

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
    st.info("Showing sample comments (Configure YouTube API key for live comment data)")
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
def get_video_by_id(video_id, api_key=None):
  """Get a specific YouTube video by ID"""
  if not api_key:
    return None
  
  try:
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
      'part': 'snippet,statistics',
      'id': video_id,
      'key': api_key
    }
    
    response = requests.get(url, params=params, timeout=15)
    
    if response.status_code == 200:
      data = response.json()
      if data.get('items'):
        item = data['items'][0]
        snippet = item.get('snippet', {})
        stats = item.get('statistics', {})
        
        return {
          'title': snippet.get('title', 'No title'),
          'channel': snippet.get('channelTitle', 'Unknown Channel'),
          'published': format_youtube_date(snippet.get('publishedAt', 'Unknown')),
          'views': get_video_views(item.get('id', ''), youtube_api_key),
          'video_id': video_id,
          'description': snippet.get('description', '')[:200] + '...' if snippet.get('description') else '',
          'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', '')
        }
  except:
    return None

def analyze_video_for_creator_auto(video, comments, creator_name, api_key):
    """Auto-analyze video + comments for creator - Reddit style"""
    if not api_key:
        return None
    
    # Prepare comment text
    comment_text = ""
    if comments:
        top_comments = []
        for comment in comments[:5]:  # Top 5 comments
            top_comments.append(f"• {comment['author']}: {comment['text'][:100]}...")
        comment_text = "\n".join(top_comments)
    
    prompt = f"""Analyze this YouTube video for {creator_name}:

Video: "{video['title']}" by {video['channel']} ({video.get('views', 'N/A')})

Top Comments:
{comment_text}

Brief analysis for {creator_name}:

REACTION ANGLE: How {creator_name} should approach this
KEY POINTS: 2-3 main points to address
AUDIENCE SENTIMENT: What viewers are saying
CONTENT IDEA: Specific video concept for {creator_name}

Keep concise and actionable."""

    try:
        import openai
        openai.api_key = api_key
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            timeout=30
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Analysis Error: {str(e)}"

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

AUDIENCE SENTIMENT: Overall mood and feelings in the comments (angry, supportive, confused, etc.)
CONTROVERSIAL POINTS: What aspects are people most divided on?
{creator_name.upper()} OPPORTUNITY: How {creator_name} could address these comments or create follow-up content
COMMENT THEMES: Top 3 recurring themes or talking points in the comments
AUDIENCE QUESTIONS: What questions are viewers asking that {creator_name} could answer?
ENGAGEMENT STRATEGY: How {creator_name} could respond to maximize engagement
CONTENT IDEAS: 2-3 video ideas based on what the audience is discussing

Focus on what the audience is actually saying and how {creator_name} could use these insights."""
  
  try:
    response = openai.ChatCompletion.create(
      model="gpt-4.1-nano",
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

TRENDING VIDEO TOPIC: [Main topic/theme]
{creator_name.upper()} ANGLE: How {creator_name} could respond, react, or create similar content
CONTENT IDEA: Specific video title for {creator_name}'s channel
FORMAT: Best format (Reaction, Analysis, Response, Original Take)
URGENCY: How time-sensitive this trend is (1-10)
HOOK: Opening line or angle to grab attention
SERIES POTENTIAL: Could this become multiple videos?"""
  
  try:
    response = openai.ChatCompletion.create(
      model="gpt-4.1-nano",
      messages=[{"role": "user", "content": prompt}],
      max_tokens=800,
      timeout=30
    )
    return response.choices[0].message.content
  except Exception as e:
    return f"AI Analysis Error: {str(e)}"
  
def get_youtube_podcast_channels(api_key=None, category="general", max_results=20):
    """Get popular podcast channels from YouTube"""
    if not api_key:
        return None
    
    # Define search queries for different podcast categories
    podcast_queries = {
        "general": "podcast channel",
        "true crime": "true crime podcast",
        "comedy": "comedy podcast",
        "business": "business podcast",
        "news": "news podcast daily",
        "technology": "tech podcast",
        "health": "health wellness podcast",
        "sports": "sports podcast",
        "education": "educational podcast",
        "music": "music podcast",
        "politics": "political podcast"
    }
    
    query = podcast_queries.get(category, "podcast channel")
    
    try:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'channel',
            'order': 'relevance',
            'maxResults': max_results,
            'key': api_key
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            channels = []
            
            for item in data.get('items', []):
                snippet = item.get('snippet', {})
                
                # Filter to ensure it's actually a podcast
                title = snippet.get('title', '').lower()
                description = snippet.get('description', '').lower()
                
                if 'podcast' in title or 'podcast' in description or 'show' in title:
                    channel_data = {
                        'channel_id': item.get('id', {}).get('channelId', ''),
                        'title': snippet.get('title', 'Unknown'),
                        'description': snippet.get('description', '')[:200] + '...',
                        'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', '')
                    }
                    channels.append(channel_data)
            
            return channels
    except:
        return None
  
# ============ SPOTIFY API FUNCTIONS ============

def get_spotify_token(client_id, client_secret):
    """Get Spotify access token using Client Credentials Flow"""
    if not client_id or not client_secret:
        return None
    
    try:
        import base64
        
        # Encode credentials
        credentials = f"{client_id}:{client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        # Get token
        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "client_credentials"
        }
        
        response = requests.post(url, headers=headers, data=data)
        
        if response.status_code == 200:
            return response.json()['access_token']
        else:
            st.error(f"❌ Spotify Auth Error: {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"❌ Spotify Token Error: {str(e)}")
        return None

def search_podcasts_by_genre(token, genre="all", limit=10):
    """Get popular podcasts by genre"""
    if not token:
        return None
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Build search query based on genre
        if genre == "all":
            # For 'all', search for popular podcast shows
            search_query = "podcast"  # Simple generic search
            params = {
                "q": search_query,
                "type": "show",
                "limit": 50,  # Get more results to filter from
                "market": "US"
            }

        else:
            # For specific genres, use the genre in the search
            # Remove the "genre:" prefix as it's not supported for shows
            search_query = genre
            params = {
                "q": search_query,
                "type": "show", 
                "limit": 50,  # Get more results to filter from
                "market": "US"
            }
        
        url = "https://api.spotify.com/v1/search"
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            shows = []
            
            items = data.get('shows', {}).get('items', [])
            
            # If we have items, process them
            for show in items[:limit]:  # Limit to requested number
                # Skip if no images
                if not show.get('images'):
                    continue
                    
                show_data = {
                    'id': show['id'],
                    'name': show['name'],
                    'publisher': show['publisher'],
                    'description': show['description'][:200] + '...' if len(show['description']) > 200 else show['description'],
                    'total_episodes': show.get('total_episodes', 0),
                    'image': show['images'][0]['url'] if show['images'] else None,
                    'explicit': show.get('explicit', False),
                    'url': show['external_urls']['spotify']
                }
                shows.append(show_data)
            
            # If no results found with genre search, try a different approach
            if not shows and genre != "all":
                # Try searching for "<genre> podcast"
                search_query = f"{genre} podcast"
                params['q'] = search_query
                
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get('shows', {}).get('items', [])
                    
                    for show in items[:limit]:
                        if not show.get('images'):
                            continue
                            
                        show_data = {
                            'id': show['id'],
                            'name': show['name'],
                            'publisher': show['publisher'],
                            'description': show['description'][:200] + '...' if len(show['description']) > 200 else show['description'],
                            'total_episodes': show.get('total_episodes', 0),
                            'image': show['images'][0]['url'] if show['images'] else None,
                            'explicit': show.get('explicit', False),
                            'url': show['external_urls']['spotify']
                        }
                        shows.append(show_data)
            
            return shows
        else:
            st.error(f"❌ Spotify Search Error: {response.status_code}")
            # Try to get error details
            if response.text:
                st.error(f"Error details: {response.text}")
            return None
            
    except Exception as e:
        st.error(f"❌ Error searching podcasts: {str(e)}")
        return None

def get_show_episodes(token, show_id, limit=10):
    """Get recent episodes from a podcast show"""
    if not token:
        return []  # <- Return empty list instead of None
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        url = f"https://api.spotify.com/v1/shows/{show_id}/episodes"
        params = {
            "limit": limit,
            "market": "US"
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            episodes = []
            
            for ep in data.get('items', []):
                episode_data = {
                    'id': ep['id'],
                    'name': ep['name'],
                    'description': ep['description'][:200] + '...' if len(ep['description']) > 200 else ep['description'],
                    'release_date': ep['release_date'],
                    'duration_ms': ep['duration_ms'],
                    'duration_min': ep['duration_ms'] // 60000,
                    'url': ep['external_urls']['spotify']
                }
                episodes.append(episode_data)
            
            return episodes
        else:
            return []  # <- Return empty list
            
    except Exception as e:
        return []  # <- Return empty list

def search_podcasts_by_topic(token, topic, limit=20):
    """Search for podcast episodes about a specific topic"""
    if not token:
        return None
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        url = "https://api.spotify.com/v1/search"
        params = {
            "q": topic,
            "type": "episode",
            "limit": limit,
            "market": "US"
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            episodes = []
            
            items = data.get('episodes', {}).get('items', [])
            
            # First, collect all episodes with their show IDs
            episode_list = []
            show_ids = set()
            
            for ep in items:
                # Extract show ID from the episode href
                # The href looks like: "https://api.spotify.com/v1/episodes/6FjEzvYK4hXVhV1X5hh2XP"
                # We need to get the show ID by fetching the full episode details
                episode_id = ep.get('id', '')
                
                episode_data = {
                    'id': episode_id,
                    'name': ep.get('name', 'Unknown Episode'),
                    'description': ep.get('description', '')[:200] + '...' if len(ep.get('description', '')) > 200 else ep.get('description', ''),
                    'release_date': ep.get('release_date', 'Unknown'),
                    'duration_min': ep.get('duration_ms', 0) // 60000,
                    'url': ep.get('external_urls', {}).get('spotify', ''),
                    'image': ep.get('images', [{}])[0].get('url', '') if ep.get('images') else None,
                    'show_id': None,
                    'show_name': 'Loading...'
                }
                episode_list.append(episode_data)
            
            # Now fetch full episode details to get show IDs
            for i, ep_data in enumerate(episode_list):
                if ep_data['id']:
                    ep_url = f"https://api.spotify.com/v1/episodes/{ep_data['id']}"
                    ep_response = requests.get(ep_url, headers=headers, params={"market": "US"})
                    
                    if ep_response.status_code == 200:
                        full_episode = ep_response.json()
                        if 'show' in full_episode:
                            show_id = full_episode['show'].get('id')
                            show_name = full_episode['show'].get('name', 'Unknown Show')
                            episode_list[i]['show_id'] = show_id
                            episode_list[i]['show_name'] = show_name
                        
                        # Small delay to respect rate limits
                        time.sleep(0.1)
            
            return episode_list
            
        else:
            st.error(f"❌ Spotify Episode Search Error: {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"❌ Error searching episodes: {str(e)}")
        return None
            
def get_new_episodes_today(token, limit=20):
    """Get podcast episodes released today"""
    if not token:
        return None
    
    # Search for episodes with today's date
    today = datetime.now().strftime("%Y-%m-%d")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        url = "https://api.spotify.com/v1/search"
        params = {
            "q": f"tag:new",  # This gets recently added content
            "type": "episode",
            "limit": limit,
            "market": "US"
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            episodes = []
            
            for ep in data.get('episodes', {}).get('items', []):
                # Filter for today's episodes
                if ep['release_date'] == today:
                    episode_data = {
                        'id': ep['id'],
                        'name': ep['name'],
                        'show_name': ep['show']['name'],
                        'description': ep['description'][:200] + '...' if len(ep['description']) > 200 else ep['description'],
                        'release_date': ep['release_date'],
                        'duration_min': ep['duration_ms'] // 60000,
                        'url': ep['external_urls']['spotify'],
                        'image': ep['images'][0]['url'] if ep['images'] else None
                    }
                    episodes.append(episode_data)
            
            return episodes
        else:
            return None
            
    except Exception as e:
        return None
    
def get_itunes_top_podcasts(genre_id=None, limit=20):
    """Get top podcasts from iTunes/Apple Podcasts"""
    try:
        # iTunes genre IDs for podcasts
        genre_map = {
            "all": None,
            "business": 1321,
            "comedy": 1303,
            "education": 1304,
            "fiction": 1483,
            "government": 1511,
            "health": 1512,
            "history": 1487,
            "kids": 1305,
            "leisure": 1502,
            "music": 1310,
            "news": 1489,
            "religion": 1314,
            "science": 1533,
            "society": 1324,
            "sports": 1545,
            "technology": 1318,
            "true_crime": 1488,
            "tv_film": 1309
        }
        
        # Use the lookup URL for top podcasts
        if genre_id:
            url = f"https://itunes.apple.com/us/rss/toppodcasts/limit={limit}/genre={genre_id}/json"
        else:
            url = f"https://itunes.apple.com/us/rss/toppodcasts/limit={limit}/json"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            podcasts = []
            
            entries = data.get('feed', {}).get('entry', [])
            
            for i, entry in enumerate(entries, 1):
                # Extract podcast data
                podcast_data = {
                    'rank': i,
                    'name': entry.get('im:name', {}).get('label', 'Unknown'),
                    'artist': entry.get('im:artist', {}).get('label', 'Unknown'),
                    'summary': entry.get('summary', {}).get('label', 'No description')[:300] + '...',
                    'image': entry.get('im:image', [{}])[-1].get('label', ''),  # Get largest image
                    'url': entry.get('link', {}).get('attributes', {}).get('href', ''),
                    'category': entry.get('category', {}).get('attributes', {}).get('label', 'Unknown'),
                    'release_date': entry.get('im:releaseDate', {}).get('label', 'Unknown')
                }
                podcasts.append(podcast_data)
            
            return podcasts
        else:
            return None
            
    except Exception as e:
        st.error(f"❌ Error fetching iTunes podcasts: {str(e)}")
        return None

def get_itunes_podcast_episodes(podcast_id, limit=5):
    """Get recent episodes for a specific podcast from iTunes"""
    try:
        # iTunes lookup API to get podcast details and feed URL
        lookup_url = f"https://itunes.apple.com/lookup?id={podcast_id}"
        response = requests.get(lookup_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                podcast_info = data['results'][0]
                feed_url = podcast_info.get('feedUrl')
                
                if feed_url:
                    # Parse the podcast RSS feed
                    feed = feedparser.parse(feed_url)
                    episodes = []
                    
                    for entry in feed.entries[:limit]:
                        episode_data = {
                            'title': entry.get('title', 'Unknown'),
                            'published': entry.get('published', 'Unknown'),
                            'duration': entry.get('itunes_duration', 'Unknown'),
                            'description': entry.get('summary', '')[:300] + '...',
                            'link': entry.get('link', '')
                        }
                        episodes.append(episode_data)
                    
                    return episodes
        return []
    except:
        return []
  
    
# ============ TMDB API FUNCTIONS ============

def get_tmdb_genres(api_key, media_type='movie'):
    """Get list of genres from TMDb"""
    try:
        url = f"https://api.themoviedb.org/3/genre/{media_type}/list"
        params = {'api_key': api_key}
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return {genre['id']: genre['name'] for genre in data['genres']}
        return {}
    except:
        return {}

def search_tmdb(api_key, query=None, media_type='movie', genre_id=None, year=None, 
                company_id=None, sort_by='popularity.desc', page=1):
    """Search TMDb for movies or TV shows"""
    try:
        if query:
            # Search by title
            url = f"https://api.themoviedb.org/3/search/{media_type}"
            params = {
                'api_key': api_key,
                'query': query,
                'page': page
            }
            if year:
                params['year'] = year
        else:
            # Discover movies/shows by filters
            url = f"https://api.themoviedb.org/3/discover/{media_type}"
            params = {
                'api_key': api_key,
                'sort_by': sort_by,
                'page': page,
                'vote_count.gte': 100  # Only show items with at least 100 votes
            }
            if genre_id:
                params['with_genres'] = genre_id
            if year:
                if media_type == 'movie':
                    params['primary_release_year'] = year
                else:
                    params['first_air_date_year'] = year
            if company_id:
                params['with_companies'] = company_id
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"TMDb API Error: {str(e)}")
        return None

def get_tmdb_item_details(api_key, item_id, media_type='movie'):
    """Get detailed information about a movie or TV show"""
    try:
        url = f"https://api.themoviedb.org/3/{media_type}/{item_id}"
        params = {
            'api_key': api_key,
            'append_to_response': 'credits,videos,keywords'
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def search_tmdb_multiple_companies(api_key, company_ids, media_type='movie', sort_by='popularity.desc', year=None):
    """Search TMDb for movies/TV shows from multiple companies (OR logic)"""
    all_results = []
    seen_ids = set()  # To avoid duplicates
    
    try:
        # Make separate API calls for each company
        for company_id in company_ids:
            url = f"https://api.themoviedb.org/3/discover/{media_type}"
            params = {
                'api_key': api_key,
                'sort_by': sort_by,
                'page': 1,
                'vote_count.gte': 50,  # Lower threshold for individual companies
                'with_companies': company_id
            }
            
            if year:
                if media_type == 'movie':
                    params['primary_release_year'] = year
                else:
                    params['first_air_date_year'] = year
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get('results', []):
                    item_id = item.get('id')
                    if item_id not in seen_ids:
                        seen_ids.add(item_id)
                        all_results.append(item)
        
        # Sort all results by the selected criteria
        if all_results:
            if sort_by == 'popularity.desc':
                all_results.sort(key=lambda x: x.get('popularity', 0), reverse=True)
            elif sort_by == 'vote_average.desc':
                all_results.sort(key=lambda x: x.get('vote_average', 0), reverse=True)
            elif sort_by == 'vote_count.desc':
                all_results.sort(key=lambda x: x.get('vote_count', 0), reverse=True)
            elif sort_by == 'release_date.desc' or sort_by == 'first_air_date.desc':
                date_field = 'release_date' if media_type == 'movie' else 'first_air_date'
                all_results.sort(key=lambda x: x.get(date_field, ''), reverse=True)
            elif sort_by == 'revenue.desc':
                all_results.sort(key=lambda x: x.get('revenue', 0), reverse=True)
        
        return {'results': all_results}
        
    except Exception as e:
        st.error(f"TMDb API Error: {str(e)}")
        return None
    
def search_tmdb_companies(api_key, query):
    """Search for production companies"""
    try:
        url = "https://api.themoviedb.org/3/search/company"
        params = {
            'api_key': api_key,
            'query': query
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            return response.json()['results']
        return []
    except:
        return []

def analyze_movie_tv_trend(title, overview, popularity, vote_average, media_type, 
                          genre_names, creator_name, api_key):
    """Analyze how a creator should cover a trending movie/TV show"""
    if not api_key:
        return None
    
    import openai
    openai.api_key = api_key
    
    context = f"""Trending {media_type.upper()}:
Title: {title}
Overview: {overview}
Popularity Score: {popularity}
Average Rating: {vote_average}/10
Genres: {', '.join(genre_names)}

This {media_type} is currently trending with high viewership and engagement."""
    
    prompt = f"""Analyze this trending {media_type} for {creator_name}'s content strategy:

{context}

Provide a comprehensive content strategy for {creator_name}:

TREND ANALYSIS: Why this {media_type} is trending and what's driving the interest (2-3 sentences)

{creator_name.upper()} ANGLE: How {creator_name} should approach this topic based on their personality and audience

VIDEO CONCEPTS: 3 specific video ideas with titles that {creator_name} could create:
- Title 1: [Specific title]
- Title 2: [Specific title]  
- Title 3: [Specific title]

HOT TAKE: {creator_name}'s unique, provocative perspective on this {media_type}

DEEP DIVE ANGLES: What aspects {creator_name} could explore (themes, controversies, behind-the-scenes, etc.)

SOCIAL MEDIA STRATEGY: How to leverage this trend across platforms:
- YouTube video idea
- YouTube Shorts approach
- TikTok series concept
- Instagram Reels idea

TIMING: How urgent is this trend? When should {creator_name} publish content?

CONTENT FORMAT: Best format for {creator_name} (review, reaction, analysis, comparison, etc.)

HASHTAGS: Relevant hashtags for maximum reach

CONTROVERSY/DISCUSSION POINTS: What aspects would generate the most engagement and discussion?"""
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1-nano",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            timeout=30
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Analysis Error: {str(e)}"
        

# ============ MAIN CONTENT ============

if platform == "Home":
    # Welcome section
    st.markdown("""
    <div style="margin-bottom: 4rem;">
      <h2 style="font-size: 48px; font-weight: 800; text-transform: uppercase; margin-bottom: 2rem;">
        Content Intelligence <span style="color: #BCE5F7;">Platform</span>
      </h2>
      <p style="font-size: 24px; font-weight: 300; line-height: 1.6; max-width: 800px;">
        Discover what's trending across social media, analyze audience sentiment, and create content strategies powered by AI.
      </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Platform cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 2rem; border-radius: 8px; margin-bottom: 2rem; min-height: 250px;">
          <h3 style="font-size: 24px; font-weight: 700; text-transform: uppercase; margin-bottom: 1rem;">
            🔍 Reddit Analysis
          </h3>
          <p style="font-size: 18px; line-height: 1.6;">
            Monitor viral discussions, analyze community sentiment, and discover content opportunities from Reddit's most engaging posts.
          </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: #f8f9fa; padding: 2rem; border-radius: 8px; min-height: 250px;">
          <h3 style="font-size: 24px; font-weight: 700; text-transform: uppercase; margin-bottom: 1rem;">
            🎬 Movie & TV Trends
          </h3>
          <p style="font-size: 18px; line-height: 1.6;">
            Track trending films and shows, analyze audience preferences, and create content around what's popular in entertainment.
          </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 2rem; border-radius: 8px; margin-bottom: 2rem; min-height: 250px;">
          <h3 style="font-size: 24px; font-weight: 700; text-transform: uppercase; margin-bottom: 1rem;">
            📺 YouTube Intelligence
          </h3>
          <p style="font-size: 18px; line-height: 1.6;">
            Find trending videos, analyze comments, and generate reaction strategies based on what's performing on YouTube.
          </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: #f8f9fa; padding: 2rem; border-radius: 8px; min-height: 250px;">
          <h3 style="font-size: 24px; font-weight: 700; text-transform: uppercase; margin-bottom: 1rem;">
            🎙️ Podcast Trends
          </h3>
          <p style="font-size: 18px; line-height: 1.6;">
            Discover top podcasts by genre, search episodes by topic, and track what's trending in audio content.
          </p>
        </div>
        """, unsafe_allow_html=True)
      
    
    # Features section
    st.markdown("""
    <div style="margin: 4rem 0;">
      <h2 style="font-size: 36px; font-weight: 800; text-transform: uppercase; margin-bottom: 3rem; text-align: center;">
        Key <span style="color: #BCE5F7;">Features</span>
      </h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
          <div style="font-size: 48px; margin-bottom: 1rem;">🤖</div>
          <h4 style="font-size: 20px; font-weight: 700; text-transform: uppercase; margin-bottom: 1rem;">AI Analysis</h4>
          <p>Get personalized content strategies and hot takes based on your creator personality.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
          <div style="font-size: 48px; margin-bottom: 1rem;">📊</div>
          <h4 style="font-size: 20px; font-weight: 700; text-transform: uppercase; margin-bottom: 1rem;">Real-Time Data</h4>
          <p>Access trending content from Reddit, YouTube, podcasts, and entertainment.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
          <div style="font-size: 48px; margin-bottom: 1rem;">💡</div>
          <h4 style="font-size: 20px; font-weight: 700; text-transform: uppercase; margin-bottom: 1rem;">Content Ideas</h4>
          <p>Generate video titles, social media strategies, and engagement tactics.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Call to action
    st.markdown("""
    <div style="background: #BCE5F7; padding: 3rem; border-radius: 8px; text-align: center; margin: 4rem 0;">
      <h3 style="font-size: 32px; font-weight: 800; text-transform: uppercase; margin-bottom: 1rem; color: #221F1F;">
        Ready to Create Better Content?
      </h3>
      <p style="font-size: 20px; margin-bottom: 2rem; color: #221F1F;">
        Select a platform from the sidebar to start analyzing trends and generating content ideas.
      </p>
    </div>
    """, unsafe_allow_html=True)

# First, add this function with your other YouTube functions (before the platform section):

def get_relevant_channels_for_creator(creator_name, api_key):
    """Use AI to find 5 most relevant YouTube channels for a creator"""
    if not api_key:
        return None
    
    prompt = f"""You are a YouTube content strategist. Find 5 YouTube channels that are most similar to "{creator_name}" in terms of:
    - Content style and format
    - Target audience
    - Topic/niche overlap
    - Production quality level
    
    Focus on channels that would have similar audiences and content approaches.
    
    Return ONLY a Python list of 5 channel names like this:
    ["Channel Name 1", "Channel Name 2", "Channel Name 3", "Channel Name 4", "Channel Name 5"]
    
    Make sure channel names are exact and searchable on YouTube. No extra text, just the list."""
    
    try:
        import openai
        openai.api_key = api_key
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.3,
            timeout=30
        )
        
        result = response.choices[0].message.content.strip()
        
        # Parse the list from the AI response
        import ast
        try:
            channels = ast.literal_eval(result)
            if isinstance(channels, list) and len(channels) <= 5:
                return [channel.strip() for channel in channels if channel.strip()]
        except:
            # Fallback parsing if AI doesn't return perfect list format
            import re
            channels = re.findall(r'"([^"]*)"', result)
            return channels[:5] if channels else None
            
    except Exception as e:
        print(f"Error getting relevant channels: {e}")
        return None

def search_youtube_by_channel(channel_name, api_key=None, max_results=5):
    """Search YouTube for recent videos from a specific channel"""
    if not api_key:
        # Return sample channel results
        sample_results = [
            {"title": f"Latest Video from {channel_name}", "views": "156K views", "published": "2 days ago", "description": f"Recent content from {channel_name}...", "video_id": f"sample_{channel_name}_1"},
            {"title": f"{channel_name}'s Hot Take on Current Events", "views": "89K views", "published": "1 day ago", "description": f"Commentary and analysis from {channel_name}...", "video_id": f"sample_{channel_name}_2"},
            {"title": f"Breaking: {channel_name} Responds", "views": "234K views", "published": "3 hours ago", "description": f"Response video from {channel_name}...", "video_id": f"sample_{channel_name}_3"},
        ]
        return sample_results
    
    try:
        # First, get the channel ID
        search_url = "https://www.googleapis.com/youtube/v3/search"
        search_params = {
            'part': 'snippet',
            'q': channel_name,
            'type': 'channel',
            'maxResults': 1,
            'key': api_key
        }
        
        search_response = requests.get(search_url, params=search_params, timeout=15)
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            if search_data.get('items'):
                channel_id = search_data['items'][0]['id']['channelId']
                
                # Now get recent videos from this channel
                videos_url = "https://www.googleapis.com/youtube/v3/search"
                videos_params = {
                    'part': 'snippet',
                    'channelId': channel_id,
                    'type': 'video',
                    'order': 'date',
                    'maxResults': max_results,
                    'key': api_key,
                    'publishedAfter': (datetime.now() - timedelta(days=30)).isoformat() + 'Z'
                }
                
                videos_response = requests.get(videos_url, params=videos_params, timeout=15)
                
                if videos_response.status_code == 200:
                    videos_data = videos_response.json()
                    channel_videos = []
                    
                    for item in videos_data.get('items', []):
                        snippet = item.get('snippet', {})
                        video_data = {
                          'title': snippet.get('title', 'No title'),
                          'channel': snippet.get('channelTitle', 'Unknown Channel'),
                          'views': get_video_views(item.get('id', ''), api_key),
                          'published': format_youtube_date(snippet.get('publishedAt', 'Unknown')),
                          'video_id': item.get('id', ''),
                          'description': snippet.get('description', '')[:200] + '...' if snippet.get('description') else '',
                          'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', '')
                        }                        
                        channel_videos.append(video_data)
                    
                    return channel_videos
        
        # Fallback to sample data if API fails
        return search_youtube_by_channel(channel_name)
        
    except Exception as e:
        return search_youtube_by_channel(channel_name)  # Return sample data on error

# Now replace your entire YouTube Intelligence platform section with this:

# First, add this function with your other YouTube functions (before the platform section):

def get_video_views(video_id, api_key):
    """Get view count for a specific video"""
    if not api_key or not video_id:
        return "N/A"
    
    try:
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            'part': 'statistics',
            'id': video_id,
            'key': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('items'):
                view_count = data['items'][0].get('statistics', {}).get('viewCount', 'N/A')
                if view_count != 'N/A':
                    # Format view count nicely (e.g., 1,234,567 -> 1.2M)
                    try:
                        views = int(view_count)
                        if views >= 1000000:
                            return f"{views/1000000:.1f}M views"
                        elif views >= 1000:
                            return f"{views/1000:.0f}K views"
                        else:
                            return f"{views} views"
                    except:
                        return f"{view_count} views"
                return view_count
        return "N/A"
    except:
        return "N/A"
    """Use AI to find 5 most relevant YouTube channels for a creator"""
    if not api_key:
        return None
    
    prompt = f"""You are a YouTube content strategist. Find 5 YouTube channels that are most similar to "{creator_name}" in terms of:
    - Content style and format
    - Target audience
    - Topic/niche overlap
    - Production quality level
    
    Focus on channels that would have similar audiences and content approaches.
    
    Return ONLY a Python list of 5 channel names like this:
    ["Channel Name 1", "Channel Name 2", "Channel Name 3", "Channel Name 4", "Channel Name 5"]
    
    Make sure channel names are exact and searchable on YouTube. No extra text, just the list."""
    
    try:
        import openai
        openai.api_key = api_key
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.3,
            timeout=30
        )
        
        result = response.choices[0].message.content.strip()
        
        # Parse the list from the AI response
        import ast
        try:
            channels = ast.literal_eval(result)
            if isinstance(channels, list) and len(channels) <= 5:
                return [channel.strip() for channel in channels if channel.strip()]
        except:
            # Fallback parsing if AI doesn't return perfect list format
            import re
            channels = re.findall(r'"([^"]*)"', result)
            return channels[:5] if channels else None
            
    except Exception as e:
        print(f"Error getting relevant channels: {e}")
        return None

def get_relevant_channels_for_creator(creator_name, api_key):
    """Search YouTube for recent videos from a specific channel"""
    if not api_key:
        # Return sample channel results
        sample_results = [
            {"title": f"Latest Video from {channel_name}", "views": "156K views", "published": "2 days ago", "description": f"Recent content from {channel_name}...", "video_id": f"sample_{channel_name}_1"},
            {"title": f"{channel_name}'s Hot Take on Current Events", "views": "89K views", "published": "1 day ago", "description": f"Commentary and analysis from {channel_name}...", "video_id": f"sample_{channel_name}_2"},
            {"title": f"Breaking: {channel_name} Responds", "views": "234K views", "published": "3 hours ago", "description": f"Response video from {channel_name}...", "video_id": f"sample_{channel_name}_3"},
        ]
        return sample_results
    
    try:
        # First, get the channel ID
        search_url = "https://www.googleapis.com/youtube/v3/search"
        search_params = {
            'part': 'snippet',
            'q': channel_name,
            'type': 'channel',
            'maxResults': 1,
            'key': api_key
        }
        
        search_response = requests.get(search_url, params=search_params, timeout=15)
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            if search_data.get('items'):
                channel_id = search_data['items'][0]['id']['channelId']
                
                # Now get recent videos from this channel
                videos_url = "https://www.googleapis.com/youtube/v3/search"
                videos_params = {
                    'part': 'snippet',
                    'channelId': channel_id,
                    'type': 'video',
                    'order': 'date',
                    'maxResults': max_results,
                    'key': api_key,
                    'publishedAfter': (datetime.now() - timedelta(days=30)).isoformat() + 'Z'
                }
                
                videos_response = requests.get(videos_url, params=videos_params, timeout=15)
                
                if videos_response.status_code == 200:
                    videos_data = videos_response.json()
                    channel_videos = []
                    
                    for item in videos_data.get('items', []):
                        snippet = item.get('snippet', {})
                        video_data = {
                          'title': snippet.get('title', 'No title'),
                          'channel': snippet.get('channelTitle', 'Unknown Channel'),
                          'views': get_video_views(item.get('id', ''), api_key),
                          'published': format_youtube_date(snippet.get('publishedAt', 'Unknown')),
                          'video_id': item.get('id', ''),
                          'description': snippet.get('description', '')[:200] + '...' if snippet.get('description') else '',
                          'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', '')
                        }   
                        channel_videos.append(video_data)
                    
                    return channel_videos
        
        # Fallback to sample data if API fails
        return search_youtube_by_channel(channel_name)
        
    except Exception as e:
        return search_youtube_by_channel(channel_name)  # Return sample data on error

# Now replace your entire YouTube Intelligence platform section with this:

# First, add this function with your other YouTube functions (before the platform section):

def get_video_views(video_id, api_key):
    """Get view count for a specific video"""
    if not api_key or not video_id:
        return "N/A"
    
    try:
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            'part': 'statistics',
            'id': video_id,
            'key': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('items'):
                view_count = data['items'][0].get('statistics', {}).get('viewCount', 'N/A')
                if view_count != 'N/A':
                    # Format view count nicely (e.g., 1,234,567 -> 1.2M)
                    try:
                        views = int(view_count)
                        if views >= 1000000:
                            return f"{views/1000000:.1f}M views"
                        elif views >= 1000:
                            return f"{views/1000:.0f}K views"
                        else:
                            return f"{views} views"
                    except:
                        return f"{view_count} views"
                return view_count
        return "N/A"
    except:
        return "N/A"
    """Use AI to find 5 most relevant YouTube channels for a creator"""
    if not api_key:
        return None
    
    prompt = f"""You are a YouTube content strategist. Find 5 YouTube channels that are most similar to "{creator_name}" in terms of:
    - Content style and format
    - Target audience
    - Topic/niche overlap
    - Production quality level
    
    Focus on channels that would have similar audiences and content approaches.
    
    Return ONLY a Python list of 5 channel names like this:
    ["Channel Name 1", "Channel Name 2", "Channel Name 3", "Channel Name 4", "Channel Name 5"]
    
    Make sure channel names are exact and searchable on YouTube. No extra text, just the list."""
    
    try:
        import openai
        openai.api_key = api_key
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.3,
            timeout=30
        )
        
        result = response.choices[0].message.content.strip()
        
        # Parse the list from the AI response
        import ast
        try:
            channels = ast.literal_eval(result)
            if isinstance(channels, list) and len(channels) <= 5:
                return [channel.strip() for channel in channels if channel.strip()]
        except:
            # Fallback parsing if AI doesn't return perfect list format
            import re
            channels = re.findall(r'"([^"]*)"', result)
            return channels[:5] if channels else None
            
    except Exception as e:
        print(f"Error getting relevant channels: {e}")
        return None

def get_relevant_channels_for_creator(creator_name, api_key):
    """Search YouTube for recent videos from a specific channel"""
    if not api_key:
        # Return sample channel results
        sample_results = [
            {"title": f"Latest Video from {channel_name}", "views": "156K views", "published": "2 days ago", "description": f"Recent content from {channel_name}...", "video_id": f"sample_{channel_name}_1"},
            {"title": f"{channel_name}'s Hot Take on Current Events", "views": "89K views", "published": "1 day ago", "description": f"Commentary and analysis from {channel_name}...", "video_id": f"sample_{channel_name}_2"},
            {"title": f"Breaking: {channel_name} Responds", "views": "234K views", "published": "3 hours ago", "description": f"Response video from {channel_name}...", "video_id": f"sample_{channel_name}_3"},
        ]
        return sample_results
    
    try:
        # First, get the channel ID
        search_url = "https://www.googleapis.com/youtube/v3/search"
        search_params = {
            'part': 'snippet',
            'q': channel_name,
            'type': 'channel',
            'maxResults': 1,
            'key': api_key
        }
        
        search_response = requests.get(search_url, params=search_params, timeout=15)
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            if search_data.get('items'):
                channel_id = search_data['items'][0]['id']['channelId']
                
                # Now get recent videos from this channel
                videos_url = "https://www.googleapis.com/youtube/v3/search"
                videos_params = {
                    'part': 'snippet',
                    'channelId': channel_id,
                    'type': 'video',
                    'order': 'date',
                    'maxResults': max_results,
                    'key': api_key,
                    'publishedAfter': (datetime.now() - timedelta(days=30)).isoformat() + 'Z'
                }
                
                videos_response = requests.get(videos_url, params=videos_params, timeout=15)
                
                if videos_response.status_code == 200:
                    videos_data = videos_response.json()
                    channel_videos = []
                    
                    for item in videos_data.get('items', []):
                        snippet = item.get('snippet', {})
                        video_data = {
                            'title': snippet.get('title', 'No title'),
                            'published': snippet.get('publishedAt', 'Unknown'),
                            'video_id': item.get('id', {}).get('videoId', ''),
                            'description': snippet.get('description', '')[:200] + '...' if snippet.get('description') else '',
                            'channel': snippet.get('channelTitle', channel_name),
                            'views': 'N/A'  # Would need additional API call to get view count
                        }
                        channel_videos.append(video_data)
                    
                    return channel_videos
        
        # Fallback to sample data if API fails
        return search_youtube_by_channel(channel_name)
        
    except Exception as e:
        return search_youtube_by_channel(channel_name)  # Return sample data on error

# Now replace your entire YouTube Intelligence platform section with this:

# First, add this function with your other YouTube functions (before the platform section):

def get_video_views(video_id, api_key):
    """Get view count for a specific video"""
    if not api_key or not video_id or video_id.startswith('sample'):
        return "N/A"
    
    try:
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            'part': 'statistics',
            'id': video_id,
            'key': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('items') and len(data['items']) > 0:
                stats = data['items'][0].get('statistics', {})
                view_count = stats.get('viewCount')
                if view_count:
                    # Format view count nicely (e.g., 1,234,567 -> 1.2M)
                    try:
                        views = int(view_count)
                        if views >= 1000000:
                            return f"{views/1000000:.1f}M views"
                        elif views >= 1000:
                            return f"{views/1000:.0f}K views"
                        else:
                            return f"{views:,} views"
                    except:
                        return f"{view_count} views"
        return "N/A"
    except Exception as e:
        print(f"Error fetching views for {video_id}: {e}")
        return "N/A"
    """Use AI to find 5 most relevant YouTube channels for a creator"""
    if not api_key:
        return None
    
    prompt = f"""You are a YouTube content strategist. Find 5 YouTube channels that are most similar to "{creator_name}" in terms of:
    - Content style and format
    - Target audience
    - Topic/niche overlap
    - Production quality level
    
    Focus on channels that would have similar audiences and content approaches.
    
    Return ONLY a Python list of 5 channel names like this:
    ["Channel Name 1", "Channel Name 2", "Channel Name 3", "Channel Name 4", "Channel Name 5"]
    
    Make sure channel names are exact and searchable on YouTube. No extra text, just the list."""
    
    try:
        import openai
        openai.api_key = api_key
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.3,
            timeout=30
        )
        
        result = response.choices[0].message.content.strip()
        
        # Parse the list from the AI response
        import ast
        try:
            channels = ast.literal_eval(result)
            if isinstance(channels, list) and len(channels) <= 5:
                return [channel.strip() for channel in channels if channel.strip()]
        except:
            # Fallback parsing if AI doesn't return perfect list format
            import re
            channels = re.findall(r'"([^"]*)"', result)
            return channels[:5] if channels else None
            
    except Exception as e:
        print(f"Error getting relevant channels: {e}")
        return None

def format_youtube_date(date_string):
    """Convert YouTube API date to MM/DD/YY format"""
    if not date_string or date_string in ['Unknown', 'N/A'] or date_string.startswith('sample'):
        return date_string
    
    try:
        from datetime import datetime
        # Handle both formats: 2025-08-08T14:00:36Z and other ISO formats
        if 'T' in date_string:
            # Remove timezone info and parse
            clean_date = date_string.replace('Z', '').split('T')[0]
            dt = datetime.strptime(clean_date, '%Y-%m-%d')
        else:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        
        return dt.strftime('%m/%d/%y')
    except Exception as e:
        print(f"Error formatting date {date_string}: {e}")
        return date_string
    """Search YouTube for recent videos from a specific channel"""
    if not api_key:
        # Return sample channel results
        sample_results = [
            {"title": f"Latest Video from {channel_name}", "views": "156K views", "published": "2 days ago", "description": f"Recent content from {channel_name}...", "video_id": f"sample_{channel_name}_1"},
            {"title": f"{channel_name}'s Hot Take on Current Events", "views": "89K views", "published": "1 day ago", "description": f"Commentary and analysis from {channel_name}...", "video_id": f"sample_{channel_name}_2"},
            {"title": f"Breaking: {channel_name} Responds", "views": "234K views", "published": "3 hours ago", "description": f"Response video from {channel_name}...", "video_id": f"sample_{channel_name}_3"},
        ]
        return sample_results
    
    try:
        # First, get the channel ID
        search_url = "https://www.googleapis.com/youtube/v3/search"
        search_params = {
            'part': 'snippet',
            'q': channel_name,
            'type': 'channel',
            'maxResults': 1,
            'key': api_key
        }
        
        search_response = requests.get(search_url, params=search_params, timeout=15)
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            if search_data.get('items'):
                channel_id = search_data['items'][0]['id']['channelId']
                
                # Now get recent videos from this channel
                videos_url = "https://www.googleapis.com/youtube/v3/search"
                videos_params = {
                    'part': 'snippet',
                    'channelId': channel_id,
                    'type': 'video',
                    'order': 'date',
                    'maxResults': max_results,
                    'key': api_key,
                    'publishedAfter': (datetime.now() - timedelta(days=30)).isoformat() + 'Z'
                }
                
                videos_response = requests.get(videos_url, params=videos_params, timeout=15)
                
                if videos_response.status_code == 200:
                    videos_data = videos_response.json()
                    channel_videos = []
                    
                    for item in videos_data.get('items', []):
                        snippet = item.get('snippet', {})
                        video_data = {
                            'title': snippet.get('title', 'No title'),
                            'published': snippet.get('publishedAt', 'Unknown'),
                            'video_id': item.get('id', {}).get('videoId', ''),
                            'description': snippet.get('description', '')[:200] + '...' if snippet.get('description') else '',
                            'channel': snippet.get('channelTitle', channel_name),
                            'views': 'N/A'  # Would need additional API call to get view count
                        }
                        channel_videos.append(video_data)
                    
                    return channel_videos
        
        # Fallback to sample data if API fails
        return search_youtube_by_channel(channel_name)
        
    except Exception as e:
        return search_youtube_by_channel(channel_name)  # Return sample data on error

# Now replace your entire YouTube Intelligence platform section with this:

if platform == "YouTube Intelligence":
    # Hero-style header
    st.markdown("""
    <div style="margin-bottom: 4rem;">
        <h1 style="font-size: 64px; font-weight: 900; text-transform: uppercase; letter-spacing: -2px; margin-bottom: 1rem;">
        YouTube <span style="color: #BCE5F7;">Center</span>
        </h1>
        <p style="font-size: 24px; font-weight: 300; color: #666; max-width: 800px;">
        Discover trending content, analyze audience sentiment, and generate data-driven content strategies.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Clean tabs with new styling
    tab1, tab2 = st.tabs(["VIDEO SEARCH", "TRENDING ANALYSIS"])
    
    with tab1:
        # Clean search inputs with better spacing
        
        col1, col2 = st.columns([3, 1])
        with col1:
            search_keywords = st.text_input(
                "KEYWORDS", 
                placeholder="e.g., 'true crime stories', 'makeup tutorial'", 
                key="keyword_input",
                label_visibility="visible"
            )
        with col2:
            search_timeframe = st.selectbox(
                "TIMEFRAME", 
                ["Last 2 Days", "Last Week", "Last Month", "Anytime"], 
                key="youtube_timeframe"
            )
        
        search_channel = st.text_input(
            "CHANNEL NAMES", 
            placeholder="e.g., 'Bailey Sarian' or 'Ben Shapiro, Matt Walsh, Daily Wire'", 
            key="channel_input",
            help="Enter one channel or multiple channels separated by commas"
        )
        
        video_url = st.text_input(
            "VIDEO URL", 
            placeholder="e.g., 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'", 
            key="video_url_input"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Search button - styled as primary CTA
        if st.button("SEARCH YOUTUBE", key="search_youtube", type="primary", use_container_width=True):
            search_results = [] # Initialize search_results here
            
            # Extract video ID from URL if provided
            if video_url:
                video_id = None
                if "youtube.com/watch?v=" in video_url:
                    video_id = video_url.split("v=")[1].split("&")[0]
                elif "youtu.be/" in video_url:
                    video_id = video_url.split("youtu.be/")[1].split("?")[0]
                else:
                    # Assume it's just the video ID
                    video_id = video_url.strip()
                
                if video_id:
                    # Fetch specific video details
                    st.info(f"🎥 Fetching video: {video_id}")
                    video_details = get_video_by_id(video_id, youtube_api_key)
                    if video_details:
                        search_results.append(video_details)
                    else:
                        # Fallback if API fails
                        search_results.append({
                            "title": f"Video: {video_id}",
                            "channel": "Unable to fetch details",
                            "views": "N/A",
                            "published": "N/A",
                            "video_id": video_id,
                            "description": "Could not retrieve video details. Check your API key.",
                            "thumbnail": f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"
                        })
            
            # Handle multiple channels separated by commas
            if search_keywords and search_channel:
                # Parse multiple channels
                channels = [channel.strip() for channel in search_channel.split(',') if channel.strip()]
                
                with st.spinner(f"🔍 Searching for '{search_keywords}' across {len(channels)} channel(s)..."):
                    for channel_name in channels:
                        # Search within each channel for the keywords
                        search_url = "https://www.googleapis.com/youtube/v3/search"
                        channel_params = {
                            'part': 'snippet',
                            'q': channel_name,
                            'type': 'channel',
                            'maxResults': 1,
                            'key': youtube_api_key
                        }
                        
                        try:
                            channel_response = requests.get(search_url, params=channel_params, timeout=15)
                            
                            if channel_response.status_code == 200:
                                channel_data = channel_response.json()
                                if channel_data.get('items'):
                                    channel_id = channel_data['items'][0]['id']['channelId']
                                    
                                    # Now search for keywords within this channel
                                    video_params = {
                                        'part': 'snippet',
                                        'channelId': channel_id,
                                        'q': search_keywords,
                                        'type': 'video',
                                        'order': 'relevance',
                                        'maxResults': 5,  # Limit per channel to avoid too many results
                                        'key': youtube_api_key
                                    }
                                    
                                    # Add timeframe filter
                                    timeframe_map = {
                                        "Last 2 Days": 2,
                                        "Last Week": 7, 
                                        "Last Month": 30,
                                        "Anytime": None
                                    }
                                    days = timeframe_map.get(search_timeframe)
                                    if days:
                                        published_after = (datetime.now() - timedelta(days=days)).isoformat() + 'Z'
                                        video_params['publishedAfter'] = published_after
                                    
                                    video_response = requests.get(search_url, params=video_params, timeout=15)
                                    
                                    if video_response.status_code == 200:
                                        video_data = video_response.json()
                                        
                                        for item in video_data.get('items', []):
                                            snippet = item.get('snippet', {})
                                            
                                            # Format published date to MM/DD/YY
                                            published_raw = snippet.get('publishedAt', '')
                                            formatted_date = format_youtube_date(published_raw)
                                            
                                            video_id = item.get('id', {}).get('videoId', '')
                                            
                                            video_data = {
                                              'title': snippet.get('title', 'No title'),
                                              'channel': snippet.get('channelTitle', 'Unknown Channel'),
                                              'views': get_video_views(item.get('id', ''), api_key),
                                              'published': format_youtube_date(snippet.get('publishedAt', 'Unknown')),
                                              'video_id': item.get('id', ''),
                                              'description': snippet.get('description', '')[:200] + '...' if snippet.get('description') else '',
                                              'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', '')
                                            }
                                            search_results.append(video_data)
                        except Exception as e:
                            st.warning(f"⚠️ Search failed for {channel_name}: {str(e)[:30]}...")
                    
                    if search_results:
                        st.success(f"✅ Found videos matching '{search_keywords}' across channels")
            
            # Search by keywords only (when no channel specified)
            elif search_keywords and not search_channel:
                # Convert timeframe to API parameter
                timeframe_map = {
                    "Last 2 Days": "2days",
                    "Last Week": "week", 
                    "Last Month": "month",
                    "Anytime": "any"
                }
                timeframe_param = timeframe_map.get(search_timeframe, "week")
                
                with st.spinner(f"🔍 Searching for '{search_keywords}'..."):
                    keyword_results = search_youtube_videos(search_keywords, youtube_api_key, timeframe=timeframe_param, search_type="video")
                    if keyword_results:
                        search_results.extend(keyword_results)
            
            # Search by channel only (when no keywords specified)
            elif search_channel and not search_keywords:
                # Parse multiple channels
                channels = [channel.strip() for channel in search_channel.split(',') if channel.strip()]
                
                with st.spinner(f"🔍 Searching {len(channels)} channel(s)..."):
                    for channel_name in channels:
                        channel_results = search_youtube_by_channel(channel_name, youtube_api_key, max_results=5)
                        if channel_results:
                            # Format dates for channel results too
                            for result in channel_results:
                                result['published'] = format_youtube_date(result.get('published', ''))
                                # Also try to get views for channel results
                                if result.get('video_id') and not result.get('video_id', '').startswith('sample'):
                                    result['views'] = get_video_views(result['video_id'], youtube_api_key)
                            search_results.extend(channel_results)
            
            # Store and display results
            if search_results:
                # Remove duplicates based on video_id
                unique_results = []
                seen_ids = set()
                for result in search_results:
                    if result['video_id'] not in seen_ids:
                        unique_results.append(result)
                        seen_ids.add(result['video_id'])
                
                # Sort by view count (highest first)
                unique_results.sort(key=lambda x: extract_view_count_for_sorting(x.get('views', 'N/A')), reverse=True)

                
                st.session_state.youtube_search_results = unique_results
                st.success(f"✅ Found {len(unique_results)} unique videos (sorted by views)")
            else:
                st.error("❌ No results found. Try different search criteria.")

        # Display search results if they exist in session state
        if 'youtube_search_results' in st.session_state and st.session_state.youtube_search_results:
            search_results = st.session_state.youtube_search_results
            
            for i, video in enumerate(search_results, 1):
                expanded_key = f"expanded_video_{i}"
                if expanded_key not in st.session_state:
                    st.session_state[expanded_key] = False
                    
                # Check if any button for this video was clicked
                if (f"analyze_video_{i}" in st.session_state or 
                    f"comments_{i}" in st.session_state or
                    f"reaction_analysis_{i}" in st.session_state or
                    f"comment_analysis_{i}" in st.session_state):
                    st.session_state[expanded_key] = True

                with st.expander(
                                    f"{i:02d} | {video['title'][:45]}{'...' if len(video['title']) > 45 else ''} | {video.get('channel', 'Unknown Channel')}", 
                                    expanded=st.session_state[expanded_key]
                                ):
                                    # Add clean metric display
                                    st.markdown(f"""
                                    <div style="display: flex; gap: 3rem; margin-bottom: 2rem;">
                                        <div>
                                        <p style="font-size: 14px; text-transform: uppercase; color: #666; margin-bottom: 0.5rem;">Channel</p>
                                        <p style="font-size: 20px; font-weight: 600;">{video['channel']}</p>
                                        </div>
                                        <div>
                                        <p style="font-size: 14px; text-transform: uppercase; color: #666; margin-bottom: 0.5rem;">Views</p>
                                        <p style="font-size: 20px; font-weight: 600;">{video.get('views', 'N/A')}</p>
                                        </div>
                                        <div>
                                        <p style="font-size: 14px; text-transform: uppercase; color: #666; margin-bottom: 0.5rem;">Published</p>
                                        <p style="font-size: 20px; font-weight: 600;">{video['published']}</p>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Add description and thumbnail
                                    if video.get('description'):
                                        st.write(f"**Description:** {video['description']}")

                                    if video.get('thumbnail'):
                                        st.image(video['thumbnail'], width=200)
                                    
                                    if video.get('video_id') and youtube_api_key and not video['video_id'].startswith('sample'):
                                        st.video(f"https://www.youtube.com/watch?v={video['video_id']}")
                                    
                                    # Automatic comment fetching and AI analysis (like Reddit)
                                    if api_key and creator_name:
                                        with st.spinner(f"🤖 Analyzing video and comments for {creator_name}..."):
                                            # Fetch comments automatically
                                            comments = get_youtube_comments(video.get('video_id', ''), youtube_api_key)
                                            
                                            # Auto-analyze video + comments
                                            analysis = analyze_video_for_creator_auto(video, comments, creator_name, api_key)
                                            
                                            if analysis and not analysis.startswith("AI Analysis Error"):
                                                st.markdown('<div class="ai-analysis">', unsafe_allow_html=True)
                                                st.markdown(f"### 🤖 AI Analysis for {creator_name}")
                                                
                                                # Show top comments first (like Reddit)
                                                if comments:
                                                    st.write("**Top Comments:**")
                                                    for j, comment in enumerate(comments[:3], 1):
                                                        st.write(f"{j}. **{comment['author']}** ({comment['likes']} ❤️): {comment['text'][:100]}...")
                                                    st.write("---")
                                                
                                                # Show AI analysis
                                                st.write(analysis)
                                                st.markdown('</div>', unsafe_allow_html=True)
                                            elif analysis:
                                                st.error(analysis)
                                    else:
                                        st.info("💡 Enter creator name and OpenAI API key for automatic AI analysis")

        # Two-column intro
        st.markdown("""
        <div class="two-column" style="margin-bottom: 3rem;">
        <div>
            <h2 style="font-size: 36px; font-weight: 800; text-transform: uppercase; margin-bottom: 1rem;">
            Search <span style="color: #BCE5F7;">Smarter</span>
            </h2>
            <p style="font-size: 20px; font-weight: 300; line-height: 1.6;">
            Find videos by keywords, channels, or direct URLs. Apply time filters to discover the freshest content.
            </p>
        </div>
        <div style="padding-left: 3rem;">
            <div class="numbered-list">
            <div style="display: flex; align-items: center; margin-bottom: 1.5rem; padding-bottom: 1.5rem; border-bottom: 1px solid #e0e0e0;">
                <span style="font-size: 44px; font-weight: 800; color: #BCE5F7; margin-right: 1.5rem;">01</span>
                <span style="font-size: 18px;">Enter search criteria</span>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 1.5rem; padding-bottom: 1.5rem; border-bottom: 1px solid #e0e0e0;">
                <span style="font-size: 44px; font-weight: 800; color: #BCE5F7; margin-right: 1.5rem;">02</span>
                <span style="font-size: 18px;">Analyze results with AI</span>
            </div>
            <div style="display: flex; align-items: center;">
                <span style="font-size: 44px; font-weight: 800; color: #BCE5F7; margin-right: 1.5rem;">03</span>
                <span style="font-size: 18px;">Generate content ideas</span>
            </div>
            </div>
        </div>
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        st.subheader("What's Trending on YouTube")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            if st.button("Get Trending Videos", key="get_youtube_trending"):
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
                    expanded_key = f"expanded_trending_{i}"
                    if expanded_key not in st.session_state:
                        st.session_state[expanded_key] = False
                        
                    # Check if button for this video was clicked
                    if f"reaction_trending_{i}" in st.session_state:
                        st.session_state[expanded_key] = True

                    with st.expander(
                        f"{i:02d} | {video['title'][:45]}{'...' if len(video['title']) > 45 else ''} | {video['channel']}", 
                        expanded=st.session_state[expanded_key]
                    ):
                        # Format trending video dates to MM/DD/YY
                        formatted_date = format_youtube_date(video.get('published', ''))
                        
                        # Add clean metric display for trending videos
                        st.markdown(f"""
                        <div style="display: flex; gap: 3rem; margin-bottom: 2rem;">
                        <div>
                            <p style="font-size: 14px; text-transform: uppercase; color: #666; margin-bottom: 0.5rem;">Channel</p>
                            <p style="font-size: 20px; font-weight: 600;">{video['channel']}</p>
                        </div>
                        <div>
                            <p style="font-size: 14px; text-transform: uppercase; color: #666; margin-bottom: 0.5rem;">Views</p>
                            <p style="font-size: 20px; font-weight: 600;">{video['views']}</p>
                        </div>
                        <div>
                            <p style="font-size: 14px; text-transform: uppercase; color: #666; margin-bottom: 0.5rem;">Published</p>
                            <p style="font-size: 20px; font-weight: 600;">{formatted_date}</p>
                        </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # After the metric display HTML, add:
                        if video.get('description'):
                            st.write(f"**Description:** {video['description']}")

                        if video.get('thumbnail'):
                            st.image(video['thumbnail'], width=200)

                        # Creator reaction analysis for each video
                        if api_key:
                            if st.button(f"{creator_name} Reaction Ideas", key=f"reaction_trending_{i}"):
                                with st.spinner(f"🤖 Analyzing reaction opportunities for {creator_name}..."):
                                    reaction_prompt = f"""Analyze this trending YouTube video for {creator_name}'s reaction content:

Title: {video['title']}
Channel: {video['channel']}
Views: {video['views']}
Description: {video.get('description', 'No description')}

Provide {creator_name}'s reaction strategy:

REACTION VIDEO TITLE: Catchy title for {creator_name}'s reaction video
{creator_name.upper()} ANGLE: How {creator_name} would uniquely react based on their personality/brand
HOT TAKES: 3 specific points {creator_name} would likely make during the reaction
OPENING HOOK: How {creator_name} should start the reaction to grab attention
BEST MOMENTS: Which parts of the original video to focus on for maximum impact
SOCIAL CLIPS: 2-3 short clips perfect for TikTok/Instagram from the reaction
ENGAGEMENT STRATEGY: How to get viewers commenting and sharing"""
                                    
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
                                        st.markdown("""
                                        <h3 style="font-size: 24px; font-weight: 800; text-transform: uppercase; margin-bottom: 1.5rem;">
                                        AI Analysis <span style="color: #BCE5F7;">Results</span>
                                        </h3>
                                        """, unsafe_allow_html=True)
                                        st.write(response.choices[0].message.content)
                                        st.markdown('</div>', unsafe_allow_html=True)
                                    except Exception as e:
                                        st.error(f"AI Analysis Error: {str(e)}")

                        if video.get('video_id') and youtube_api_key and not video['video_id'].startswith('sample'):
                            st.video(f"https://www.youtube.com/watch?v={video['video_id']}")

elif platform == "Podcast Trends":
    # Get Spotify credentials
    _, _, spotify_client_id, spotify_client_secret, _ = get_api_keys()
    
    # Hero-style header
    st.markdown("""
    <div style="margin-bottom: 4rem;">
        <h1 style="font-size: 64px; font-weight: 900; text-transform: uppercase; letter-spacing: -2px; margin-bottom: 1rem;">
            Podcast <span style="color: #BCE5F7;">Trends</span>
        </h1>
        <p style="font-size: 24px; font-weight: 300; color: #666; max-width: 800px;">
            Discover trending podcasts, find episodes about specific topics, and track what's popular in audio content.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get Spotify token
    if spotify_client_id and spotify_client_secret:
        if 'spotify_token' not in st.session_state:
            with st.spinner("Authenticating with Spotify..."):
                token = get_spotify_token(spotify_client_id, spotify_client_secret)
                if token:
                    st.session_state.spotify_token = token
    else:
        st.error("❌ Please add SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET to Railway environment variables")
        st.stop()

    # Initialize tab state
    if 'podcast_active_tab' not in st.session_state:
        st.session_state.podcast_active_tab = 0

    # Create container for tabs
    tab_container = st.container()
    
    with tab_container:
        # Create tabs
        tab_list = ["TOP PODCASTS", "TOPIC SEARCH", "TOP EPISODES"]
        tabs = st.tabs(tab_list)
        
        # Simply use the stored active tab
        active_tab_index = st.session_state.podcast_active_tab
    
    # TAB 1: TOP PODCASTS
    with tabs[0]:
        st.markdown("### 🎙️ Top Podcasts by Genre (Apple Podcasts Charts)")
        
        # Genre selection
        col1, col2 = st.columns([3, 1])
        with col1:
            # iTunes genre mapping
            genre_options = [
                ("all", "All Genres"),
                ("business", "Business"),
                ("comedy", "Comedy"),
                ("education", "Education"),
                ("fiction", "Fiction"),
                ("government", "Government"),
                ("health", "Health & Fitness"),
                ("history", "History"),
                ("kids", "Kids & Family"),
                ("leisure", "Leisure"),
                ("music", "Music"),
                ("news", "News"),
                ("religion", "Religion & Spirituality"),
                ("science", "Science"),
                ("society", "Society & Culture"),
                ("sports", "Sports"),
                ("technology", "Technology"),
                ("true_crime", "True Crime"),
                ("tv_film", "TV & Film")
            ]
            
            selected_genre = st.selectbox(
                "Select Genre",
                options=[g[0] for g in genre_options],
                format_func=lambda x: dict(genre_options).get(x, x),
                key="podcast_genre"
            )
        
        with col2:
            limit = st.number_input("Show top", min_value=5, max_value=50, value=20, key="podcast_limit")
        
        if st.button("Get Top Podcasts", key="get_top_podcasts_btn", type="primary"):
            st.session_state.podcast_active_tab = 0
            # Genre ID mapping
            genre_ids = {
                "all": None,
                "business": 1321,
                "comedy": 1303,
                "education": 1304,
                "fiction": 1483,
                "government": 1511,
                "health": 1512,
                "history": 1487,
                "kids": 1305,
                "leisure": 1502,
                "music": 1310,
                "news": 1489,
                "religion": 1314,
                "science": 1533,
                "society": 1324,
                "sports": 1545,
                "technology": 1318,
                "true_crime": 1488,
                "tv_film": 1309
            }
            
            genre_id = genre_ids.get(selected_genre)
            genre_name = dict(genre_options).get(selected_genre, "All")
            
            with st.spinner(f"Fetching top {genre_name} podcasts from Apple Podcasts..."):
                podcasts = get_itunes_top_podcasts(genre_id, limit)
                
                if podcasts:
                    st.session_state.top_podcasts = podcasts
                    st.success(f"✅ Found top {len(podcasts)} {genre_name} podcasts")
        
        # Display results
        if 'top_podcasts' in st.session_state:
            for podcast in st.session_state.top_podcasts:
                with st.expander(f"#{podcast['rank']:02d} | 🎙️ {podcast['name']} - {podcast['artist']}", expanded=False):
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        if podcast['image']:
                            st.image(podcast['image'], width=150)
                    
                    with col2:
                        st.markdown(f"**Rank:** #{podcast['rank']} in {podcast['category']}")
                        st.write(f"**Host/Network:** {podcast['artist']}")
                        st.write(f"**Description:** {podcast['summary']}")
                        st.write(f"**Latest Release:** {podcast['release_date']}")
                        if podcast['url']:
                            st.write(f"[Listen on Apple Podcasts]({podcast['url']})")
    
    # TAB 2: TOPIC SEARCH
    with tabs[1]:
        st.markdown("### 🔍 Search Podcasts by Topic")
        
        # Topic search with sort option
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_topic = st.text_input(
                "Enter topic or current event",
                placeholder="e.g., 'Taylor Swift', 'Presidential Election', 'AI Technology'",
                key="topic_search"
            )
        
        with col2:
            sort_option = st.selectbox(
                "Sort by",
                ["Relevance", "Newest First", "Oldest First"],
                key="podcast_sort"
            )
        
        if st.button("Search Episodes", key="search_topic_btn", type="primary") and search_topic:
            st.session_state.podcast_active_tab = 1
            if 'spotify_token' in st.session_state:
                with st.spinner(f"Searching for episodes about '{search_topic}'..."):
                    episodes = search_podcasts_by_topic(st.session_state.spotify_token, search_topic)
                    if episodes:
                        # Sort based on selection
                        if sort_option == "Newest First":
                            episodes.sort(key=lambda x: x.get('release_date', ''), reverse=True)
                        elif sort_option == "Oldest First":
                            episodes.sort(key=lambda x: x.get('release_date', ''))
                        # If "Relevance" is selected, keep Spotify's default order
                        
                        st.session_state.topic_results = episodes
                        st.success(f"✅ Found {len(episodes)} episodes about '{search_topic}' (sorted by {sort_option})")

        # Display topic results
        if 'topic_results' in st.session_state:
            for i, ep in enumerate(st.session_state.topic_results, 1):
                # Show episode name with show name if available
                if ep.get('show_name') and ep['show_name'] != 'Loading...':
                    display_title = f"{ep['name']} - {ep['show_name']}"
                else:
                    display_title = ep['name']
                    
                with st.expander(f"{i:02d} | {display_title}", expanded=False):
                    if ep['image']:
                        st.image(ep['image'], width=200)
                    
                    st.write(f"**Released:** {ep['release_date']}")
                    st.write(f"**Duration:** {ep['duration_min']} minutes")
                    st.write(f"**Description:** {ep['description']}")
                    st.write(f"[Listen on Spotify]({ep['url']})")
    
    # TAB 3: TOP EPISODES
    with tabs[2]:
        st.markdown("### 🎧 Top Episodes by Genre")
        
        # Complete genre selection with all categories
        genre_options = [
            ("all", "All Categories"),
            ("news", "News"),
            ("comedy", "Comedy"),
            ("society", "Society & Culture"),
            ("business", "Business"),
            ("true_crime", "True Crime"),
            ("sports", "Sports"),
            ("health", "Health & Fitness"),
            ("religion", "Religion & Spirituality"),
            ("arts", "Arts"),
            ("education", "Education"),
            ("history", "History"),
            ("tv_film", "TV & Film"),
            ("science", "Science"),
            ("technology", "Technology"),
            ("music", "Music"),
            ("kids", "Kids & Family"),
            ("leisure", "Leisure"),
            ("fiction", "Fiction"),
            ("government", "Government")
        ]
        
        episode_genre = st.selectbox(
            "Select Genre for Top Episodes",
            options=[g[0] for g in genre_options],
            format_func=lambda x: dict(genre_options).get(x, x),
            key="episode_genre"
        )
        
        if st.button("Get Top Episodes", key="get_top_episodes", type="primary"):
            # Set flag to keep this tab active
            st.session_state.podcast_active_tab = 2
            
            genre_ids = {
                "all": None,
                "news": 1489,
                "comedy": 1303,
                "society": 1324,
                "business": 1321,
                "true_crime": 1488,
                "sports": 1545,
                "health": 1512,
                "religion": 1314,
                "arts": 1301,
                "education": 1304,
                "history": 1487,
                "tv_film": 1309,
                "science": 1533,
                "technology": 1318,
                "music": 1310,
                "kids": 1305,
                "leisure": 1502,
                "fiction": 1483,
                "government": 1511
            }
            
            genre_id = genre_ids.get(episode_genre)
            genre_name = dict(genre_options).get(episode_genre, "All")
            
            with st.spinner(f"Fetching top episodes in {genre_name}..."):
                # Get top podcasts in genre
                podcasts = get_itunes_top_podcasts(genre_id, limit=20)
                
                if podcasts:
                    all_episodes = []
                    
                    # Collect episodes with their parent podcast's rank
                    for podcast in podcasts:
                        if podcast['url']:
                            podcast_id = podcast['url'].split('/id')[-1].split('?')[0]
                            episodes = get_itunes_podcast_episodes(podcast_id, limit=1)  # Get only latest episode
                            
                            for ep in episodes:
                                ep['podcast_name'] = podcast['name']
                                ep['podcast_artist'] = podcast['artist']
                                ep['podcast_rank'] = podcast['rank']  # Store the podcast's rank
                                all_episodes.append(ep)
                    
                    # Sort episodes by their podcast's rank to maintain Apple's order
                    all_episodes.sort(key=lambda x: x['podcast_rank'])
                    
                    if all_episodes:
                        st.session_state.top_genre_episodes = all_episodes
                        st.success(f"✅ Found {len(all_episodes)} recent episodes from top {genre_name} podcasts")
                    else:
                        st.warning("No episodes found. Try a different genre.")
        
        # Display top episodes in order
        if 'top_genre_episodes' in st.session_state:
            st.markdown("---")
            for i, ep in enumerate(st.session_state.top_genre_episodes, 1):
                # Format matching your image: "01 | Episode Title - Podcast Name"
                with st.expander(f"{i:02d} | {ep['title']} - {ep['podcast_name']}", expanded=False):
                    st.write(f"**Podcast:** {ep['podcast_name']} by {ep['podcast_artist']}")
                    st.write(f"**Published:** {ep['published']}")
                    st.write(f"**Duration:** {ep['duration']}")
                    st.write(f"**Description:** {ep['description']}")
                    if ep.get('link'):
                        st.write(f"[Listen to Episode]({ep['link']})")
                    
                    # AI Analysis for episode
                    if api_key and st.button(f"🤖 {creator_name} Content Ideas", key=f"analyze_ep_{i}"):
                        with st.spinner(f"Analyzing for {creator_name}..."):
                            prompt = f"""Analyze this podcast episode for {creator_name}'s content strategy:

Episode: "{ep['title']}"
Podcast: {ep['podcast_name']}
Description: {ep['description']}

Provide content ideas for {creator_name}:

REACTION ANGLE: How {creator_name} could react to or discuss this episode
VIDEO TITLE: Specific title for {creator_name}'s video
KEY TOPICS: Main points to cover based on this episode
HOT TAKE: {creator_name}'s unique perspective
FORMAT: Best video format (reaction, analysis, story-time, etc.)
CROSS-PLATFORM: How to leverage this across YouTube, TikTok, Instagram"""
                            
                            try:
                                import openai
                                openai.api_key = api_key
                                
                                response = openai.ChatCompletion.create(
                                    model="gpt-4.1-nano",
                                    messages=[{"role": "user", "content": prompt}],
                                    max_tokens=600,
                                    timeout=30
                                )
                                
                                st.markdown('<div class="ai-analysis">', unsafe_allow_html=True)
                                st.markdown("""
                                <h3 style="font-size: 24px; font-weight: 800; text-transform: uppercase; margin-bottom: 1.5rem;">
                                    AI Analysis <span style="color: #BCE5F7;">Results</span>
                                </h3>
                                """, unsafe_allow_html=True)
                                st.write(response.choices[0].message.content)
                                st.markdown('</div>', unsafe_allow_html=True)
                                
                            except Exception as e:
                                st.error(f"❌ AI Analysis Error: {str(e)}")

elif platform == "Movie & TV Trends":
    # Hero-style header
    st.markdown("""
    <div style="margin-bottom: 4rem;">
        <h1 style="font-size: 64px; font-weight: 900; text-transform: uppercase; letter-spacing: -2px; margin-bottom: 1rem;">
            Movie & TV <span style="color: #BCE5F7;">Trends</span>
        </h1>
        <p style="font-size: 24px; font-weight: 300; color: #666; max-width: 800px;">
            Discover trending films and shows, analyze audience preferences, and create content around what's popular in entertainment.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if not tmdb_key:
        st.error("❌ Please add TMDB_API_KEY to Railway environment variables")
        st.info("Get your free API key at https://www.themoviedb.org/settings/api")
        st.stop()
    
    # Navigation tabs
    tab1, tab2 = st.tabs(["DISCOVER TRENDS", "SEARCH TITLES"])
    
    with tab1:
        st.markdown("### 🎬 Discover Trending Movies & Shows")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            media_type = st.selectbox(
                "Media Type",
                ["movie", "tv"],
                format_func=lambda x: "Movies" if x == "movie" else "TV Shows", 
                key="media_type_discover"
            )
        
        with col2:
            # Get genres for selected media type
            genres = get_tmdb_genres(tmdb_key, media_type)
            genre_options = [(str(gid), gname) for gid, gname in genres.items()]
            
            selected_genres = st.multiselect(
                "Genres (select multiple)",
                options=[g[0] for g in genre_options],
                format_func=lambda x: dict(genre_options).get(x, x),
                key="genre_multiselect",
                placeholder="Select genres or leave empty for all"
            )
        
        with col3:
            sort_options = [
                ("popularity.desc", "Most Popular"),
                ("vote_average.desc", "Highest Rated"),
                ("vote_count.desc", "Most Voted"),
                ("release_date.desc", "Newest First"),
                ("revenue.desc", "Highest Revenue")
            ]
            
            sort_by = st.selectbox(
                "Sort By",
                options=[s[0] for s in sort_options],
                format_func=lambda x: dict(sort_options).get(x, x),
                key="sort_select"
            )
        
        # Optional year filter
        col1, col2 = st.columns([1, 2])
        with col1:
            use_year_filter = st.checkbox("Filter by year", key="use_year_discover")
            if use_year_filter:
                year_filter = st.number_input(
                    "Year",
                    min_value=1900,
                    max_value=datetime.now().year + 1,
                    value=datetime.now().year, 
                    key="year_filter"
                )
            else:
                year_filter = None
        
        if st.button("🎬 Get Trending", key="get_trending", type="primary"):
            with st.spinner(f"Fetching trending {media_type}s..."):
                # Join multiple genre IDs with comma for TMDB API
                genre_ids = ','.join(selected_genres) if selected_genres else None
                year = year_filter if use_year_filter else None
                
                results = search_tmdb(tmdb_key, media_type=media_type, genre_id=genre_ids, 
                                    year=year, sort_by=sort_by)


                
                results = search_tmdb(tmdb_key, media_type=media_type, genre_id=genre_id, 
                                    year=year, sort_by=sort_by)
                
                if results and results.get('results'):
                    st.session_state.trending_results = results['results']
                    st.success(f"✅ Found {len(results['results'])} trending {media_type}s")
        
        # Display results
        if 'trending_results' in st.session_state:
            for i, item in enumerate(st.session_state.trending_results[:20], 1):
                title = item.get('title') or item.get('name', 'Unknown')
                release_date = item.get('release_date') or item.get('first_air_date', 'Unknown')
                
                with st.expander(f"{i:02d} | {title} ({release_date[:4] if release_date != 'Unknown' else 'N/A'})", expanded=False):
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        if item.get('poster_path'):
                            poster_url = f"https://image.tmdb.org/t/p/w200{item['poster_path']}"
                            st.image(poster_url, width=150)
                    
                    with col2:
                        # Metrics
                        st.markdown(f"""
                        <div style="display: flex; gap: 2rem; margin-bottom: 1rem;">
                            <div>
                                <p style="font-size: 24px; font-weight: 800; color: #BCE5F7; margin: 0;">⭐ {item.get('vote_average', 0):.1f}</p>
                                <p style="font-size: 12px; text-transform: uppercase; color: #666;">Rating</p>
                            </div>
                            <div>
                                <p style="font-size: 24px; font-weight: 800; color: #BCE5F7; margin: 0;">{item.get('vote_count', 0):,}</p>
                                <p style="font-size: 12px; text-transform: uppercase; color: #666;">Votes</p>
                            </div>
                            <div>
                                <p style="font-size: 24px; font-weight: 800; color: #BCE5F7; margin: 0;">{item.get('popularity', 0):.0f}</p>
                                <p style="font-size: 12px; text-transform: uppercase; color: #666;">Popularity</p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.write(f"**Overview:** {item.get('overview', 'No overview available.')}")
                        
                        # Get genre names
                        genre_names = [genres.get(gid, 'Unknown') for gid in item.get('genre_ids', [])]
                        if genre_names:
                            st.write(f"**Genres:** {', '.join(genre_names)}")
                    
                    # AI Analysis
                    if api_key and st.button(f"🤖 {creator_name} Content Strategy", key=f"analyze_tmdb_{i}"):
                        with st.spinner(f"Analyzing for {creator_name}..."):
                            media_type_display = "movie" if 'title' in item else "TV show"
                            analysis = analyze_movie_tv_trend(
                                title,
                                item.get('overview', ''),
                                item.get('popularity', 0),
                                item.get('vote_average', 0),
                                media_type_display,
                                genre_names,
                                creator_name,
                                api_key
                            )
                            
                            if analysis:
                                st.markdown('<div class="ai-analysis">', unsafe_allow_html=True)
                                st.markdown("""
                                <h3 style="font-size: 24px; font-weight: 800; text-transform: uppercase; margin-bottom: 1.5rem;">
                                    AI Analysis <span style="color: #BCE5F7;">Results</span>
                                </h3>
                                """, unsafe_allow_html=True)
                                st.write(analysis)
                                st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 🔍 Search Movies & TV Shows")
        
        search_query = st.text_input(
            "Search by Title/Keyword",
            placeholder="e.g., 'Star Wars', 'zombie', 'superhero'",
            key="title_search"
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            search_media_type = st.selectbox(
                "Media Type",
                ["movie", "tv"],
                format_func=lambda x: "Movies" if x == "movie" else "TV Shows",
                key="media_type_search"
            )
        
        with col2:
            use_search_year = st.checkbox("Filter by year", key="use_year_search")
            if use_search_year:
                search_year = st.number_input(
                    "Year",
                    min_value=1900,
                    max_value=datetime.now().year + 1,
                    value=datetime.now().year,
                    key="search_year"
                )
            else:
                search_year = None
        
        if st.button("🔍 Search", key="search_titles", type="primary") and search_query:
            with st.spinner(f"Searching for '{search_query}'..."):
                # First do the search
                results = search_tmdb(tmdb_key, query=search_query, media_type=search_media_type, year=search_year)
                
                if results and results.get('results'):
                    # Store raw results for sorting
                    st.session_state.search_results_raw = results['results']
                    st.session_state.search_query_used = search_query
                    st.session_state.search_media_type_used = search_media_type
                    st.success(f"✅ Found {len(results['results'])} results for '{search_query}'")
                else:
                    st.warning("No results found. Try different keywords.")
        
        # If we have search results, show sorting options
        if 'search_results_raw' in st.session_state and st.session_state.search_results_raw:
            st.markdown("---")
            st.markdown(f"**Results for: '{st.session_state.search_query_used}'**")
            
            # Sorting options
            sort_options = [
                ("popularity", "Most Popular"),
                ("vote_average", "Highest Rated"),
                ("vote_count", "Most Voted"),
                ("release_date", "Newest First"),
                ("title", "Alphabetical")
            ]
            
            sort_by = st.selectbox(
                "Sort Results By",
                options=[s[0] for s in sort_options],
                format_func=lambda x: dict(sort_options).get(x, x),
                key="search_sort"
            )
            
            # Sort the results
            sorted_results = sorted(
                st.session_state.search_results_raw,
                key=lambda x: x.get(sort_by, 0) if sort_by != 'title' else (x.get('title') or x.get('name', '')),
                reverse=(sort_by != 'title')
            )
            
            # Get genres for the selected media type
            genres = get_tmdb_genres(tmdb_key, st.session_state.search_media_type_used)
            
            # Display sorted results
            for i, item in enumerate(sorted_results[:20], 1):
                title = item.get('title') or item.get('name', 'Unknown')
                release_date = item.get('release_date') or item.get('first_air_date', 'Unknown')
                
                with st.expander(f"{i:02d} | {title} ({release_date[:4] if release_date != 'Unknown' and len(release_date) >= 4 else 'N/A'})", expanded=False):
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        if item.get('poster_path'):
                            poster_url = f"https://image.tmdb.org/t/p/w200{item['poster_path']}"
                            st.image(poster_url, width=150)
                    
                    with col2:
                        # Metrics
                        st.markdown(f"""
                        <div style="display: flex; gap: 2rem; margin-bottom: 1rem;">
                            <div>
                                <p style="font-size: 24px; font-weight: 800; color: #BCE5F7; margin: 0;">⭐ {item.get('vote_average', 0):.1f}</p>
                                <p style="font-size: 12px; text-transform: uppercase; color: #666;">Rating</p>
                            </div>
                            <div>
                                <p style="font-size: 24px; font-weight: 800; color: #BCE5F7; margin: 0;">{item.get('vote_count', 0):,}</p>
                                <p style="font-size: 12px; text-transform: uppercase; color: #666;">Votes</p>
                            </div>
                            <div>
                                <p style="font-size: 24px; font-weight: 800; color: #BCE5F7; margin: 0;">{item.get('popularity', 0):.0f}</p>
                                <p style="font-size: 12px; text-transform: uppercase; color: #666;">Popularity</p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.write(f"**Overview:** {item.get('overview', 'No overview available.')}")
                        
                        # Get genre names
                        genre_names = [genres.get(gid, 'Unknown') for gid in item.get('genre_ids', [])]
                        if genre_names:
                            st.write(f"**Genres:** {', '.join(genre_names)}")
                    
                    # AI Analysis
                    if api_key and st.button(f"🤖 {creator_name} Content Strategy", key=f"analyze_search_{i}"):
                        with st.spinner(f"Analyzing for {creator_name}..."):
                            media_type_display = "movie" if 'title' in item else "TV show"
                            analysis = analyze_movie_tv_trend(
                                title,
                                item.get('overview', ''),
                                item.get('popularity', 0),
                                item.get('vote_average', 0),
                                media_type_display,
                                genre_names,
                                creator_name,
                                api_key
                            )
                            
                            if analysis:
                                st.markdown('<div class="ai-analysis">', unsafe_allow_html=True)
                                st.markdown("""
                                <h3 style="font-size: 24px; font-weight: 800; text-transform: uppercase; margin-bottom: 1.5rem;">
                                    AI Analysis <span style="color: #BCE5F7;">Results</span>
                                </h3>
                                """, unsafe_allow_html=True)
                                st.write(analysis)
                                st.markdown('</div>', unsafe_allow_html=True)
                        

elif platform == "Reddit Analysis":
  # Hero-style header
  st.markdown("""
  <div style="margin-bottom: 2rem;">
    <h1 style="font-size: 64px; font-weight: 900; text-transform: uppercase; letter-spacing: -2px; margin-bottom: 1rem;">
      Reddit Content <span style="color: #BCE5F7;">Analysis</span>
    </h1>
    <p style="font-size: 24px; font-weight: 300; color: #666; max-width: 800px; margin-bottom: 2rem;">
      Discover viral discussions, analyze community sentiment, and create content that resonates.
    </p>
    <hr style="border: none; height: 1px; background-color: #e0e0e0; margin: 0;">
  </div>
  """, unsafe_allow_html=True)
  
  # Handle dynamic subreddit selection
  if 'selected_subreddits' in st.session_state:
      # Filter AI suggestions to only include ones that exist in our options
      suggested_subreddits = st.session_state.selected_subreddits
      
      # Base subreddit options
      subreddit_options = [
        "TrueCrime", "AskReddit", "politics", "Conservative", "news", "worldnews", 
        "technology", "movies", "television", "music", "gaming", "sports",
        "funny", "todayilearned", "science", "relationships", "food", "fitness",
        "travel", "books", "photography", "MakeupAddiction", "beauty", "serialkillers",
        "UnresolvedMysteries", "nosleep", "LetsNotMeet", "creepy", "entertainment"
      ]
      
      # Add any AI-suggested subreddits that aren't already in the list
      for subreddit in suggested_subreddits:
        if subreddit not in subreddit_options:
          subreddit_options.append(subreddit)
      
      # Filter suggested subreddits to only valid ones
      valid_defaults = [sub for sub in suggested_subreddits if sub in subreddit_options]
      default_subreddits = valid_defaults if valid_defaults else ["UnresolvedMysteries"]
  else:
      # Base subreddit options
      subreddit_options = [
        "TrueCrime", "AskReddit", "politics", "Conservative", "news", "worldnews", 
        "technology", "movies", "television", "music", "gaming", "sports",
        "funny", "todayilearned", "science", "relationships", "food", "fitness",
        "travel", "books", "photography", "MakeupAddiction", "beauty", "serialkillers",
        "UnresolvedMysteries", "nosleep", "LetsNotMeet", "creepy", "entertainment"
      ]
      default_subreddits = ["UnresolvedMysteries"]

  # Clean main search section
  st.markdown('<h3 style="font-size: 18px; font-weight: 700; text-transform: uppercase; margin-bottom: 1.5rem; color: #221F1F; margin-top: 2rem;">SEARCH REDDIT</h3>', unsafe_allow_html=True)
  
  # Search inputs in a clean layout
  col1, col2 = st.columns([2, 1])
        
  with col1:
      # Keywords search input
      search_keywords = st.text_input(
        "SEARCH KEYWORDS (optional)", 
        placeholder="e.g., 'trump speech', 'taylor swift', 'election news'", 
        key="keywords_input",
        help="Leave empty to browse subreddits without keyword filtering"
      )
      
      # Multi-select subreddit input (using the options defined above)
      selected_subreddits = st.multiselect(
        "SUBREDDIT NAMES (optional)",
        options=subreddit_options,
        default=default_subreddits,
        placeholder="Select subreddits to search",
        help="Choose from popular subreddits or add custom ones below"
      )
      
      # Custom subreddit input
      custom_subreddit = st.text_input(
        "ADD CUSTOM SUBREDDIT",
        placeholder="e.g., cryptocurrency, wallstreetbets",
        key="custom_subreddit_input",
        help="Type any subreddit name and press Enter to add it"
      )
      
      # Add custom subreddit to selection
      if custom_subreddit:
        # Clean the input (remove r/ if present)
        clean_subreddit = custom_subreddit.replace("r/", "").strip()
        
        if clean_subreddit and clean_subreddit not in selected_subreddits:
          # Add to current selection
          updated_selection = selected_subreddits + [clean_subreddit]
          
          # Update session state to include the custom subreddit
          st.session_state.custom_added = True
          st.session_state.updated_subreddits = updated_selection
          
          # Show success message
          st.success(f"✅ Added r/{clean_subreddit}")
          
          # Auto-rerun to update the multiselect
          st.rerun()
      
      # Use updated selection if custom subreddit was added
      if hasattr(st.session_state, 'custom_added') and st.session_state.custom_added:
        final_subreddits = st.session_state.updated_subreddits
        st.session_state.custom_added = False  # Reset flag
      else:
        final_subreddits = selected_subreddits

  with col2:
    # Post category selection
    post_category = st.selectbox(
      "POST TYPE", 
      ["hot", "top", "rising", "new"], 
      format_func=lambda x: {
        "hot": "Hot Posts",
        "top": "Top Posts", 
        "rising": "Rising Posts",
        "new": "New Posts"
      }.get(x, x),
      key="category_select"
    )
    
    # Post limit
    post_limit = st.slider(
      "NUMBER OF POSTS", 
      2, 15, 5, 
      key="post_limit_slider"
    )
  
  # Search logic explanation
  if search_keywords and selected_subreddits:
    search_description = f"Search for '{search_keywords}' in {len(selected_subreddits)} selected subreddits"
  elif search_keywords and not selected_subreddits:
    search_description = f"Search for '{search_keywords}' across all of Reddit"
  elif not search_keywords and selected_subreddits:
    search_description = f"Browse {post_category} posts from {len(selected_subreddits)} selected subreddits"
  else:
    search_description = "Enter keywords or select subreddits to search"
  
  st.markdown(f"""
  <div style="text-align: center; margin-bottom: 2rem;">
    <p style="font-size: 18px; color: #666; font-style: italic;">{search_description}</p>
  </div>
  """, unsafe_allow_html=True)
  
  # Search buttons side by side
  col1, col2, col3 = st.columns([1, 1, 1])
  
  with col1:
    if st.button("🔍 SEARCH REDDIT", type="primary", key="search_reddit_btn", use_container_width=True):
      if not search_keywords and not selected_subreddits:
        st.warning("Please enter keywords or select subreddits to search")
      else:
        st.session_state.should_search = True
        st.session_state.search_params = {
          'keywords': search_keywords,
          'subreddits': selected_subreddits,
          'category': post_category,
          'limit': post_limit
        }
  
  with col2:
    if st.button("🎯 GET RELEVANT SUBREDDITS", key="get_relevant_btn", use_container_width=True):
      if creator_name:
        with st.spinner(f"Finding relevant subreddits for {creator_name}..."):
          relevant_subreddits = get_relevant_subreddits_for_creator(creator_name, api_key)
          if relevant_subreddits:
            # Take only top 5 most relevant
            top_5_subreddits = relevant_subreddits[:5]
            
            # Update the multiselect with these subreddits
            st.session_state.selected_subreddits = top_5_subreddits
            st.success(f"✅ Added {len(top_5_subreddits)} relevant subreddits for {creator_name}")
            st.info(f"Selected: {', '.join(top_5_subreddits)}")
            
            # Force rerun to update the multiselect display
            st.rerun()
          else:
            st.error("❌ Could not get relevant subreddits. Check your API key.")
      else:
        st.warning("Please enter a creator name in the sidebar first")
  
  # Execute search when button is clicked
  if hasattr(st.session_state, 'should_search') and st.session_state.should_search:
    st.session_state.should_search = False
    params = st.session_state.search_params
    
    keywords = params['keywords']
    subreddits = params['subreddits']
    category = params['category']
    limit = params['limit']
    
    # Determine search strategy
    if keywords and subreddits:
      # Search for keywords within selected subreddits
      st.info(f"🔍 Searching for '{keywords}' in {len(subreddits)} subreddits...")
      
      all_posts = []
      for subreddit in subreddits:
        # Get posts from the subreddit
        posts = get_reddit_posts(subreddit, category, limit)
        
        if posts:
          # Filter posts that contain the keywords
          keywords_lower = keywords.lower()
          for post in posts:
            post_data = post['data']
            title = post_data.get('title', '').lower()
            selftext = post_data.get('selftext', '').lower()
            
            # Check if keywords appear in title or content
            if keywords_lower in title or keywords_lower in selftext:
              post['data']['source_subreddit'] = subreddit
              all_posts.append(post)
      
      if all_posts:
        # Sort by score and limit results
        all_posts.sort(key=lambda x: x['data']['score'], reverse=True)
        limited_posts = all_posts[:limit]
        
        st.success(f"✅ Found {len(limited_posts)} posts containing '{keywords}' in selected subreddits")
        
        # Group by subreddit for display
        grouped_posts = {}
        for post in limited_posts:
          sub = post['data']['source_subreddit']
          if sub not in grouped_posts:
            grouped_posts[sub] = []
          grouped_posts[sub].append(post)
        
        for sub, sub_posts in grouped_posts.items():
          st.subheader(f"r/{sub} ({len(sub_posts)} posts)")
          display_posts(sub_posts, sub, api_key, creator_name)
      else:
        st.warning(f"No posts found containing '{keywords}' in selected subreddits")
    
    elif keywords and not subreddits:
      # Search keywords across all Reddit
      st.info(f"🔍 Searching for '{keywords}' across all of Reddit...")
      
      try:
        search_url = "https://www.reddit.com/search.json"
        params_dict = {
          'q': keywords,
          'sort': 'top' if category == 'top' else 'hot',
          't': 'day',
          'limit': limit * 2,
          'type': 'link',
          'raw_json': 1
        }
        
        time.sleep(2)
        response = requests.get(search_url, headers=HEADERS, params=params_dict, timeout=15)
        
        if response.status_code == 200:
          data = response.json()
          if 'data' in data and 'children' in data['data'] and data['data']['children']:
            posts = data['data']['children'][:limit]
            
            # Add source subreddit info for display
            for post in posts:
              post['data']['source_subreddit'] = post['data']['subreddit']
            
            st.success(f"✅ Found {len(posts)} posts matching '{keywords}' across Reddit")
            
            # Group by subreddit for better organization
            grouped_posts = {}
            for post in posts:
              sub = post['data']['source_subreddit']
              if sub not in grouped_posts:
                grouped_posts[sub] = []
              grouped_posts[sub].append(post)
            
            for sub, sub_posts in grouped_posts.items():
              st.subheader(f"r/{sub} ({len(sub_posts)} posts)")
              display_posts(sub_posts, sub, api_key, creator_name)
              
          else:
            st.warning(f"No posts found for '{keywords}'. Try different keywords.")
        else:
          st.error("Search failed. Try selecting specific subreddits instead.")
      except Exception as e:
        st.error(f"Search error: {str(e)}. Try selecting specific subreddits instead.")
    
    elif not keywords and subreddits:
      # Browse selected subreddits by category
      st.info(f"🔍 Getting {category} posts from {len(subreddits)} selected subreddits...")
      
      all_posts_found = False
      
      for subreddit in subreddits:
        with st.spinner(f"Fetching {category} posts from r/{subreddit}..."):
          posts = get_reddit_posts(subreddit, category, limit)
          
          if posts:
            all_posts_found = True
            st.subheader(f"{category.title()} posts from r/{subreddit}")
            display_posts(posts, subreddit, api_key, creator_name)
          else:
            st.warning(f"❌ Could not fetch posts from r/{subreddit}")

      if not all_posts_found:
        st.error(f"❌ Could not fetch posts from any selected subreddits. Try different subreddits.")
    
    else:
      st.warning("Please enter keywords or select subreddits to search")

  # Batch export section
  if 'analyzed_posts' in st.session_state and st.session_state.analyzed_posts:
    st.markdown("---")
    st.markdown("### Export Analysis")
    col1, col2, col3 = st.columns([2, 2, 1])
    with col3:
      all_analyses = "\n\n" + "="*50 + "\n\n".join(st.session_state.analyzed_posts)
      st.download_button(
        label=f"📄 Export All ({len(st.session_state.analyzed_posts)} posts)",
        data=all_analyses,
        file_name=f"{creator_name}_batch_export_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
        mime="text/plain",
        help="Download all analyzed posts in one file",
        use_container_width=True
      )

  # Popular Subreddits - Quick selection
  st.markdown("---")
  st.markdown("### Popular Subreddits")
  st.markdown("*Click any subreddit to quickly add it to your selection*")
  
  popular_subreddits = [
    ("TrueCrime", "🔍"), ("AskReddit", "🤷"), ("politics", "🗳️"), ("Conservative", "🇺🇸"),
    ("news", "📰"), ("worldnews", "🌍"), ("technology", "💻"), ("movies", "🎬"),
    ("television", "📺"), ("music", "🎵"), ("gaming", "🎮"), ("sports", "⚽"),
    ("funny", "😂"), ("todayilearned", "🧠"), ("science", "🔬"), ("relationships", "💕"),
    ("food", "🍕"), ("fitness", "💪"), ("travel", "✈️"), ("books", "📚"),
    ("photography", "📸"), ("dataisbeautiful", "📊"), ("explainlikeimfive", "🧒"), ("lifehacks", "💡")
  ]
  
  # Display in 4 columns
  cols = st.columns(4)
  for i, (subreddit, emoji) in enumerate(popular_subreddits):
    col = cols[i % 4]
    with col:
      if st.button(f"{emoji} r/{subreddit}", key=f"quick_sub_{subreddit}_{i}"):
        # Add to current selection if not already there
        current_selection = st.session_state.get('selected_subreddits', default_subreddits)
        if subreddit not in current_selection:
          current_selection.append(subreddit)
          st.session_state.selected_subreddits = current_selection
          st.rerun()
  
  # Two-column layout for intro/tips
  st.markdown("---")
  st.markdown("""
  <div class="two-column" style="margin-bottom: 3rem;">
    <div>
      <h2 style="font-size: 36px; font-weight: 800; text-transform: uppercase; margin-bottom: 1rem;">
        Search <span style="color: #BCE5F7;">Tips</span>
      </h2>
      <p style="font-size: 20px; font-weight: 300; line-height: 1.6;">
        Get the most out of Reddit analysis with these search strategies.
      </p>
    </div>
    <div style="padding-left: 3rem;">
      <div class="numbered-list">
        <div style="display: flex; align-items: center; margin-bottom: 1.5rem; padding-bottom: 1.5rem; border-bottom: 1px solid #e0e0e0;">
          <span style="font-size: 44px; font-weight: 800; color: #BCE5F7; margin-right: 1.5rem;">01</span>
          <span style="font-size: 18px;">Use keywords + subreddits for targeted search</span>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 1.5rem; padding-bottom: 1.5rem; border-bottom: 1px solid #e0e0e0;">
          <span style="font-size: 44px; font-weight: 800; color: #BCE5F7; margin-right: 1.5rem;">02</span>
          <span style="font-size: 18px;">Click "Get Relevant Subreddits" for personalized suggestions</span>
        </div>
        <div style="display: flex; align-items: center;">
          <span style="font-size: 44px; font-weight: 800; color: #BCE5F7; margin-right: 1.5rem;">03</span>
          <span style="font-size: 18px;">Select multiple subreddits for broader content discovery</span>
        </div>
      </div>
    </div>
  </div>
  """, unsafe_allow_html=True)


elif platform == "Google Trends":
    # Hero-style header
    st.markdown("""
    <div style="margin-bottom: 4rem;">
        <h1 style="font-size: 64px; font-weight: 900; text-transform: uppercase; letter-spacing: -2px; margin-bottom: 1rem;">
            Google <span style="color: #BCE5F7;">Trends</span>
        </h1>
        <p style="font-size: 24px; font-weight: 300; color: #666; max-width: 800px;">
            Discover what's trending on Google Search and create content around viral topics.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get trending searches
    st.markdown("### Currently Trending on Google")
    
    if st.button("Get Trending Searches", key="get_trends", type="primary"):
        with st.spinner("Fetching Google Trends..."):            
            try:
                # Try different RSS feed URLs
                urls_to_try = [
                    "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US",
                    "https://trends.google.com/trending/rss?geo=US",
                    "https://trends.google.com/trends/hottrends/atom/feed?pn=p1",
                    "https://trends.google.com/trends/trendingsearches/realtime?geo=US&category=all"
                ]
                
                trends = []
                for url in urls_to_try:
                    try:
                        feed = feedparser.parse(url)
                        if feed.entries:
                            for entry in feed.entries[:20]:
                                trends.append({
                                    'title': entry.title,
                                    'traffic': entry.get('ht_approx_traffic', 'N/A'),
                                    'link': entry.get('link', '#'),
                                    'published': entry.get('published', 'N/A')
                                })
                            break
                    except:
                        continue
                
                if not trends:
                    # Fallback - show sample trending topics
                    st.warning("Could not fetch live trends. Showing sample trending topics.")
                    trends = [
                        {'title': 'Taylor Swift Eras Tour', 'traffic': '2M+ searches', 'link': '#', 'published': 'Today'},
                        {'title': 'iPhone 16 Release', 'traffic': '1M+ searches', 'link': '#', 'published': 'Today'},
                        {'title': 'Election Results 2024', 'traffic': '5M+ searches', 'link': '#', 'published': 'Today'},
                        {'title': 'ChatGPT Update', 'traffic': '500K+ searches', 'link': '#', 'published': 'Today'},
                        {'title': 'Super Bowl 2025', 'traffic': '3M+ searches', 'link': '#', 'published': 'Today'}
                    ]
                
                st.session_state.google_trends = trends
                st.success(f"✅ Found {len(trends)} trending searches")
                    
            except Exception as e:
                st.error(f"❌ Error fetching trends: {str(e)}")
                # Show sample data
                trends = [
                    {'title': 'Taylor Swift Eras Tour', 'traffic': '2M+ searches', 'link': '#', 'published': 'Today'},
                    {'title': 'iPhone 16 Release', 'traffic': '1M+ searches', 'link': '#', 'published': 'Today'},
                    {'title': 'Election Results 2024', 'traffic': '5M+ searches', 'link': '#', 'published': 'Today'},
                    {'title': 'ChatGPT Update', 'traffic': '500K+ searches', 'link': '#', 'published': 'Today'},
                    {'title': 'Super Bowl 2025', 'traffic': '3M+ searches', 'link': '#', 'published': 'Today'}
                ]
                st.session_state.google_trends = trends
                st.info("Showing sample trending topics for demonstration")

elif platform == "Saved Content":
  st.header("Saved Content")
  
  if not st.session_state.saved_posts:
    st.info("No saved posts yet. Analyze some Reddit content and save posts to get started!")
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
      with st.expander(f"{creator} ({len(posts)} posts)", expanded=True):
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

elif platform == "Show Planner":
  st.header("Show Planner")
  
  if not st.session_state.saved_posts:
    st.info("Save some Reddit posts first to create show concepts!")
  else:
    tab1, tab2 = st.tabs(["Create Show", "My Shows"])
    
    with tab1:
      st.subheader("Create New Show Concept")
      
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
        estimated_duration = len(selected_posts) * 8 # 8 minutes per segment
        st.info(f"Estimated Duration: {estimated_duration} minutes ({len(selected_posts)} segments)")
        
        if st.button("Create Show Concept", key="create_show_btn") and show_title:
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
        st.info("No show concepts yet. Create your first show!")
      else:
        for i, show in enumerate(st.session_state.show_concepts):
          with st.expander(f"{show['title']} ({show['duration']} min)", expanded=False):
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
                  label="Download Show Notes",
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

st.markdown("""
<div class="footer">
  <div class="brand">SHORTHAND STUDIOS</div>
  <div style="font-size: 18px; margin-bottom: 1rem;">Content Intelligence Platform</div>
  <div style="color: #999; font-size: 14px;">
    Transform trending conversations into compelling content
  </div>
</div>
""", unsafe_allow_html=True) 
