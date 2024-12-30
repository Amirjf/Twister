import re
import time

def clean_tweet(tweet_text):
    """
    Clean up the tweet by removing timestamps, stray punctuation, and line breaks.
    """
    tweet_text = re.sub(r'\b\w{3,9} \d{1,2}\b', '', tweet_text)  # Remove dates
    tweet_text = re.sub(r'^\.\s*|\s*\.\s*$', '', tweet_text.strip())  # Remove stray punctuation
    tweet_text = re.sub(r'\s+', ' ', tweet_text)  # Collapse multiple spaces
    return tweet_text.strip()

def take_screenshot(page, tweet_element):
    """Take screenshot with improved error handling."""
    try:
        # Ensure element is visible in viewport
        page.evaluate('element => element.scrollIntoView()', tweet_element)
        page.wait_for_timeout(1000)  # Wait for any animations
        
        screenshot_path = f"tweet_screenshot_{int(time.time())}.png"
        tweet_element.screenshot(path=screenshot_path)
        return screenshot_path
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return None