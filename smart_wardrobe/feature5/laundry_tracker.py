import gradio as gr
import json
import datetime

# File paths
WARDROBE_FILE = "wardrobe_data.json"
HISTORY_FILE = "suggestion_history.json"

# Load/Save JSON
def load_json(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return f"<b>Error: The file '{file}' was not found.</b>"
    except json.JSONDecodeError:
        return f"<b>Error: The file '{file}' contains invalid JSON.</b>"
    except Exception as e:
        return f"<b>Error loading the file '{file}': {repr(e)}</b>"

def save_json(file, data):
    try:
        with open(file, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        return f"<b>Error saving the file '{file}': {repr(e)}</b>"

wardrobe_data = load_json(WARDROBE_FILE)

# --- Laundry Tracker Logic ---
def get_laundry_items(username, status_filter):
    try:
        user_items = wardrobe_data.get(username, {}).get("clothing_items", [])
        
        if not user_items:
            raise ValueError(f"No clothing items found for username '{username}'.")

        # Filter items by status
        filtered = [item for item in user_items if item.get("status") == status_filter]
        
        if not filtered:
            return f"<b>No items found with status: {status_filter}</b>"
        
        html = f"<b>{status_filter} Items:</b><ul>"
        
        for item in filtered:
            item_name = item.get("item_name", "Unnamed Item")  # Corrected from 'name' to 'item_name'
            category = item.get("category", "Unknown Category")  # Default value if missing

            # Check for missing values
            if item_name == "Unnamed Item":
                raise ValueError(f"Item '{item}' is missing a name.")
            if category == "Unknown Category":
                raise ValueError(f"Item '{item}' is missing a category.")

            html += f"<li>{item_name} ({category})</li>"
        
        html += "</ul>"
        return html

    except Exception as e:
        # Provide detailed error message with context
        error_message = f"<b>Error occurred while retrieving laundry items:</b> {str(e)}<br>"
        error_message += f"<i>Username:</i> {username}<br>"
        error_message += f"<i>Status Filter:</i> {status_filter}<br>"
        error_message += f"<i>Full Error:</i> {repr(e)}"
        return error_message

def update_item_status(username, item_name, new_status):
    try:
        user_items = wardrobe_data.get(username, {}).get("clothing_items", [])
        
        if not user_items:
            raise ValueError(f"No clothing items found for username '{username}'.")

        item_found = False
        for item in user_items:
            if item.get("item_name") == item_name:  # Corrected from 'name' to 'item_name'
                item["status"] = new_status
                if new_status == "Clean":
                    item["last_washed"] = str(datetime.date.today())
                item_found = True
                break

        if not item_found:
            raise ValueError(f"Item '{item_name}' not found in wardrobe.")
        
        save_json(WARDROBE_FILE, wardrobe_data)
        return f"<b>Updated {item_name} to {new_status}</b>"

    except Exception as e:
        error_message = f"<b>Error occurred while updating item status:</b> {str(e)}<br>"
        error_message += f"<i>Username:</i> {username}<br>"
        error_message += f"<i>Item Name:</i> {item_name}<br>"
        error_message += f"<i>New Status:</i> {new_status}<br>"
        error_message += f"<i>Full Error:</i> {repr(e)}"
        return error_message

def generate_laundry_list(username):
    try:
        user_items = wardrobe_data.get(username, {}).get("clothing_items", [])
        
        if not user_items:
            raise ValueError(f"No clothing items found for username '{username}'.")

        dirty_items = [item for item in user_items if item.get("status") == "Dirty"]
        
        if not dirty_items:
            return "<b>No dirty items in wardrobe.</b>"
        
        result = "<b>Laundry List:</b><ul>"
        for item in dirty_items:
            result += f"<li>{item.get('item_name')} ({item.get('category')})</li>"  # Corrected from 'name' to 'item_name'
        result += "</ul>"
        return result

    except Exception as e:
        error_message = f"<b>Error occurred while generating laundry list:</b> {str(e)}<br>"
        error_message += f"<i>Username:</i> {username}<br>"
        error_message += f"<i>Full Error:</i> {repr(e)}"
        return error_message

# --- Style Evolution Analysis ---
def analyze_style(username):
    try:
        wardrobe = []

        if isinstance(wardrobe_data, dict):
            user_wardrobe = wardrobe_data.get(username)
            if isinstance(user_wardrobe, list):
                wardrobe = user_wardrobe
            elif isinstance(user_wardrobe, dict):
                wardrobe = user_wardrobe.get("wardrobe") or user_wardrobe.get("clothing_items", [])

        if not wardrobe or not isinstance(wardrobe, list):
            return "<b>No wardrobe data available to analyze style evolution.</b>"

        category_count = {}
        color_count = {}
        year_count = {}

        for item in wardrobe:
            if not isinstance(item, dict):
                continue
            category = str(item.get("category", "Unknown"))
            color = str(item.get("color", "Unknown"))
            year = str(item.get("year", "Unknown"))

            category_count[category] = category_count.get(category, 0) + 1
            color_count[color] = color_count.get(color, 0) + 1
            year_count[year] = year_count.get(year, 0) + 1

        result = f"<b>📈 Style Evolution for {username}</b><br><br>"
        result += "<b>Top Categories:</b><br>" + "<br>".join(f"- {cat}: {count}" for cat, count in sorted(category_count.items(), key=lambda x: x[1], reverse=True)) + "<br><br>"
        result += "<b>Preferred Colors:</b><br>" + "<br>".join(f"- {col}: {count}" for col, count in sorted(color_count.items(), key=lambda x: x[1], reverse=True)) + "<br><br>"
        result += "<b>Wardrobe Additions Over Years:</b><br>" + "<br>".join(f"- {yr}: {count}" for yr, count in sorted(year_count.items()))
        result += "<br><br><i>Insight:</i> You seem to be exploring more colors and categories in recent years! 🌟"
        return result

    except Exception as e:
        return f"<b>Error analyzing style evolution:</b> {str(e)}"

# --- Gradio Interface ---
with gr.Blocks(title="🧺 Laundry & Style Assistant") as laundry_interface:
    gr.Markdown("### 🧺 Laundry Care Assistant")
    username_input = gr.Textbox(label="Username", placeholder="e.g., Anuradha")

    with gr.Tab("🧺 Laundry Tracker"):
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### ✏️ Update Item Status")
                item_name_input = gr.Textbox(label="Item Name", placeholder="e.g., jeans")
                status_dropdown = gr.Dropdown(["Clean", "Dirty", "Needs Repair"], label="New Status")
                update_button = gr.Button("✅ Update Status", variant="primary")
                update_result = gr.HTML()
                update_button.click(update_item_status, inputs=[username_input, item_name_input, status_dropdown], outputs=update_result)

            with gr.Column(scale=1):
                gr.Markdown("### 🔎 View by Status")
                with gr.Row():
                    dirty_button = gr.Button("🟥 Dirty")
                    repair_button = gr.Button("🛠 Needs Repair")
                    clean_button = gr.Button("🟩 Clean")
                status_result = gr.HTML()
                dirty_button.click(get_laundry_items, inputs=[username_input, gr.Textbox(value="Dirty", visible=False)], outputs=status_result)
                repair_button.click(get_laundry_items, inputs=[username_input, gr.Textbox(value="Needs Repair", visible=False)], outputs=status_result)
                clean_button.click(get_laundry_items, inputs=[username_input, gr.Textbox(value="Clean", visible=False)], outputs=status_result)

        gr.Markdown("### 🧾 Laundry List Generator")
        laundry_list_btn = gr.Button("🧼 Generate Laundry List")
        laundry_list_output = gr.HTML()
        laundry_list_btn.click(generate_laundry_list, inputs=username_input, outputs=laundry_list_output)

    with gr.Tab("👗 Style Evolution"):
        gr.Markdown("### 📈 Analyze Your Fashion Style")
        analyze_button = gr.Button("🔍 Analyze Style")
        style_output = gr.HTML()
        analyze_button.click(analyze_style, inputs=username_input, outputs=style_output)
