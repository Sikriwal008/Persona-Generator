# Reddit User Persona Builder

A Python-based tool that analyzes a Reddit user’s recent activity to automatically generate a concise, human‑readable “persona” report. Perfect for HR, marketing, UX researchers, or any team that wants to understand an individual’s background, interests, motivations, and communication style without manual review of dozens of posts.

---

## 📋 At a Glance

- **Purpose:** Transform a user’s public Reddit comments and submissions into an easy‑to‑digest persona summary.
- **Who It’s For:**  
  - **HR & Recruiting:** Quickly gauge a candidate’s interests, background hints, and communication style.  
  - **Marketing & UX Teams:** Understand target audiences by example.  
  - **Community Managers:** Spot key motivations or pain points in user conversations.  
- **Outcome:** A text file named `persona_<username>.txt` with clear sections on demographics, personality, motivations, habits, goals, and frustrations.

---

## 🎯 Business Value

1. **Saves Time & Effort**  
   - No more manual reading of 100+ posts to form an impression.  
   - Automates extraction of age hints, job clues, location mentions, and more.

2. **Data‑Driven Insights**  
   - Applies regex patterns and keyword analysis to identify key traits.  
   - Categorizes motivations (e.g. “Wellness & Health” vs. “Career & Learning”).

3. **Consistent Reporting**  
   - Every persona follows the same format—easy to compare and share.  
   - Standardized sections make it straightforward to scan for relevant details.

---

## 🔍 High‑Level Architecture

1. **Reddit Connection**  
   - Uses PRAW (Python Reddit API Wrapper) with your unique credentials.  
   - Fetches a user’s 50 most recent comments + 50 submissions.

2. **Text Analysis**  
   - **Demographics:** Regular expressions detect phrases like “I’m 25 years old” or “I work as a teacher.”  
   - **Personality:** Keyword matching for traits (analytical, creative, helpful, expressive).  
   - **Motivations:** Maps subreddit names to broader themes (e.g. r/fitness → “Wellness & Health”).  
   - **Goals & Frustrations:** Captures sentences that mention “goal,” “problem,” “frustrated,” etc.

3. **Report Generation**  
   - Compiles findings into clearly labeled sections:  
     - Demographics  
     - Motivations  
     - Personality Traits  
     - Behaviour & Habits  
     - Goals & Needs  
     - Frustrations  
   - Outputs a neatly formatted `.txt` file for easy sharing.

---

## 🚀 Quick Start

1. **Obtain Reddit API Credentials**  
   - Log in to Reddit and create a “script” app at [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps).  
   - Copy your Client ID & Secret.

2. **Set Environment Variables**  
   ```bash
   export REDDIT_CLIENT_ID="your_client_id"
   export REDDIT_CLIENT_SECRET="your_client_secret"
   export REDDIT_USER_AGENT="UserPersonaBuilder/1.0 by u/YourRedditUsername"
