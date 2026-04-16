import gradio as gr
import random
import json
import os

# Enhanced knowledge base for AI styling assistant
skin_tone_makeup = {
    "Fair": ["Peach blush", "Pink lipstick", "Brown eyeliner"],
    "Medium": ["Coral blush", "Mauve lipstick", "Black eyeliner"],
    "Olive": ["Bronze blush", "Nude lipstick", "Brown eyeliner"],
    "Dark": ["Berry blush", "Plum lipstick", "Black eyeliner"]
}

personality_color_mapping = {
    "Bold": ["Red", "Black", "Neon Green"],
    "Elegant": ["Navy", "Ivory", "Maroon"],
    "Casual": ["Blue", "Grey", "White"],
    "Creative": ["Purple", "Teal", "Mustard"]
}

outfit_accessories = {
    "Formal": ["Pearl Necklace", "Leather Watch"],
    "Casual": ["Canvas Tote", "Friendship Bands"],
    "Party": ["Chandelier Earrings", "Shimmer Clutch"],
    "Traditional": ["Jhumkas", "Bangles"]
}

hairstyle_suggestions = {
    "Formal": ["Sleek Bun", "French Twist"],
    "Casual": ["Messy Bun", "Side Braid"],
    "Party": ["Beach Waves", "Curled Ponytail"],
    "Traditional": ["Braided Bun", "Classic Plait"]
}

perfume_matches = {
    "Day": ["Citrus Spark", "Fresh Linen"],
    "Night": ["Floral Bliss", "Mystic Oud"]
}

footwear_recommendations = {
    "Formal": ["Black Loafers", "Nude Heels"],
    "Casual": ["Sneakers", "Flats"],
    "Party": ["Stilettos", "Glitter Sandals"],
    "Traditional": ["Mojaris", "Kolhapuris"]
}

SUGGESTIONS_FILE = "styling_history.json"
if os.path.exists(SUGGESTIONS_FILE):
    with open(SUGGESTIONS_FILE, "r") as f:
        styling_history = json.load(f)
else:
    styling_history = {}

def get_styling_suggestions(username, outfit_type, personality, skin_tone, time_of_day):
    color_suggestions = personality_color_mapping.get(personality, ["Neutral"])
    accessories = outfit_accessories.get(outfit_type, ["Simple Bracelet"])
    hairstyle = random.choice(hairstyle_suggestions.get(outfit_type, ["Classic Ponytail"]))
    makeup = ", ".join(skin_tone_makeup.get(skin_tone, ["Neutral Makeup"]))
    perfume = random.choice(perfume_matches.get(time_of_day, ["Mild Scent"]))
    footwear = random.choice(footwear_recommendations.get(outfit_type, ["Comfortable Flats"]))

    suggestion = {
        "Color Palette": color_suggestions,
        "Accessories": accessories,
        "Hairstyle": hairstyle,
        "Makeup": makeup,
        "Perfume": perfume,
        "Footwear": footwear
    }

    if username not in styling_history:
        styling_history[username] = []
    styling_history[username].append({
        "outfit_type": outfit_type,
        "personality": personality,
        "skin_tone": skin_tone,
        "time_of_day": time_of_day,
        "suggestion": suggestion
    })
    with open(SUGGESTIONS_FILE, "w") as f:
        json.dump(styling_history, f, indent=2)

    return (
        f"👤 User: {username}\n"
        f"🎨 Color Palette for {personality} personality: {', '.join(color_suggestions)}\n"
        f"💎 Accessories for {outfit_type}: {', '.join(accessories)}\n"
        f"💇 Hairstyle: {hairstyle}\n"
        f"💄 Makeup for {skin_tone} skin: {makeup}\n"
        f"🌸 Perfume (for {time_of_day}): {perfume}\n"
        f"👠 Footwear: {footwear}"
    )

def view_past_suggestions(username):
    if username not in styling_history or not styling_history[username]:
        return "No past styling suggestions found."

    entries = styling_history[username][-3:]
    formatted = ""
    for entry in entries:
        suggestion = entry.get("suggestion", {})
        formatted += (
            f"\n👗 Outfit Type: {entry.get('outfit_type', 'N/A')}\n"
            f"→ Personality: {entry.get('personality', 'N/A')} | "
            f"Skin Tone: {entry.get('skin_tone', 'N/A')} | "
            f"Time: {entry.get('time_of_day', 'N/A')}\n"
            f"→ Color Palette: {', '.join(suggestion.get('Color Palette', ['N/A']))}\n"
            f"→ Accessories: {', '.join(suggestion.get('Accessories', ['N/A']))}\n"
            f"→ Hairstyle: {suggestion.get('Hairstyle', 'N/A')}\n"
            f"→ Makeup: {suggestion.get('Makeup', 'N/A')}\n"
            f"→ Perfume: {suggestion.get('Perfume', 'N/A')}\n"
            f"→ Footwear: {suggestion.get('Footwear', 'N/A')}\n"
        )
    return formatted


with gr.Blocks() as styling_suggestions_interface:
    gr.Markdown("## 🤖 AI Styling Assistant")

    username = gr.Textbox(label="Username")
    outfit_type = gr.Dropdown(["Formal", "Casual", "Party", "Traditional"], label="Outfit Type")
    personality = gr.Dropdown(["Bold", "Elegant", "Casual", "Creative"], label="Personality Type")
    skin_tone = gr.Dropdown(["Fair", "Medium", "Olive", "Dark"], label="Skin Tone")
    time_of_day = gr.Radio(["Day", "Night"], label="Time of Day")

    suggest_btn = gr.Button("✨ Get Styling Suggestion")
    suggestion_output = gr.Textbox(label="Styling Recommendation", lines=10)

    view_history_btn = gr.Button("🕘 View Past Suggestions")
    history_output = gr.Textbox(label="Past Styling History", lines=10)

    suggest_btn.click(get_styling_suggestions, inputs=[username, outfit_type, personality, skin_tone, time_of_day], outputs=suggestion_output)
    view_history_btn.click(view_past_suggestions, inputs=[username], outputs=history_output)
