import openai
import re
import language_tool_python
from better_profanity import profanity
"""
Before submitting the assignment, describe here in a few sentences what you would have built next if you spent 2 more hours on this project:
If I had spent two more hours on this project, I would have focused on improving the storytelling—perhaps by gamifying it and making it more interactive, 
like a role-playing game with choices. I would also have tried to incorporate lessons at each step or at the end.
"""
# OpenAI API Key (Set before running)
openai.api_key = "key"

# Load a comprehensive banned words dictionary
profanity.load_censor_words()

def load_banned_words():
    """Load banned words from an external file (if available)."""
    try:
        with open("banned_words.txt", "r") as file:
            return set(word.strip().lower() for word in file)
    except FileNotFoundError:
        return set()  # Return an empty set if the file is missing

BANNED_WORDS = load_banned_words()

# Suggested replacement themes for inappropriate topics
SUGGESTED_THEMES = [
    "fantasy", "adventure", "moral lesson", "talking animals", "space exploration", "magical lands"
]

def moderate_input(user_input: str) -> str:
    """Cleans user input by masking sensitive data and filtering inappropriate words."""
    
    # Mask personal information (like phone numbers)
    user_input = re.sub(r'\b\d{7,}\b', '[REDACTED]', user_input)

    # Check for inappropriate words from both lists
    words = set(user_input.lower().split())
    if words.intersection(BANNED_WORDS) or profanity.contains_profanity(user_input):
        return None  # Block inappropriate requests

    return user_input

def correct_grammar(text):
    """Corrects grammar and syntax errors using LanguageTool."""
    tool = language_tool_python.LanguageToolPublicAPI('en-US')
    matches = tool.check(text)
    return language_tool_python.utils.correct(text, matches)

def call_model(prompt: str, max_tokens=500, temperature=0.7) -> str:
    """Generates a bedtime story using OpenAI API with structured prompts."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return correct_grammar(response["choices"][0]["message"]["content"])  # Correct output grammar
    except Exception as e:
        return f"Sorry, an error occurred: {e}"

def get_story_prompt(user_input: str) -> str:
    """Categorizes story requests and generates structured prompts."""
    categories = {
        "fantasy": "Tell a magical bedtime story for kids aged 5-10 about a brave young wizard and their adventure.",
        "adventure": "Create an exciting adventure bedtime story featuring a young explorer discovering a hidden treasure.",
        "moral": "Tell a bedtime story that teaches a moral lesson about kindness and honesty, using fun characters.",
        "funny": "Write a silly and humorous bedtime story about a talking pizza and its quest to avoid being eaten."
    }

    keywords = {
        "princess": "fantasy",
        "dragon": "fantasy",
        "space": "adventure",
        "pirate": "adventure",
        "honest": "moral",
        "kindness": "moral",
        "robot": "funny",
        "banana": "funny"
    }

    for word, category in keywords.items():
        if re.search(rf'\b{word}\b', user_input.lower()):
            return categories[category] + f" Include: {user_input}"

    return f"Tell a creative bedtime story for kids aged 5-10. Theme: {user_input}"

def suggest_new_theme():
    """Suggests an alternative story theme to the user."""
    print("\nThat topic isn't suitable for a bedtime story. Here are some fun themes you can try:")
    for theme in SUGGESTED_THEMES:
        print(f"- {theme.capitalize()}")
    print()

def main():
    """Handles user interaction and story generation."""
    print("Welcome to the AI Bedtime Story Generator! 🌙✨")
    
    while True:
        user_input = input("\nWhat kind of story do you want to hear? (Fantasy, Adventure, Moral, Funny, or describe your idea): ").strip()
        clean_text = moderate_input(user_input)

        if clean_text is None:
            print("\n❌ That topic is inappropriate and cannot be used for a bedtime story.")
            suggest_new_theme()
            continue  # Ask for input again

        prompt = get_story_prompt(clean_text)
        story = call_model(prompt)

        print("\nHere's your bedtime story:\n")
        print(story)

        # Allow story modifications
        while True:
            feedback = input("\nWould you like any changes? (e.g.'Add a dragon', 'No'): ").strip().lower()
            if feedback in ["no", "n"]:
                break
            else:
                clean_feedback = moderate_input(feedback)
                if clean_feedback is None:
                    print("\n❌ That modification request is inappropriate. Try again.")
                    continue
                
                story = call_model(prompt + f" {clean_feedback}")
                print("\nUpdated Story:\n")
                print(story)

        # Ask if user wants another story
        another = input("\nWould you like another story? (Yes/No): ").strip().lower()
        if another not in ["yes", "y"]:
            print("\nGoodnight! Sweet dreams! 🌙✨")
            break

if __name__ == "__main__":
    main()
