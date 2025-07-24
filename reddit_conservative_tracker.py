import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
import re

# Configure Streamlit page
st.set_page_config(
    page_title="Reddit Conservative Sentiment Tracker",
    page_icon="🗳️",
    layout="wide"
)

# Reddit API headers
HEADERS = {
    'User-Agent': 'Conservative-Sentiment-Tracker/1.0 (Daily Wire Content Analysis Tool)'
}

def get_reddit_posts(subreddit="Conservative", limit=10, time_filter="day"):
    """Get top posts from r/Conservative"""
    url = f"https://www.reddit.com/r/{subreddit}/top.json"
    params = {
        'limit': limit,
        't': time_filter  # day, week, month, year, all
    }
    
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'children' in data['data']:
                return data['data']['children']
        return []
    except Exception as e:
        st.error(f"Error fetching posts: {e}")
        return []

def get_post_comments(post_id, subreddit="Conservative", limit=5):
    """Get top comments for a specific post"""
    url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json"
    params = {'limit': limit}
    
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1 and 'data' in data[1] and 'children' in data[1]['data']:
                comments = []
                for comment in data[1]['data']['children'][:limit]:
                    if comment['kind'] == 't1':  # Comment type
                        comment_data = comment['data']
                        if 'body' in comment_data and comment_data['body'] != '[deleted]':
                            comments.append({
                                'body': comment_data['body'],
                                'score': comment_data.get('score', 0),
                                'author': comment_data.get('author', 'Unknown'),
                                'created_utc': comment_data.get('created_utc', 0)
                            })
                return comments
        return []
    except Exception as e:
        st.error(f"Error fetching comments for post {post_id}: {e}")
        return []

def analyze_topic_sentiment(post_title, comments, post_topics):
    """Generate specific insights about how conservatives feel about topics"""
    
    # Combine all text for analysis
    all_text = post_title + " " + " ".join([c['body'] for c in comments])
    text_lower = all_text.lower()
    
    insights = []
    
    # Topic-specific sentiment analysis
    for topic in post_topics:
        topic_insights = []
        
        if topic == "Immigration/Border":
            if any(word in text_lower for word in ['frustrated', 'angry', 'fed up', 'enough']):
                if 'border' in text_lower:
                    topic_insights.append("Conservatives are frustrated with current border security")
                if 'deportation' in text_lower:
                    topic_insights.append("Conservatives want more aggressive deportation policies")
            if any(word in text_lower for word in ['finally', 'about time', 'good']):
                topic_insights.append("Conservatives are pleased with recent immigration actions")
        
        elif topic == "Economy":
            if any(word in text_lower for word in ['inflation', 'gas prices', 'expensive']):
                if any(word in text_lower for word in ['blame', 'fault', 'caused']):
                    topic_insights.append("Conservatives blame current administration for economic problems")
                else:
                    topic_insights.append("Conservatives are concerned about inflation and cost of living")
            if 'jobs' in text_lower and any(word in text_lower for word in ['good', 'great', 'better']):
                topic_insights.append("Conservatives are optimistic about job market improvements")
        
        elif topic == "Culture War":
            if any(word in text_lower for word in ['woke', 'transgender', 'pronouns']):
                if any(word in text_lower for word in ['tired', 'sick', 'enough', 'stop']):
                    topic_insights.append("Conservatives are exhausted by woke ideology push")
                if any(word in text_lower for word in ['fight back', 'resist', 'stand up']):
                    topic_insights.append("Conservatives want to actively fight back against woke policies")
            if 'schools' in text_lower or 'education' in text_lower:
                topic_insights.append("Conservatives are concerned about liberal indoctrination in schools")
        
        elif topic == "Elections":
            if any(word in text_lower for word in ['fraud', 'rigged', 'stolen']):
                topic_insights.append("Conservatives remain skeptical about election integrity")
            if any(word in text_lower for word in ['audit', 'investigate', 'prove']):
                topic_insights.append("Conservatives want thorough election investigations")
        
        elif topic == "Foreign Policy":
            if 'ukraine' in text_lower:
                if any(word in text_lower for word in ['enough', 'stop', 'waste']):
                    topic_insights.append("Conservatives are tired of Ukraine funding")
                elif any(word in text_lower for word in ['support', 'help', 'defend']):
                    topic_insights.append("Conservatives support helping Ukraine defend itself")
            if 'china' in text_lower:
                if any(word in text_lower for word in ['threat', 'danger', 'enemy']):
                    topic_insights.append("Conservatives view China as a major threat")
        
        elif topic == "Media/Tech":
            if any(word in text_lower for word in ['censorship', 'banned', 'silenced']):
                topic_insights.append("Conservatives are angry about Big Tech censorship")
            if 'media' in text_lower and any(word in text_lower for word in ['lies', 'fake', 'propaganda']):
                topic_insights.append("Conservatives distrust mainstream media reporting")
        
        elif topic == "Deep State":
            if any(word in text_lower for word in ['fbi', 'doj', 'corrupt']):
                topic_insights.append("Conservatives believe federal agencies are weaponized")
            if any(word in text_lower for word in ['expose', 'investigate', 'clean house']):
                topic_insights.append("Conservatives want accountability for federal agencies")
        
        # Add specific Trump-related insights
        if 'trump' in text_lower:
            if any(word in text_lower for word in ['disappointed', 'frustrated', 'wrong']):
                if 'epstein' in text_lower:
                    topic_insights.append("Conservatives are frustrated that Trump won't release Epstein files")
                elif 'vaccine' in text_lower:
                    topic_insights.append("Conservatives are disappointed in Trump's vaccine stance")
                else:
                    topic_insights.append("Conservatives have concerns about some Trump decisions")
            elif any(word in text_lower for word in ['support', 'defend', 'based', 'right']):
                topic_insights.append("Conservatives strongly support Trump's position")
        
        if topic_insights:
            insights.extend(topic_insights)
    
    # General sentiment patterns
    if any(word in text_lower for word in ['hopeful', 'optimistic', 'winning', 'finally']):
        insights.append("Conservatives are feeling optimistic about recent developments")
    elif any(word in text_lower for word in ['tired', 'exhausted', 'fed up', 'had enough']):
        insights.append("Conservatives are feeling frustrated and want action")
    elif any(word in text_lower for word in ['worried', 'concerned', 'scared', 'dangerous']):
        insights.append("Conservatives are concerned about current trajectory")
    
    return insights[:3]  # Return top 3 most relevant insights

