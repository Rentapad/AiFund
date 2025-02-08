import os
from typing import Dict, Any
from datetime import datetime
from .twitter_client import TwitterClient

class TwitterPublisher:
    def __init__(self):
        self.client = TwitterClient()
        
    async def format_daily_discussion(self, analysis_data: Dict[str, Any]) -> list[str]:
        """Formats the daily discussion into tweets."""
        tweets = []
        
        # Get the discussion from the analysis data
        discussion = analysis_data.get('daily_discussion') or analysis_data.get('discussion')
        if not discussion:
            return ["No daily discussion available for today."]
            
        # Add a header tweet with the date
        date_str = datetime.now().strftime("%Y-%m-%d")
        tweets.append(f"🤖 AI Agent Tokens Daily Discussion ({date_str}) 🗣️\n\nHighlights from today's analysis:")
            
        # Split the discussion into tweet-sized chunks (max 280 chars)
        current_chunk = ""
        
        for sentence in discussion.split('. '):
            # Clean up the sentence
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Check if adding this sentence would exceed tweet limit
            if len(current_chunk) + len(sentence) + 2 <= 280:  # +2 for ". "
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    tweets.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        # Add any remaining text as the last tweet
        if current_chunk:
            tweets.append(current_chunk.strip())
            
        return tweets

    async def publish_daily_analysis(self, analysis_data: Dict[str, Any]):
        """Publishes the daily discussion as tweets."""
        try:
            # Get Twitter credentials from environment variables
            username = os.getenv("TWITTER_USERNAME")
            email = os.getenv("TWITTER_EMAIL")
            password = os.getenv("TWITTER_PASSWORD")
            
            if not all([username, email, password]):
                raise ValueError("Missing required Twitter credentials")
            
            # Login to Twitter
            await self.client.ensure_login(username, email, password)
            
            # Format the tweets from the daily discussion
            tweets = await self.format_daily_discussion(analysis_data)
            
            # Publish the thread
            thread_tweets = await self.client.publish_thread(tweets)
            
            # Logout
            await self.client.logout()
            
            return {
                "status": "success",
                "tweet_count": len(tweets)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            } 