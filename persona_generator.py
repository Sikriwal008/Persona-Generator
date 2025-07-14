# Import necessary libraries
import praw
import re
import os
from collections import Counter


# This section holds the API credentials required to connect to Reddit.
CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID", "YOUR_CLIENT_ID_HERE")
CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET", "YOUR_SECRET_HERE")
USER_AGENT = "UserPersonaScript/0.2 by YourUsername"


# This section defines keywords and patterns to infer user information.
DEMOGRAPHIC_PATTERNS = {
    "age": r"\b(i'm|i am|being)\s+(\d{1,2})\s+(years old|yo|old)\b",
    "occupation": r"\b(i'm|i am|my job is|i work as|working as)\s+(a|an)\s+([\w\s]+?)(?=\.|\s+and|\s+but|,|\s+in)",
    "location": r"\b(i live in|living in|from)\s+([\w\s,]+?)(?=\.|\s+and|\s+but|,|\s+so)",
    "status": r"\b(my\s+(wife|husband|partner|girlfriend|boyfriend))\b" # Detects mentions of a partner
}
SINGLE_STATUS_KEYWORDS = ["i'm single", "i am single", "being single"]

# Keywords to infer personality traits from text.
PERSONALITY_KEYWORDS = {
    "Analytical": ['data', 'logic', 'analyze', 'research', 'think', 'science', 'conclusion', 'evidence'],
    "Creative": ['art', 'music', 'drawing', 'design', 'writing', 'creative', 'imagine', 'build'],
    "Helpful": ['help', 'advice', 'suggest', 'you should', 'try this', 'the solution is'],
    "Expressive": ['i feel', 'my opinion', 'personally', 'passionate', 'i love', 'i hate']
}

# Subreddit topics to infer user motivations.
MOTIVATION_SUBREDDITS = {
    "Wellness & Health": ['fitness', 'loseit', 'health', 'mentalhealth', 'meditation', 'selfimprovement'],
    "Financial Growth": ['personalfinance', 'investing', 'stocks', 'fire', 'financialindependence', 'frugal'],
    "Career & Learning": ['cscareerquestions', 'learnpython', 'programming', 'datascience', 'askengineers', 'college'],
    "Entertainment & Hobbies": ['gaming', 'movies', 'books', 'music', 'hobbies', 'dnd', 'boardgames'],
    "Social & Community": ['askreddit', 'relationships', 'socialskills', 'discussion']
}

#Initializes and returns a read-only Reddit instance using PRAW.
def initialize_reddit():
    if CLIENT_ID == "YOUR_CLIENT_ID_HERE" or CLIENT_SECRET == "YOUR_SECRET_HERE":
        raise ValueError("Reddit API credentials are not set. Please edit the script and add your credentials.")
    return praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT)

#Analyzes a single piece of text to find and extract persona details.
def analyze_text(text, persona):
    text_lower = text.lower()
    
    # 1. Analyze for Demographics
    for key, pattern in DEMOGRAPHIC_PATTERNS.items():
        if re.search(pattern, text_lower) and persona['demographics'][key]['value'] == 'Unknown':
            if key == 'status':
                persona['demographics']['status']['value'] = 'In a relationship'
            else:
                match = re.search(pattern, text_lower)
                persona['demographics'][key]['value'] = match.group(2).strip()
    for keyword in SINGLE_STATUS_KEYWORDS:
        if keyword in text_lower:
            persona['demographics']['status']['value'] = 'Single'
            break

    # 2. Analyze for Personality Traits
    for trait, keywords in PERSONALITY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                persona['personality_traits'].add(trait) 

    # 3. Analyze for Frustrations and Goals
    for keyword in ['frustrated', 'annoying', 'hate', 'disappointed', 'issue', 'problem']:
        if keyword in text_lower:
            persona['frustrations'].add(text)
            break
    for keyword in ['goal', 'aim', 'achieve', 'learn', 'improve', 'start', 'need to', 'how to']:
        if keyword in text_lower:
            persona['goals_and_needs'].add(text)
            break