def extract_topics(text):
    """Extract key political topics mentioned"""
    text_lower = text.lower()
    
    topics = {
        'Immigration/Border': ['border', 'immigration', 'illegal', 'deportation', 'wall', 'migrant'],
        'Elections': ['election', 'voting', 'ballot', 'fraud', 'rigged', 'steal', 'dominion'],
        'Economy': ['economy', 'inflation', 'gas prices', 'jobs', 'unemployment', 'recession'],
        'Foreign Policy': ['ukraine', 'china', 'russia', 'israel', 'iran', 'foreign', 'war'],
        'Culture War': ['woke', 'transgender', 'pronouns', 'crt', 'dei', 'pronouns', 'gender'],
        'Media/Tech': ['media', 'censorship', 'facebook', 'twitter', 'google', 'big tech'],
        'COVID/Health': ['covid', 'vaccine', 'mandate', 'lockdown', 'fauci', 'pandemic'],
        'Second Amendment': ['gun', 'second amendment', '2a', 'firearms', 'shooting'],
        'Education': ['school', 'education', 'teachers', 'parents', 'curriculum', 'college'],
        'Deep State': ['deep state', 'fbi', 'cia', 'doj', 'corrupt', 'establishment']
    }
    
    found_topics = []
    for topic, keywords in topics.items():
        if any(keyword in text_lower for keyword in keywords):
            found_topics.append(topic)
    
    return found_topics

# Streamlit UI
st.title("🗳️ Reddit Conservative Sentiment Tracker")
st.markdown("*Analyzing r/Conservative to understand grassroots conservative sentiment*")

# Sidebar controls
st.sidebar.header("Analysis Settings")
time_filter = st.sidebar.selectbox(
    "Time Period",
    options=['day', 'week', 'month'],
    format_func=lambda x: {'day': 'Today', 'week': 'This Week', 'month': 'This Month'}[x]
)

num_posts = st.sidebar.slider("Number of posts to analyze", 5, 25, 10)
num_comments = st.sidebar.slider("Comments per post", 3, 10, 5)

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()

