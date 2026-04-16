import gradio as gr
import json
import os
import hashlib
import base64
import secrets
import time
import shutil
from datetime import datetime

# Ensure the images directory exists
os.makedirs("application/images", exist_ok=True)

# Load user data
try:
    with open("user_data.json", "r") as f:
        user_data = json.load(f)
except FileNotFoundError:
    user_data = {}

def save_user_data():
    with open("user_data.json", "w") as f:
        json.dump(user_data, f, indent=4)

# Function to fix existing profile picture paths in the data
def fix_existing_profile_pic_paths():
    for username, data in user_data.items():
        if data.get("profile_pic"):
            # If it's a full path, extract just the filename and move the file if needed
            old_path = data["profile_pic"]
            if os.path.exists(old_path):
                filename = f"{username}_profile_{datetime.now().strftime('%Y%m%d%H%M%S')}{os.path.splitext(old_path)[1]}"
                new_path = os.path.join("application/images", filename)
                try:
                    shutil.copy2(old_path, new_path)
                    data["profile_pic"] = filename  # Store just the filename
                except Exception as e:
                    print(f"Error copying profile pic for {username}: {e}")
            else:
                # If the file doesn't exist, just store the basename
                data["profile_pic"] = os.path.basename(old_path)
    save_user_data()
    print("Fixed existing profile picture paths in the data")

# Call this function when the application starts
fix_existing_profile_pic_paths()

# Hash password
def hash_password(password, salt=None):
    if salt is None:
        # Generate a random salt for new passwords
        salt = base64.b64encode(secrets.token_bytes(16)).decode('utf-8')
        # Use SHA-256 for hashing
        hashed = hashlib.sha256(password.encode() + salt.encode()).hexdigest()
        return hashed, salt
    else:
        # For verification, use the provided salt
        hashed = hashlib.sha256(password.encode() + salt.encode()).hexdigest()
        return hashed

# Register new user
def register_user(username, password, email, gender, age):
    if username in user_data:
        return "Username already exists. Please choose another one."
    
    if not username or not password or not email:
        return "Username, password, and email are required fields."
    
    hashed_password, salt = hash_password(password)
    
    user_data[username] = {
        "password": hashed_password,
        "salt": salt,
        "email": email,
        "gender": gender,
        "age": int(age) if age else None,
        "preferences": {},
        "profile_pic": "",
        "last_active": time.time()
    }
    
    save_user_data()
    return f"User {username} registered successfully!"

# Login
def login_user(username, password):
    if username not in user_data:
        return False, "Username not found."
    
    stored_password = user_data[username]["password"]
    salt = user_data[username].get("salt", None)
    
    if salt:
        # New salt-based verification
        hashed_input = hash_password(password, salt)
        if hashed_input == stored_password:
            user_data[username]["last_active"] = time.time()
            save_user_data()
            return True, f"Welcome back, {username}!"
        else:
            return False, "Incorrect password."
    else:
        # Legacy verification (no salt)
        hashed_input = hashlib.sha256(password.encode()).hexdigest()
        if hashed_input == stored_password:
            user_data[username]["last_active"] = time.time()
            save_user_data()
            return True, f"Welcome back, {username}!"
        else:
            return False, "Incorrect password."

# Update profile
def update_profile(username, field, value):
    if username not in user_data:
        return "User not found."
    
    if field == "age":
        try:
            value = int(value)
        except ValueError:
            return "Age must be a number."
    
    if field == "preferences":
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return "Invalid JSON format for preferences."
    
    user_data[username][field] = value
    save_user_data()
    return f"Updated {field} for {username}."

# Upload profile picture with proper path handling
def upload_profile_pic(username, image_path):
    if username not in user_data:
        return "User not found."
    
    if not image_path:
        return "No image provided."
    
    try:
        # Create a safe filename using username and timestamp
        ext = os.path.splitext(image_path)[1]
        safe_filename = f"{username}_profile_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
        dest_path = os.path.join("application/images", safe_filename)
        
        # Copy the uploaded image to our images directory
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(image_path, dest_path)
        
        # Store just the filename in the user data
        user_data[username]["profile_pic"] = safe_filename
        save_user_data()
        
        return f"Profile picture updated for {username}."
    except Exception as e:
        return f"Error uploading profile picture: {e}"