#Builds a user persona by scraping and analyzing a user's Reddit history.
def build_persona(reddit, username):
    
    try:
        redditor = reddit.redditor(username)
        _ = redditor.id
    except Exception:
        print(f"Error: User '{username}' not found or is suspended.")
        return None

    # Expanded persona structure with new fields and using sets for unique entries
    persona = {
        "username": redditor.name,
        "demographics": {
            "age": {"value": "Unknown"},
            "occupation": {"value": "Unknown"},
            "location": {"value": "Unknown"},
            "status": {"value": "Unknown"}
        },
        "motivations": set(),
        "personality_traits": set(),
        "behaviour_and_habits": [],
        "frustrations": set(),
        "goals_and_needs": set()
    }
    
    print(f"Analyzing user: {username}. This may take a moment...")
    
    all_subreddits = []
    # Analyze last 100 comments and submissions
    for item in list(redditor.comments.new(limit=50)) + list(redditor.submissions.new(limit=50)):
        text_to_analyze = ""
        if hasattr(item, 'body'):
            text_to_analyze = item.body
        else:
            text_to_analyze = f"{item.title}. {item.selftext}"
        
        analyze_text(text_to_analyze, persona)
        all_subreddits.append(item.subreddit.display_name.lower())

    # 1. Aggregate Habits from most active subreddits
    if all_subreddits:
        top_subreddits = [sub[0] for sub in Counter(all_subreddits).most_common(5)]
        persona['behaviour_and_habits'].append(
            f"Frequently posts or comments in communities like: {', '.join(top_subreddits)}"
        )
    
    # 2. Infer Motivations from subreddit activity
    for motivation, sub_keywords in MOTIVATION_SUBREDDITS.items():
        for sub in top_subreddits:
            if any(keyword in sub for keyword in sub_keywords):
                persona['motivations'].add(motivation)
                break

    print("Analysis complete.")
    return persona

#Formats the persona dictionary into a clean, readable text file.
def format_persona_to_file(persona, filename):

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"USER PERSONA: u/{persona['username']}\n")
        f.write("="*40 + "\n\n")

        # Demographics
        f.write("## DEMOGRAPHICS (Inferred)\n")
        f.write(f"- **Age:** {persona['demographics']['age']['value']}\n")
        f.write(f"- **Location:** {persona['demographics']['location']['value']}\n")
        f.write(f"- **Occupation:** {persona['demographics']['occupation']['value']}\n")
        f.write(f"- **Status:** {persona['demographics']['status']['value']}\n")
        f.write("\n")
        
        # Motivations
        f.write("## MOTIVATIONS (Inferred from activity)\n")
        if persona['motivations']:
            for item in persona['motivations']:
                f.write(f"- {item}\n")
        else:
            f.write("- Motivations not clearly identified from recent activity.\n")
        f.write("\n")
        
        # Personality
        f.write("## PERSONALITY TRAITS (Inferred from language)\n")
        if persona['personality_traits']:
            f.write(f"- Appears to be: {', '.join(persona['personality_traits'])}\n")
        else:
            f.write("- Personality traits not clearly identified from recent activity.\n")
        f.write("\n")

        # Behaviour and Habits
        f.write("## BEHAVIOUR & HABITS\n")
        if persona['behaviour_and_habits']:
            for habit in persona['behaviour_and_habits']:
                f.write(f"- {habit}\n")
        else:
            f.write("- No specific habits identified.\n")
        f.write("\n")

        # Goals and Needs
        f.write("## GOALS & NEEDS (Inferred)\n")
        if persona['goals_and_needs']:
            for item in list(persona['goals_and_needs'])[:3]: # Show up to 3 examples
                f.write(f" \"{item[:100]}...\"\n")
        else:
            f.write("- No specific goals identified from recent activity.\n")
        f.write("\n")

        # Frustrations / Pain Points
        f.write("## FRUSTRATIONS\n")
        if persona['frustrations']:
            for item in list(persona['frustrations'])[:3]: # Show up to 3 examples
                f.write(f" \"{item[:100]}...\"\n")
        else:
            f.write("- No specific frustrations identified from recent activity.\n")
        f.write("\n")
    
    print(f"Clean persona file created: {filename}")

if __name__ == "__main__":
    reddit_url = input("Enter the Reddit user's profile URL: ")
    match = re.search(r"user/([\w-]+)", reddit_url)
    if not match:
        print("Invalid Reddit user profile URL. URL must be in the format: https://www.reddit.com/user/username/")
    else:
        username = match.group(1)
        try:
            reddit_instance = initialize_reddit()
            user_persona = build_persona(reddit_instance, username)
            if user_persona:
                output_filename = f"persona_{username}.txt"
                format_persona_to_file(user_persona, output_filename)
        except ValueError as e:
            print(f"Configuration Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")