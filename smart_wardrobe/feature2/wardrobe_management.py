import gradio as gr
import json
import random
import os
import csv
import shutil
from datetime import datetime

# Ensure static/images directory exists
os.makedirs("static/images", exist_ok=True)

# Load wardrobe data
try:
    with open("wardrobe_data.json", "r") as f:
        wardrobe_data = json.load(f)
except FileNotFoundError:
    wardrobe_data = {}

def save_wardrobe_data():
    with open("wardrobe_data.json", "w") as f:
        json.dump(wardrobe_data, f, indent=4)

# Function to fix existing image paths in the data
def fix_existing_image_paths():
    for username, user_data in wardrobe_data.items():
        for item in user_data.get("clothing_items", []):
            if item.get("image"):
                # If it's a full path, extract just the filename
                item["image"] = os.path.basename(item["image"])
    save_wardrobe_data()
    print("Fixed existing image paths in the data")

# Call this function when the application starts
fix_existing_image_paths()

def backup_data():
    backup_filename = f"wardrobe_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_filename, "w") as f:
        json.dump(wardrobe_data, f, indent=4)
    return backup_filename



# Add clothing item with proper image handling
# Add clothing item with proper image handling
def add_clothing_item(username, category, item_name, brand, color, material, size, pattern, style, occasion, image=None):
    if username not in wardrobe_data:
        wardrobe_data[username] = {"clothing_items": []}

    # Handle image saving
    image_path = None
    if image:
        # Ensure directory exists
        os.makedirs("static/images", exist_ok=True)
        
        # Create a safe filename
        safe_item_name = f"{username}_{item_name}".replace(" ", "_").lower()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Get file extension or default to .jpg
        if isinstance(image, str):
            ext = os.path.splitext(image)[1]
        else:
            ext = ".jpg"
            
        image_filename = f"{safe_item_name}_{timestamp}{ext}"
        dest_path = os.path.join("static/images", image_filename)
        
        try:
            # Copy the uploaded image to our static directory
            if isinstance(image, str) and os.path.exists(image):
                shutil.copy2(image, dest_path)
            else:
                # For Gradio temporary files
                with open(image, "rb") as src, open(dest_path, "wb") as dst:
                    dst.write(src.read())
                    
            # Store just the filename, not the full path
            image_path = image_filename
            print(f"Image saved to: {dest_path}")
        except Exception as e:
            print(f"Error saving image: {e}")
            image_path = None

    new_item = {
        "category": category,
        "item_name": item_name,
        "brand": brand,
        "color": color if isinstance(color, list) else [color],
        "material": material,
        "size": size,
        "pattern": pattern,
        "style": style,
        "occasion": occasion,
        "worn_count": 0,
        "image": image_path,  # Just store the filename
        "pairings": [],
        "favorite": False
    }

    wardrobe_data[username]["clothing_items"].append(new_item)
    save_wardrobe_data()
    return f"Clothing item '{item_name}' added successfully!"



# Sample items generator
def generate_sample_items(username):
    if username not in wardrobe_data:
        wardrobe_data[username] = {"clothing_items": []}
        
    sample_items = [
        {
            "category": "Accessories",
            "item_name": "Sunglasses",
            "brand": "Ray-Ban"
        },
        {
            "category": "Perfume",
            "item_name": "Chanel No.5",
            "brand": "Chanel"
        },
        {
            "category": "Hairstyle",
            "item_name": "Slick Back",
            "brand": "Hairdo"
        }
    ]

    # Enhanced dropdown options
    colors = ["Red", "Blue", "Green", "Black", "White", "Beige", "Yellow", "Pink", "Purple", "Orange", "Brown", "Grey", "Multicolor"]
    sizes = ["XS", "S", "M", "L", "XL", "XXL", "Free Size", "Custom"]
    patterns = ["Solid", "Striped", "Floral", "Polka Dots", "Checked", "Geometric", "Animal Print", "Abstract", "Tie-Dye", "Embroidery"]
    styles = ["Modern", "Classic", "Bohemian", "Vintage", "Streetwear", "Minimalist", "Athleisure", "Chic", "Trendy", "Preppy"]
    occasions = ["Casual", "Formal", "Party", "Work", "Wedding", "Interview", "Travel", "Festival", "Beach", "Night Out", "Religious Event"]
    materials = ["Cotton", "Silk", "Linen", "Denim", "Leather", "Polyester", "Wool", "Rayon", "Nylon", "Velvet", "Chiffon"]

    for item in sample_items:
        item["color"] = random.sample(colors, k=random.randint(1, 2))
        item["size"] = random.choice(sizes)
        item["pattern"] = random.choice(patterns)
        item["style"] = random.choice(styles)
        item["occasion"] = random.choice(occasions)
        item["material"] = random.choice(materials)
        item["worn_count"] = 0
        item["favorite"] = random.choice([True, False])
        item["image"] = None
        item["pairings"] = []
        
        wardrobe_data[username]["clothing_items"].append(item)
    
    save_wardrobe_data()
    return f"Added {len(sample_items)} sample wardrobe items."