# Get profile picture
def get_profile_pic(username):
    if username not in user_data:
        return None
    
    pic_filename = user_data[username].get("profile_pic", "")
    if not pic_filename:
        return None
    
    # Construct the full path
    pic_path = os.path.join("application/images", pic_filename)
    
    if os.path.exists(pic_path):
        return pic_path
    else:
        return None

# Get user preferences
def get_user_preferences(username):
    if username not in user_data:
        return "User not found."
    
    preferences = user_data[username].get("preferences", {})
    return json.dumps(preferences, indent=4)

# Update user preferences
def update_user_preferences(username, favorite_styles, favorite_brands):
    if username not in user_data:
        return "User not found."
    
    if "preferences" not in user_data[username]:
        user_data[username]["preferences"] = {}
    
    # Convert comma-separated strings to lists
    if favorite_styles:
        styles_list = [style.strip() for style in favorite_styles.split(",")]
        user_data[username]["preferences"]["favorite_styles"] = styles_list
    
    if favorite_brands:
        brands_list = [brand.strip() for brand in favorite_brands.split(",")]
        user_data[username]["preferences"]["favorite_brands"] = brands_list
    
    save_user_data()
    return f"Preferences updated for {username}."

# Update body measurements
def update_body_measurements(username, body_type, skin_tone, eye_color, hair_color, height, weight, clothing_size):
    if username not in user_data:
        return "User not found."
    
    user_data[username]["body_type"] = body_type
    user_data[username]["skin_tone"] = skin_tone
    user_data[username]["eye_color"] = eye_color
    user_data[username]["hair_color"] = hair_color
    
    try:
        if height:
            user_data[username]["height"] = float(height)
        if weight:
            user_data[username]["weight"] = float(weight)
    except ValueError:
        return "Height and weight must be numbers."
    
    user_data[username]["clothing_size"] = clothing_size
    
    save_user_data()
    return f"Body measurements updated for {username}."

# Get user profile
def get_user_profile(username):
    if username not in user_data:
        return "User not found."
    
    profile = user_data[username].copy()
    # Remove sensitive information
    if "password" in profile:
        del profile["password"]
    if "salt" in profile:
        del profile["salt"]
    
    return json.dumps(profile, indent=4)

# Display profile picture
def display_profile(username):
    if username not in user_data:
        return "User not found.", None
    
    profile = user_data[username].copy()
    # Remove sensitive information
    if "password" in profile:
        del profile["password"]
    if "salt" in profile:
        del profile["salt"]
    
    # Get profile picture
    pic_filename = profile.get("profile_pic", "")
    pic_path = None
    
    if pic_filename:
        full_path = os.path.join("application/images", pic_filename)
        if os.path.exists(full_path):
            pic_path = full_path
    
    # Format profile data for display
    profile_text = f"Username: {username}\n"
    profile_text += f"Email: {profile.get('email', 'Not provided')}\n"
    profile_text += f"Gender: {profile.get('gender', 'Not provided')}\n"
    profile_text += f"Age: {profile.get('age', 'Not provided')}\n"
    
    if "body_type" in profile:
        profile_text += f"Body Type: {profile['body_type']}\n"
    if "skin_tone" in profile:
        profile_text += f"Skin Tone: {profile['skin_tone']}\n"
    if "height" in profile:
        profile_text += f"Height: {profile['height']} cm\n"
    if "weight" in profile:
        profile_text += f"Weight: {profile['weight']} kg\n"
    if "clothing_size" in profile:
        profile_text += f"Clothing Size: {profile['clothing_size']}\n"
    
    preferences = profile.get("preferences", {})
    if preferences:
        profile_text += "\nPreferences:\n"
        if "favorite_styles" in preferences:
            profile_text += f"Favorite Styles: {', '.join(preferences['favorite_styles'])}\n"
        if "favorite_brands" in preferences:
            profile_text += f"Favorite Brands: {', '.join(preferences['favorite_brands'])}\n"
    
    return profile_text, pic_path