# Main analysis
if st.button("📊 Analyze r/Conservative") or 'reddit_data' not in st.session_state:
    
    st.info(f"Analyzing top {num_posts} posts from r/Conservative...")
    
    # Get posts
    posts = get_reddit_posts("Conservative", num_posts, time_filter)
    
    if not posts:
        st.error("Could not fetch posts. Reddit may be experiencing issues.")
        st.stop()
    
    analysis_results = []
    progress_bar = st.progress(0)
    
    for i, post in enumerate(posts):
        post_data = post['data']
        post_id = post_data['id']
        
        st.text(f"Analyzing: {post_data['title'][:50]}...")
        
        # Get comments for this post
        comments = get_post_comments(post_id, "Conservative", num_comments)
        
        # Analyze sentiment and topics
        post_topics = extract_topics(post_data['title'] + " " + post_data.get('selftext', ''))
        
        # Get specific insights about how conservatives feel
        topic_insights = analyze_topic_sentiment(post_data['title'], comments, post_topics)
        
        analysis_results.append({
            'title': post_data['title'],
            'score': post_data['score'],
            'num_comments': post_data['num_comments'],
            'url': f"https://reddit.com{post_data['permalink']}",
            'post_topics': post_topics,
            'topic_insights': topic_insights,
            'comments': comments,
            'created_utc': post_data['created_utc']
        })
        
        progress_bar.progress((i + 1) / len(posts))
        time.sleep(1)  # Be respectful to Reddit's servers
    
    progress_bar.empty()
    st.session_state['reddit_data'] = analysis_results
    st.success(f"✅ Analysis complete! Analyzed {len(analysis_results)} posts and {sum(len(r['comments']) for r in analysis_results)} comments.")