# Export function
def export_wardrobe(username, format):
    if username not in wardrobe_data:
        return None, "User not found."

    filename = f"{username}_wardrobe_export.{format.lower()}"
    items = wardrobe_data[username]["clothing_items"]

    try:
        if format == "JSON":
            with open(filename, "w") as f:
                json.dump(items, f, indent=4)
        elif format == "CSV":
            # Convert all items to flat dicts with stringified list values
            flattened_items = []
            for item in items:
                flat_item = {}
                for k, v in item.items():
                    if isinstance(v, list):
                        flat_item[k] = ", ".join(map(str, v))
                    elif v is None:
                        flat_item[k] = ""
                    else:
                        flat_item[k] = v
                flattened_items.append(flat_item)

            with open(filename, "w", newline='') as f:
                writer = csv.DictWriter(f, fieldnames=flattened_items[0].keys())
                writer.writeheader()
                writer.writerows(flattened_items)
        return filename, f"Exported wardrobe as {filename}"
    except Exception as e:
        return None, f"Export failed: {e}"

# Preview items before importing
def preview_import(file_obj):
    if not file_obj:
        return "No file uploaded."
    ext = os.path.splitext(file_obj.name)[-1].lower()
    try:
        if ext == ".json":
            with open(file_obj.name, "r") as f:
                items = json.load(f)
        elif ext == ".csv":
            with open(file_obj.name, "r") as f:
                reader = csv.DictReader(f)
                items = list(reader)
        else:
            return "Unsupported file format."

        preview_html = "<ul>"
        for item in items[:10]:
            preview_html += f"<li>{item.get('item_name', 'Unknown Item')} - {item.get('category', '')} ({item.get('brand', '')})</li>"
        preview_html += "</ul>"

        return preview_html
    except Exception as e:
        return f"Error previewing file: {e}"

# Import logic
def import_wardrobe(username, file_obj):
    if not file_obj:
        return "No file provided."
    if username not in wardrobe_data:
        wardrobe_data[username] = {"clothing_items": []}

    ext = os.path.splitext(file_obj.name)[-1].lower()
    try:
        backup_file = backup_data()
        new_items = []

        if ext == ".json":
            with open(file_obj.name, "r") as f:
                new_items = json.load(f)
        elif ext == ".csv":
            with open(file_obj.name, "r") as f:
                reader = csv.DictReader(f)
                new_items = list(reader)
                for item in new_items:
                    if "color" in item and isinstance(item["color"], str):
                        try:
                            item["color"] = json.loads(item["color"].replace("'", '"'))
                        except:
                            item["color"] = [item["color"]]

        existing = wardrobe_data[username]["clothing_items"]
        added = 0
        for item in new_items:
            if item not in existing:
                item["favorite"] = item.get("favorite", False)  # Ensure favorite exists
                existing.append(item)
                added += 1

        save_wardrobe_data()
        return f"Imported {added} new items. Backup created: {backup_file}"
    except Exception as e:
        return f"Import failed: {e}"

