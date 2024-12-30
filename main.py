from playwright.sync_api import sync_playwright
from openai_utils import refactor_tweet
from utils import clean_tweet
import time
import os

TWITTER_USERNAME = os.environ.get("TWITTER_USERNAME")
TWITTER_PASSWORD = os.environ.get("TWITTER_PASSWORD")
MAX_STORED_TWEETS = 20

# Store both original and AI-generated responses
tweet_queue = []


def collect_tweets(page):
    """Just collect tweets and their AI responses."""
    global tweet_queue
    
    try:
        page.goto("https://twitter.com/home")
        page.wait_for_selector("article[role='article']")
        tweets = page.query_selector_all("article[role='article']")

        for tweet in tweets:
            try:
                tweet_text = tweet.inner_text().strip()
                cleaned_tweet = clean_tweet(tweet_text)
                
                # Skip if we already have this tweet
                if any(item['original'] == cleaned_tweet for item in tweet_queue):
                    continue
                
                print(f"Processing tweet: {cleaned_tweet[:50]}...")
                ai_response = refactor_tweet(cleaned_tweet)
                
                if ai_response:
                    tweet_queue.append({
                        'original': cleaned_tweet,
                        'response': ai_response
                    })
                    print(f"Stored AI response: {ai_response[:50]}...")
                
                # If we have enough tweets, stop collecting
                if len(tweet_queue) >= MAX_STORED_TWEETS:
                    print(f"Reached {MAX_STORED_TWEETS} stored tweets. Stopping collection.")
                    break
                    
            except Exception as e:
                print(f"Error processing tweet: {e}")
                continue
                
    except Exception as e:
        print(f"Error collecting tweets: {e}")

def post_stored_tweets(page):
    """Post all stored tweets."""
    global tweet_queue
    
    print(f"Starting to post {len(tweet_queue)} stored tweets...")
    
    while tweet_queue:
        tweet_data = tweet_queue.pop(0)  # Get and remove first item
        try:
            print(f"Posting response: {tweet_data['response'][:50]}...")
            
            page.goto("https://twitter.com/home")
            page.wait_for_selector("div[data-testid='tweetTextarea_0']")
            page.fill("div[data-testid='tweetTextarea_0']", tweet_data['response'])
            
            post_button = page.locator("button[data-testid='tweetButtonInline']")
            post_button.click()
            
            print("Tweet posted successfully!")
            time.sleep(3)  # Wait between posts
            
        except Exception as e:
            print(f"Error posting tweet: {e}")
            # Put the tweet back in queue if posting failed
            tweet_queue.append(tweet_data)
            time.sleep(5)  # Wait longer after an error
            continue

if __name__ == "__main__":
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Login first
        try:
            page.goto("https://x.com/i/flow/login")
            page.wait_for_selector("input[name='text']")
            page.fill("input[name='text']", TWITTER_USERNAME)
            page.locator("button:has-text('Next')").click()
            page.wait_for_selector("input[name='password']")
            page.fill("input[name='password']", TWITTER_PASSWORD)
            page.locator("button:has-text('Log in')").click()
            page.wait_for_selector("article[role='article']")
            print("Logged in successfully!")

            while True:
                try:
                    # First phase: Collect tweets until we have 20
                    while len(tweet_queue) < MAX_STORED_TWEETS:
                        print(f"Collecting tweets... Currently have {len(tweet_queue)}")
                        collect_tweets(page)
                        time.sleep(10)  # Wait between collection attempts
                    
                    # Second phase: Post all stored tweets
                    print("Starting to post stored tweets...")
                    post_stored_tweets(page)
                    
                except Exception as e:
                    print(f"Error in main loop: {e}")
                    time.sleep(30)  # Wait longer after an error
                    continue

        except KeyboardInterrupt:
            print("Stopping the script...")
        finally:
            browser.close()