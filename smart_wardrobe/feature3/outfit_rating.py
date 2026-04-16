import random

def get_ai_score(outfit):
    return random.uniform(6, 10)

def rate_outfit(username, outfit_items, user_score=None):
    ai_score = get_ai_score(outfit_items)
    if user_score is not None:
        return f"AI Score: {ai_score:.2f}\nYour Score: {user_score:.2f}"
    return f"AI Score: {ai_score:.2f}"