def delete_uploaded_file(file_obj):
    if file_obj and hasattr(file_obj, 'name') and os.path.exists(file_obj.name):
        deleted_filename = file_obj.name
        os.remove(deleted_filename)
        print(f"Deleted file: {deleted_filename}")
        return f"Deleted file: {deleted_filename}"
    return "No file deleted. File might not exist."

# Enhanced View/Filter logic with proper image handling# Enhanced View/Filter logic with proper image handling
# Enhanced View/Filter logic with proper image handling
def get_filtered_clothing_items(username, view, category, color, size, brand, occasion):
    if username not in wardrobe_data or not wardrobe_data[username].get("clothing_items"):
        return "<p>No items found for this user.</p>"
    
    items = wardrobe_data[username]["clothing_items"]
    
    def match(item):
        return (
            (not category or item["category"] == category) and
            (not color or color in item.get("color", [])) and
            (not size or item["size"] == size) and
            (not brand or brand.lower() in item["brand"].lower()) and
            (not occasion or item["occasion"] == occasion)
        )
    
    filtered = [i for i in items if match(i)]
    
    if not filtered:
        return "<p>No items matched your filters.</p>"
    
    if view == "grid":
        html = "<div style='display:flex;flex-wrap:wrap;gap:20px;'>"
        
        for item in filtered:
            # Handle image display
            if item.get("image"):
                # Check if the image exists in the static/images directory
                image_path = os.path.join("static/images", item["image"])
                if os.path.exists(image_path):
                    # Use data URI to embed the image directly in the HTML
                    with open(image_path, "rb") as img_file:
                        import base64
                        img_data = base64.b64encode(img_file.read()).decode('utf-8')
                        img_type = "jpeg" if image_path.lower().endswith(".jpg") or image_path.lower().endswith(".jpeg") else "png"
                        image_src = f"data:image/{img_type};base64,{img_data}"
                else:
                    image_src = "https://via.placeholder.com/150?text=Image+Not+Found"
            else:
                image_src = "https://via.placeholder.com/150?text=No+Image"
            
            # Create a card for each item
            star = "⭐" if item.get("favorite") else ""
            colors_display = ", ".join(item.get("color", ["Unknown"]))
            
            html += f"""
            <div style='width:200px;border:1px solid #ddd;border-radius:8px;padding:10px;box-shadow:0 2px 4px rgba(0,0,0,0.1);'>
                <div style='height:150px;display:flex;align-items:center;justify-content:center;overflow:hidden;margin-bottom:10px;'>
                    <img src='{image_src}' style='max-width:100%;max-height:100%;object-fit:contain;'>
                </div>
                <h3 style='margin:5px 0;font-size:16px;'>{item['item_name']} {star}</h3>
                <p style='margin:3px 0;font-size:14px;color:#666;'>{item['category']} | {item['brand']}</p>
                <p style='margin:3px 0;font-size:13px;'>Color: {colors_display}</p>
                <p style='margin:3px 0;font-size:13px;'>Size: {item['size']}</p>
                <p style='margin:3px 0;font-size:13px;'>Occasion: {item['occasion']}</p>
            </div>
            """
        
        html += "</div>"
        return html
    else:
        # List view with table
        html = """
        <table style='width:100%;border-collapse:collapse;'>
            <thead>
                <tr style='background-color:#f2f2f2;'>
                    <th style='padding:10px;text-align:left;border:1px solid #ddd;'>Image</th>
                    <th style='padding:10px;text-align:left;border:1px solid #ddd;'>Item Name</th>
                    <th style='padding:10px;text-align:left;border:1px solid #ddd;'>Category</th>
                    <th style='padding:10px;text-align:left;border:1px solid #ddd;'>Brand</th>
                    <th style='padding:10px;text-align:left;border:1px solid #ddd;'>Color</th>
                    <th style='padding:10px;text-align:left;border:1px solid #ddd;'>Size</th>
                    <th style='padding:10px;text-align:left;border:1px solid #ddd;'>Occasion</th>
                    <th style='padding:10px;text-align:left;border:1px solid #ddd;'>Favorite</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for item in filtered:
            # Handle image display for list view
            if item.get("image"):
                image_path = os.path.join("static/images", item["image"])
                if os.path.exists(image_path):
                    # Use data URI to embed the image directly in the HTML
                    with open(image_path, "rb") as img_file:
                        import base64
                        img_data = base64.b64encode(img_file.read()).decode('utf-8')
                        img_type = "jpeg" if image_path.lower().endswith(".jpg") or image_path.lower().endswith(".jpeg") else "png"
                        image_src = f"data:image/{img_type};base64,{img_data}"
                else:
                    image_src = "https://via.placeholder.com/50?text=Not+Found"
            else:
                image_src = "https://via.placeholder.com/50?text=No+Image"
            
            colors_display = ", ".join(item.get("color", ["Unknown"]))
            star = "⭐" if item.get("favorite") else ""
            
            html += f"""
            <tr>
                <td style='padding:10px;border:1px solid #ddd;'><img src='{image_src}' style='width:50px;height:50px;object-fit:cover;'></td>
                <td style='padding:10px;border:1px solid #ddd;'>{item['item_name']}</td>
                <td style='padding:10px;border:1px solid #ddd;'>{item['category']}</td>
                <td style='padding:10px;border:1px solid #ddd;'>{item['brand']}</td>
                <td style='padding:10px;border:1px solid #ddd;'>{colors_display}</td>
                <td style='padding:10px;border:1px solid #ddd;'>{item['size']}</td>
                <td style='padding:10px;border:1px solid #ddd;'>{item['occasion']}</td>
                <td style='padding:10px;border:1px solid #ddd;'>{star}</td>
            </tr>
            """


        
        html += """
            </tbody>
        </table>
        """
        return html

# Edit/Delete logic
def update_item(username, index, field, value):
    if username in wardrobe_data and 0 <= index < len(wardrobe_data[username]["clothing_items"]):
        # Handle special case for color which should be a list
        if field == "color" and not isinstance(value, list):
            value = [value.strip() for value in value.split(",")]
        
        wardrobe_data[username]["clothing_items"][index][field] = value
        save_wardrobe_data()
        return f"Item updated successfully! Field '{field}' set to '{value}'."
    return "Error updating item. Please check the index and try again."

def delete_item(username, index):
    if username in wardrobe_data and 0 <= index < len(wardrobe_data[username]["clothing_items"]):
        deleted_item = wardrobe_data[username]["clothing_items"].pop(index)
        save_wardrobe_data()
        return f"Item '{deleted_item['item_name']}' at index {index} deleted."
    return "Error deleting item. Please check the index and try again."

# Toggle favorite
def toggle_favorite(username, index):
    if username in wardrobe_data and 0 <= index < len(wardrobe_data[username]["clothing_items"]):
        item = wardrobe_data[username]["clothing_items"][index]
        item["favorite"] = not item.get("favorite", False)
        save_wardrobe_data()
        return f"Favorite set to {item['favorite']} for item '{item['item_name']}'"
    return "Error toggling favorite. Please check the index and try again."

# Get all items for a user (for display in the UI)
def get_all_items(username):
    if username not in wardrobe_data or not wardrobe_data[username].get("clothing_items"):
        return []
    return wardrobe_data[username]["clothing_items"]

# Get item count for a user
def get_item_count(username):
    if username not in wardrobe_data or not wardrobe_data[username].get("clothing_items"):
        return 0
    return len(wardrobe_data[username]["clothing_items"])

# Gradio UI
with gr.Blocks(css="footer {visibility: hidden}") as wardrobe_management_interface:
    gr.Markdown("# Smart Wardrobe Management System")
    username = gr.Textbox(label="Username", placeholder="Enter your username")
    
    with gr.Tab("Add Clothing Item"):
        gr.Markdown("## Add New Clothing Item")
        with gr.Row():
            with gr.Column(scale=1):
                category = gr.Dropdown(
                    ["Tops", "Bottoms", "Dresses", "Outerwear", "Accessories", "Shoes", "Perfume", "Hairstyle", "Jewelry", "Sportswear", "Sleepwear", "Ethnic", "Casual", "Formal"],
                    label="Category"
                )
                item_name = gr.Textbox(label="Item Name", placeholder="Enter item name")
                brand = gr.Textbox(placeholder="Enter brand name", label="Brand")
                color = gr.Dropdown(
                    ["Red", "Blue", "Green", "Black", "White", "Beige", "Yellow", "Pink", "Purple", "Orange", "Brown", "Grey", "Multicolor"],
                    label="Color",
                    multiselect=True
                )
                material = gr.Dropdown(
                    ["Cotton", "Silk", "Linen", "Denim", "Leather", "Polyester", "Wool", "Rayon", "Nylon", "Velvet", "Chiffon"],
                    label="Material"
                )
            
            with gr.Column(scale=1):
                size = gr.Dropdown(
                    ["XS", "S", "M", "L", "XL", "XXL", "Free Size", "Custom"],
                    label="Size"
                )
                pattern = gr.Dropdown(
                    ["Solid", "Striped", "Floral", "Polka Dots", "Checked", "Geometric", "Animal Print", "Abstract", "Tie-Dye", "Embroidery"],
                    label="Pattern"
                )
                style = gr.Dropdown(
                    ["Modern", "Classic", "Bohemian", "Vintage", "Streetwear", "Minimalist", "Athleisure", "Chic", "Trendy", "Preppy"],
                    label="Style"
                )
                occasion = gr.Dropdown(
                    ["Casual", "Formal", "Party", "Work", "Wedding", "Interview", "Travel", "Festival", "Beach", "Night Out", "Religious Event"],
                    label="Occasion"
                )
                image = gr.Image(label="Image (Optional)", type="filepath")
        
        with gr.Row():
            add_btn = gr.Button("Add Item", variant="primary")
            sample_btn = gr.Button("Generate Sample Items")
        
        add_output = gr.Textbox(label="Status")
        
        add_btn.click(add_clothing_item, inputs=[
            username, category, item_name, brand, color, material, size,
            pattern, style, occasion, image
        ], outputs=add_output)
        
        sample_btn.click(generate_sample_items, inputs=[username], outputs=add_output)

    with gr.Tab("View & Filter Wardrobe"):
        gr.Markdown("## Browse Your Wardrobe")
        
        with gr.Row():
            view_type = gr.Radio(["grid", "list"], label="View As", value="grid")
            item_counter = gr.Textbox(label="Item Count", value="0")
        
        with gr.Accordion("Filters", open=True):
            with gr.Row():
                f_category = gr.Dropdown(["", "Tops", "Bottoms", "Dresses", "Outerwear", "Accessories", "Shoes", "Perfume", "Hairstyle", "Jewelry", "Sportswear", "Sleepwear", "Ethnic", "Casual", "Formal"], label="Category")
                f_color = gr.Dropdown(["", "Red", "Blue", "Green", "Yellow", "Pink", "Purple", "Beige", "Black", "White", "Orange", "Brown", "Grey", "Multicolor"], label="Color")
                f_size = gr.Dropdown(["","XS", "S", "M", "L", "XL", "XXL", "Free Size", "Custom"], label="Size")
            
            with gr.Row():
                f_brand = gr.Textbox(placeholder="Enter brand name", label="Brand")
                f_occasion = gr.Dropdown(["", "Casual","Formal", "Party", "Wedding", "Interview", "Travel", "Date", "Business", "Gym", "Beach", "Festival", "Religious Event", "Night Out"], label="Occasion")
        
        refresh_btn = gr.Button("Refresh Wardrobe View")
        wardrobe_view = gr.HTML()
        
        # Update item count when username changes
        username.change(
            lambda u: str(get_item_count(u)),
            inputs=[username],
            outputs=[item_counter]
        )
        
        # Update wardrobe view when filters change or refresh button is clicked
        for comp in [view_type, f_category, f_color, f_size, f_brand, f_occasion, refresh_btn]:
            comp.change(
                get_filtered_clothing_items, 
                inputs=[username, view_type, f_category, f_color, f_size, f_brand, f_occasion],
                outputs=wardrobe_view
            ) if hasattr(comp, 'change') else None
            
            if hasattr(comp, 'click'):
                comp.click(
                    get_filtered_clothing_items, 
                    inputs=[username, view_type, f_category, f_color, f_size, f_brand, f_occasion],
                    outputs=wardrobe_view
                )

    with gr.Tab("Import/Export"):
        gr.Markdown("## Import & Export Your Wardrobe")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Export Wardrobe")
                format = gr.Radio(["JSON", "CSV"], label="Export Format", value="JSON")
                export_btn = gr.Button("Export Wardrobe")
                export_file = gr.File(label="Download Exported File")
                export_status = gr.Textbox(label="Export Status")
            
            with gr.Column(scale=1):
                gr.Markdown("### Import Wardrobe")
                import_file = gr.File(label="Upload JSON/CSV File")
                preview_btn = gr.Button("Preview File")
                preview_html = gr.HTML(label="Import Preview")
                import_btn = gr.Button("Import Wardrobe")
                import_status = gr.Textbox(label="Import Status")
                delete_file_btn = gr.Button("Delete Uploaded File")
                delete_status = gr.Textbox(label="Delete File Status")
        
        export_btn.click(fn=export_wardrobe, inputs=[username, format], outputs=[export_file, export_status])
        preview_btn.click(preview_import, inputs=[import_file], outputs=preview_html)
        import_btn.click(fn=import_wardrobe, inputs=[username, import_file], outputs=import_status)
        delete_file_btn.click(delete_uploaded_file, inputs=[import_file], outputs=delete_status)

    with gr.Tab("Manage Items"):
        gr.Markdown("## Edit & Delete Items")
        
        with gr.Row():
            index = gr.Number(label="Item Index", precision=0, value=0)
            field = gr.Dropdown(
                ["category", "item_name", "brand", "color", "material", "size", "pattern", "style", "occasion"], 
                label="Field to Update"
            )
            new_value = gr.Textbox(label="New Value")
        
        with gr.Row():
            update_btn = gr.Button("Update Item")
            delete_btn = gr.Button("Delete Item")
            toggle_fav_btn = gr.Button("Toggle Favorite")
        
        manage_output = gr.Textbox(label="Manage Status")
        
        # Display current items to help with index selection
        item_display = gr.HTML(label="Current Items")
        
        def format_items_for_display(username):
            items = get_all_items(username)
            if not items:
                return "<p>No items found for this user.</p>"
            
            html = """
            <table style='width:100%;border-collapse:collapse;'>
                <thead>
                    <tr style='background-color:#f2f2f2;'>
                        <th style='padding:8px;text-align:left;border:1px solid #ddd;'>Index</th>
                        <th style='padding:8px;text-align:left;border:1px solid #ddd;'>Item Name</th>
                        <th style='padding:8px;text-align:left;border:1px solid #ddd;'>Category</th>
                        <th style='padding:8px;text-align:left;border:1px solid #ddd;'>Brand</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for i, item in enumerate(items):
                star = "⭐" if item.get("favorite") else ""
                html += f"""
                <tr>
                    <td style='padding:8px;border:1px solid #ddd;'>{i}</td>
                    <td style='padding:8px;border:1px solid #ddd;'>{item['item_name']} {star}</td>
                    <td style='padding:8px;border:1px solid #ddd;'>{item['category']}</td>
                    <td style='padding:8px;border:1px solid #ddd;'>{item['brand']}</td>
                </tr>
                """
            
            html += """
                </tbody>
            </table>
            """
            return html
        
        # Update item display when username changes
        username.change(format_items_for_display, inputs=[username], outputs=[item_display])
        
        # Connect buttons to functions
        update_btn.click(update_item, inputs=[username, index, field, new_value], outputs=manage_output)
        delete_btn.click(delete_item, inputs=[username, index], outputs=manage_output)
        toggle_fav_btn.click(toggle_favorite, inputs=[username, index], outputs=manage_output)
        
        # Refresh item display after operations
        for btn in [update_btn, delete_btn, toggle_fav_btn]:
            btn.click(format_items_for_display, inputs=[username], outputs=[item_display])


