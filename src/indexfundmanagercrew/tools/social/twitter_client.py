from twikit import Client
import json
import os
from typing import List

class TwitterClient:
    def __init__(self):
        self.client = Client(language='en-US')
        self.cookies_file = 'twitter_cookies.json'
        
    async def ensure_login(self, username: str, email: str, password: str):
        """Ensures the client is logged in, using cookies if available."""
        try:
            if os.path.exists(self.cookies_file):
                self.client.load_cookies(self.cookies_file)
            else:
                await self.client.login(
                    auth_info_1=username,
                    auth_info_2=email,
                    password=password,
                )
                self.client.save_cookies(self.cookies_file)
        except Exception as e:
            raise Exception(f"Failed to login to Twitter: {str(e)}")

    async def publish_thread(self, tweets: List[str]):
        """Publishes a thread of tweets."""
        try:
            previous_tweet_id = None
            thread_tweets = []
            
            for tweet_text in tweets:
                tweet = await self.client.create_tweet(
                    text=tweet_text,
                    reply_to=previous_tweet_id if previous_tweet_id else None
                )
                previous_tweet_id = tweet.id
                thread_tweets.append(tweet)
                
            return thread_tweets
            
        except Exception as e:
            raise Exception(f"Failed to publish Twitter thread: {str(e)}")

    async def logout(self):
        """Logs out the current session."""
        try:
            await self.client.logout()
        except Exception as e:
            raise Exception(f"Failed to logout from Twitter: {str(e)}") 