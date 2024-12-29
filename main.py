from playwright.sync_api import sync_playwright

# Target account username
target_account = "elonmusk"  # Replace with the actual username
base_url = f"https://twitter.com/{target_account}"

def get_latest_tweet():
    """
    Extract the latest tweet text from a user's profile using Playwright.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)  # Set to False to see the browser
            page = browser.new_page()
            page.goto(base_url)

            # Wait for the tweets container to load
            page.wait_for_selector("article[role='article']", timeout=15000)

            # Select the first tweet (article element)
            tweet_element = page.query_selector("article[role='article']")
            if tweet_element:
                # Extract the text of the tweet
                tweet_text = tweet_element.inner_text()
                print(f"Latest Tweet:\n{tweet_text}")
            else:
                print("No tweet found!")

            browser.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_latest_tweet()