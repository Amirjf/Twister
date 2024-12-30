from openai import OpenAI
import base64
import os

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

MAX_TWEET_LENGTH = 280

def validate_tweet(tweet_text):
    """Validate tweet length and content."""
    if not tweet_text:
        return False
    if len(tweet_text) > MAX_TWEET_LENGTH:
        return False
    return True


def encode_image_to_base64(image_path):
    """Convert image to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')



def truncate_tweet(tweet_text):
    """Ensure tweet is within character limit."""
    if len(tweet_text) > MAX_TWEET_LENGTH:
        return tweet_text[:MAX_TWEET_LENGTH-3] + "..."
    return tweet_text

def refactor_tweet(original_tweet):
    """Get AI response for a tweet."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """You are a witty social media expert. CRITICAL: All responses must be under 280 characters TOTAL.
                    Create engaging responses that:
                    1. Never exceed 280 characters
                    2. Use natural, conversational language
                    3. Include emojis sparingly
                    4. Reference both the image and tweet text
                    5. Add brief interesting facts when relevant"""
                },
                {
                    "role": "user",
                    "content": f"Create a response to: {original_tweet}"
                }
            ],
            max_tokens=200
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return None


def analyze_image_and_tweet(image_path, original_tweet):
    """Analyze image using OpenAI Vision API and generate a character-limited response."""
    try:
        base64_image = encode_image_to_base64(image_path)
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """You are a witty social media expert. CRITICAL: All responses must be under 280 characters TOTAL.
                    Create engaging responses that:
                    1. Never exceed 280 characters
                    2. Use natural, conversational language
                    3. Include emojis sparingly
                    4. Reference both the image and tweet text
                    5. Add brief interesting facts when relevant"""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Create a response (max 280 chars) to this tweet and image: {original_tweet}"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000  # Reduced to help ensure shorter responses
        )
        
        response_text = response.choices[0].message.content
        return truncate_tweet(response_text)
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return None

def validate_tweet(tweet_text):
    """Validate tweet length and content."""
    if not tweet_text:
        return False
    if len(tweet_text) > MAX_TWEET_LENGTH:
        return False
    return True