# Gradio UI
with gr.Blocks() as user_management_interface:
    gr.Markdown("# User Management")
    
    with gr.Tab("Register"):
        reg_username = gr.Textbox(label="Username")
        reg_password = gr.Textbox(label="Password", type="password")
        reg_email = gr.Textbox(label="Email")
        reg_gender = gr.Radio(["Male", "Female", "Other"], label="Gender")
        reg_age = gr.Number(label="Age")
        reg_btn = gr.Button("Register")
        reg_output = gr.Textbox(label="Status")
        
        reg_btn.click(register_user, inputs=[reg_username, reg_password, reg_email, reg_gender, reg_age], outputs=reg_output)
    
    with gr.Tab("Login"):
        login_username = gr.Textbox(label="Username")
        login_password = gr.Textbox(label="Password", type="password")
        login_btn = gr.Button("Login")
        login_output = gr.Textbox(label="Status")
        
        def login_handler(username, password):
            success, message = login_user(username, password)
            return message
        
        login_btn.click(login_handler, inputs=[login_username, login_password], outputs=login_output)
    
    with gr.Tab("Profile"):
        profile_username = gr.Textbox(label="Username")
        
        with gr.Accordion("Update Profile Picture"):
            profile_pic = gr.Image(type="filepath", label="Profile Picture")
            upload_pic_btn = gr.Button("Upload Profile Picture")
            pic_status = gr.Textbox(label="Status")
            
            upload_pic_btn.click(upload_profile_pic, inputs=[profile_username, profile_pic], outputs=pic_status)
        
        with gr.Accordion("Update Preferences"):
            favorite_styles = gr.Textbox(label="Favorite Styles (comma-separated)", placeholder="Casual, Formal, Bohemian")
            favorite_brands = gr.Textbox(label="Favorite Brands (comma-separated)", placeholder="Nike, Adidas, Zara")
            update_pref_btn = gr.Button("Update Preferences")
            pref_status = gr.Textbox(label="Status")
            
            update_pref_btn.click(update_user_preferences, inputs=[profile_username, favorite_styles, favorite_brands], outputs=pref_status)
        
        with gr.Accordion("Update Body Measurements"):
            body_type = gr.Dropdown(["Slim", "Athletic", "Average", "Curvy", "Plus Size"], label="Body Type")
            skin_tone = gr.Dropdown(["Fair", "Light", "Medium", "Olive", "Brown", "Dark"], label="Skin Tone")
            eye_color = gr.Dropdown(["Brown", "Blue", "Green", "Hazel", "Black", "Grey"], label="Eye Color")
            hair_color = gr.Dropdown(["Black", "Brown", "Blonde", "Red", "Grey", "White", "Other"], label="Hair Color")
            height = gr.Number(label="Height (cm)")
            weight = gr.Number(label="Weight (kg)")
            clothing_size = gr.Dropdown(["XS", "S", "M", "L", "XL", "XXL", "Custom"], label="Clothing Size")
            update_body_btn = gr.Button("Update Body Measurements")
            body_status = gr.Textbox(label="Status")
            
            update_body_btn.click(update_body_measurements, 
                                 inputs=[profile_username, body_type, skin_tone, eye_color, hair_color, height, weight, clothing_size], 
                                 outputs=body_status)
        
        with gr.Accordion("View Profile", open=True):
            view_profile_btn = gr.Button("View Profile")
            
            # Use a Row to display profile text and image side by side
            with gr.Row():
                # Left column for profile text
                with gr.Column(scale=2):
                    profile_text = gr.Textbox(label="Profile Information", lines=15)
                
                # Right column for profile image
                with gr.Column(scale=1):
                    profile_image = gr.Image(label="Profile Picture", height=300)
            
            view_profile_btn.click(display_profile, inputs=[profile_username], outputs=[profile_text, profile_image])