# Display results
if 'reddit_data' in st.session_state and st.session_state['reddit_data']:
    data = st.session_state['reddit_data']
    
    # Overall insights analysis
    st.header("🎯 Conservative Base Insights")
    
    # Collect all insights
    all_insights = []
    for post in data:
        all_insights.extend(post['topic_insights'])
    
    # Group similar insights
    insight_counts = {}
    for insight in all_insights:
        # Group similar insights together
        key = insight.split()[:6]  # First 6 words as grouping key
        key_str = " ".join(key)
        if key_str in insight_counts:
            insight_counts[key_str] += 1
        else:
            insight_counts[key_str] = 1
    
    # Show top insights
    st.write("**Key Conservative Sentiment Patterns:**")
    sorted_insights = sorted(insight_counts.items(), key=lambda x: x[1], reverse=True)
    
    for insight, count in sorted_insights[:8]:
        # Find the full insight text
        full_insight = next((i for i in all_insights if i.startswith(insight)), insight)
        if count > 1:
            st.write(f"🔸 **{full_insight}** *(mentioned {count} times)*")
        else:
            st.write(f"🔸 {full_insight}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top topics
        all_topics = []
        for post in data:
            all_topics.extend(post['post_topics'])
        
        topic_counts = pd.Series(all_topics).value_counts().head(5)
        st.write("**Most Discussed Topics:**")
        for topic, count in topic_counts.items():
            st.write(f"• {topic}: {count} posts")
    
    with col2:
        # Engagement metrics
        total_upvotes = sum(post['score'] for post in data)
        total_comments = sum(post['num_comments'] for post in data)
        avg_score = total_upvotes / len(data)
        
        st.metric("Total Upvotes", f"{total_upvotes:,}")
        st.metric("Total Comments", f"{total_comments:,}")
        st.metric("Avg Post Score", f"{avg_score:.0f}")
    
    # Detailed post analysis
    st.header("🔍 Post-by-Post Analysis")
    
    for i, post in enumerate(data):
        with st.expander(f"#{i+1}: {post['title'][:80]}..." if len(post['title']) > 80 else f"#{i+1}: {post['title']}"):
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Score:** {post['score']} upvotes | **Comments:** {post['num_comments']}")
                if post['post_topics']:
                    st.write(f"**Topics:** {', '.join(post['post_topics'])}")
                
                # Show specific insights about conservative sentiment
                if post['topic_insights']:
                    st.write("**Conservative Sentiment:**")
                    for insight in post['topic_insights']:
                        st.write(f"• {insight}")
                
                st.write(f"[View on Reddit]({post['url']})")
                
                # Top comments
                st.write("**Top Comments:**")
                for j, comment in enumerate(post['comments'][:3]):
                    st.write(f"*Comment {j+1} - Score: {comment['score']}*")
                    st.write(f"> {comment['body'][:200]}..." if len(comment['body']) > 200 else f"> {comment['body']}")
                    st.write("")
            
            with col2:
                # Show comment scores and engagement
                if post['comments']:
                    comment_scores = [c['score'] for c in post['comments']]
                    avg_comment_score = sum(comment_scores) / len(comment_scores)
                    st.write("**Comment Engagement:**")
                    st.write(f"• Avg comment score: {avg_comment_score:.1f}")
                    st.write(f"• Top comment: {max(comment_scores)} points")
                    st.write(f"• Total comments analyzed: {len(post['comments'])}")
    
    # Daily Wire content recommendations
    st.header("💡 Daily Wire Content Recommendations")
    
    # Analyze insights for content recommendations
    st.write("**Based on conservative grassroots sentiment:**")
    
    # Group insights by topic for recommendations
    topic_mentions = {}
    for post in data:
        for topic in post['post_topics']:
            if topic not in topic_mentions:
                topic_mentions[topic] = []
            topic_mentions[topic].extend(post['topic_insights'])
    
    recommendations = []
    
    # Generate specific recommendations based on insights
    for topic, insights in topic_mentions.items():
        if not insights:
            continue
            
        insight_text = " ".join(insights).lower()
        
        if topic == "Immigration/Border":
            if "frustrated" in insight_text:
                recommendations.append("🔥 **URGENT**: Conservative base frustrated with border - cover latest border crisis developments and demand action")
            elif "pleased" in insight_text:
                recommendations.append("✅ **POSITIVE**: Conservatives pleased with immigration actions - highlight wins and progress")
        
        elif topic == "Culture War":
            if "exhausted" in insight_text or "tired" in insight_text:
                recommendations.append("🎯 **RED MEAT**: Base exhausted by woke ideology - cover pushback stories and victories against woke policies")
            if "fight back" in insight_text:
                recommendations.append("⚔️ **CALL TO ACTION**: Conservatives want to fight back - provide actionable steps and local organizing")
        
        elif topic == "Economy":
            if "blame" in insight_text:
                recommendations.append("💰 **ECONOMIC**: Conservatives blame administration for economic problems - tie current policies to kitchen table issues")
        
        elif topic == "Deep State":
            if "weaponized" in insight_text:
                recommendations.append("🔍 **ACCOUNTABILITY**: Conservatives believe agencies are weaponized - cover federal overreach and demand investigations")
    
    # Trump-specific recommendations
    trump_insights = [insight for post in data for insight in post['topic_insights'] if 'trump' in insight.lower()]
    if trump_insights:
        trump_text = " ".join(trump_insights).lower()
        if "frustrated" in trump_text and "epstein" in trump_text:
            recommendations.append("📋 **TRUMP ALERT**: Base frustrated Trump won't release Epstein files - address directly or explain strategy")
        elif "disappointed" in trump_text:
            recommendations.append("🤔 **TRUMP CONCERN**: Some conservative disappointment with Trump decisions - provide context or pushback")
    
    if not recommendations:
        recommendations.append("📊 Standard conservative content performing well - continue current editorial direction")
    
    for rec in recommendations:
        st.write(rec)
    
    # Show most mentioned insights for additional context
    if all_insights:
        st.write("\n**Most Common Conservative Concerns:**")
        for insight, count in sorted_insights[:3]:
            full_insight = next((i for i in all_insights if i.startswith(insight)), insight)
            st.write(f"• {full_insight}")

    # Trending warning system
    frustrated_count = sum(1 for insight in all_insights if 'frustrated' in insight.lower() or 'tired' in insight.lower())
    if frustrated_count >= 3:
        st.warning("⚠️ **BASE MOOD ALERT**: High frustration levels detected - consider more aggressive/action-oriented content")
    
    optimistic_count = sum(1 for insight in all_insights if 'optimistic' in insight.lower() or 'pleased' in insight.lower())
    if optimistic_count >= 3:
        st.success("🌟 **POSITIVE MOMENTUM**: Base feeling optimistic - good time for victory laps and positive messaging")

else:
    st.info("👆 Click 'Analyze r/Conservative' to start tracking conservative sentiment")

# Footer
st.markdown("---")
st.markdown("*Data from Reddit r/Conservative subreddit*")
st.markdown("*This tool helps Daily Wire understand grassroots conservative sentiment for content planning*")
st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")