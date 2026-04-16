import gradio as gr 
import json
from random import choice

# Improved recommendation logic
def recommend_packing_for_trip(username, days, destination, wardrobe_data):
    print(f"Received username: {username}")
    print(f"Received wardrobe data: {wardrobe_data}")
    
    if not isinstance(wardrobe_data, dict):
         return "⚠️ It looks like we don't have enough matching items in your wardrobe for this trip. Please make sure you have clothing items suitable for the destination. 🌞"
    
    if username not in wardrobe_data:
        return f"🚨 Oops! We couldn't find a wardrobe for {username}. Please ensure your username is correct. 🔄"

    wardrobe = wardrobe_data[username].get("clothing_items", [])
    if not wardrobe:
        return "👚 Your wardrobe is currently empty. Please add some clothing items to your wardrobe to get packing suggestions. 🧳"

    destination_tag = destination.lower().strip()

    def match_items(category, fallback_tags=[]):
        filtered = [
            item for item in wardrobe
            if item.get("category", "").lower() == category.lower()
            and any(tag.lower() in item.get("tags", []) for tag in fallback_tags)
        ]
        if not filtered:
            filtered = [
                item for item in wardrobe
                if item.get("category", "").lower() == category.lower()
            ]
        return filtered

    if "hot" in destination_tag:
        temperature_tags = ["hot", "summer"]
    elif "cold" in destination_tag:
        temperature_tags = ["cold", "winter"]
    else:
        temperature_tags = ["neutral", "casual"]

    top_items = match_items("Top", temperature_tags + [destination_tag])
    bottom_items = match_items("Bottom", temperature_tags + [destination_tag])
    footwear_items = match_items("Footwear", ["beach", "travel", destination_tag])
    accessory_items = match_items("Accessory", ["sunny", "vacation", destination_tag])

    if not top_items or not bottom_items or not footwear_items:
        return "⚠️ It looks like we don't have enough matching items in your wardrobe for this trip. Please make sure you have clothing items suitable for the destination. 🌞"

    packing_list = ""
    for day in range(1, days + 1):
        top = choice(top_items)["item_name"]
        bottom = choice(bottom_items)["item_name"]
        footwear = choice(footwear_items)["item_name"]
        accessory = choice(accessory_items)["item_name"] if accessory_items else "No accessory"
        packing_list += f"📅 Day {day}: {top}, {bottom}, {footwear}, {accessory}\n"

    return packing_list.strip()

# Function to handle logout
def logout():
    return "", 3, "", ""  # Reset username, days, destination, and output

# Packing Assistant UI
with gr.Blocks() as packing_assistant_interface:
    gr.Markdown("## 🧳 AI-Powered Packing Assistant")

    with gr.Row():
        username_input = gr.Textbox(label="Enter Your Name")
        days_input = gr.Number(label="Number of Days", value=3, minimum=1)
        destination_input = gr.Textbox(label="Trip Destination", placeholder="e.g., Goa, Shimla")

    wardrobe_data_input = gr.State()

    with gr.Row():
        generate_button = gr.Button("Generate Packing Suggestions ✨")
        logout_button = gr.Button("Log Out 🔓")

    packing_output = gr.Textbox(label="Packing List", lines=10)

    generate_button.click(
        recommend_packing_for_trip,
        inputs=[username_input, days_input, destination_input, wardrobe_data_input],
        outputs=packing_output
    )

    logout_button.click(
        logout,
        outputs=[username_input, days_input, destination_input, packing_output]
    )


