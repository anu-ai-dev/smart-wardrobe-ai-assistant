import json
import os
import random
import gradio as gr
import requests
from datetime import datetime, timedelta, date
import colorsys

def geocode_location(location):
    """
    Geocodes a location string using the OpenStreetMap Nominatim API.

    Args:
        location (str): The location string to geocode.

    Returns:
        tuple: A tuple containing the latitude and longitude of the location,
               or (None, None) if the location cannot be geocoded.
    """
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={location}&format=jsonv2"
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        if data:
            latitude = float(data[0]["lat"])
            longitude = float(data[0]["lon"])
            return latitude, longitude
        else:
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"Error during geocoding request: {e}")
        return None, None
    except (KeyError, ValueError, IndexError) as e:
        print(f"Error processing geocoding response: {e}")
        return None, None

def get_real_time_location():
    """
    Retrieves the user's current location using the ipinfo.io API.

    Returns:
        str: The city and country of the user's current location,
             or None if the location cannot be determined.
    """
    try:
        url = "https://ipinfo.io08b1f19db9510c="  # Replace with your ipinfo.io token if needed
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        city = data.get("city")
        country = data.get("country")
        if city and country:
            return f"{city}, {country}"
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error during real-time location request: {e}")
        return None
    except (KeyError, TypeError) as e:
        print(f"Error processing real-time location response: {e}")
        return None
    
# Weather API key
WEATHER_API_KEY = "fbaf322ed08f82b7204d10fc531bf608"

# Load clothing recommendations from JSON
RECOMMENDATIONS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "clothing_recommendations.json")
try:
    with open(RECOMMENDATIONS_FILE, "r") as f:
        clothing_recommendations = json.load(f)
except FileNotFoundError:
    print(f"Warning: Recommendations file not found at {RECOMMENDATIONS_FILE}")
    clothing_recommendations = {}

# Weather data cache
weather_cache = {}
CACHE_EXPIRY = 30 * 60  # 30 minutes in seconds

# Outfit history tracking
outfit_history_file = "outfit_history.json"
try:
    with open(outfit_history_file, "r") as f:
        outfit_history = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    outfit_history = {}

# Saved outfits file
saved_outfits_file = "saved_outfits.json"
try:
    with open(saved_outfits_file, "r") as f:
        saved_outfits = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    saved_outfits = {}

# Special events calendar
events_calendar_file = "events_calendar.json"
try:
    with open(events_calendar_file, "r") as f:
        events_calendar = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    events_calendar = {}

# Feedback data
feedback_file = "outfit_feedback.json"
try:
    with open(feedback_file, "r") as f:
        outfit_feedback = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    outfit_feedback = {}

def save_outfit_history():
    """Save outfit history to file"""
    with open(outfit_history_file, "w") as f:
        json.dump(outfit_history, f, indent=4)

def save_saved_outfits():
    """Save user's saved outfits to file"""
    with open(saved_outfits_file, "w") as f:
        json.dump(saved_outfits, f, indent=4)

def save_events_calendar():
    """Save events calendar to file"""
    with open(events_calendar_file, "w") as f:
        json.dump(events_calendar, f, indent=4)

def save_outfit_feedback():
    """Save outfit feedback to file"""
    with open(feedback_file, "w") as f:
        json.dump(outfit_feedback, f, indent=4)

def get_cultural_context(location):
    """Determine cultural context based on location"""
    # Define regions and their associated countries/cities
    indian_locations = ["india", "mumbai", "delhi", "bangalore", "hyderabad", "chennai", "kolkata",
                        "jaipur", "ahmedabad", "pune", "lucknow", "kanpur", "nagpur", "indore", "thane"]
    
    middle_eastern_locations = ["uae", "dubai", "abu dhabi", "saudi arabia", "riyadh", "jeddah",
                               "qatar", "doha", "kuwait", "bahrain", "oman", "muscat"]
    
    east_asian_locations = ["china", "japan", "korea", "beijing", "shanghai", "tokyo", "seoul",
                           "hong kong", "taipei", "singapore", "kuala lumpur", "bangkok"]
    
    western_locations = ["usa", "uk", "canada", "australia", "new zealand", "germany", "france",
                        "italy", "spain", "london", "new york", "paris", "sydney", "toronto"]
    
    # Check location against regions
    location_lower = location.lower() if location else ""
    
    if any(loc in location_lower for loc in indian_locations):
        return "indian"
    elif any(loc in location_lower for loc in middle_eastern_locations):
        return "middle_eastern"
    elif any(loc in location_lower for loc in east_asian_locations):
        return "east_asian"
    elif any(loc in location_lower for loc in western_locations):
        return "western"
    else:
        return "generic"  # Default if no specific culture is identified

def get_temperature_category(temperature):
    """Categorize temperature as hot, normal, or cold"""
    if temperature > 28:  # Celsius
        return "hot"
    elif temperature < 15:
        return "cold"
    else:
        return "normal"

def get_season(location, date=None):
    """Determine the current season based on location and date"""
    if not date:
        date = datetime.now()
    
    month = date.month
    
    # Northern hemisphere seasons
    northern_locations = ["usa", "uk", "canada", "europe", "china", "japan", "korea", 
                         "india", "middle east", "russia", "mexico"]
    
    # Southern hemisphere seasons
    southern_locations = ["australia", "new zealand", "argentina", "brazil", "chile", 
                         "south africa", "uruguay", "paraguay"]
    
    location_lower = location.lower() if location else ""
    
    # Determine hemisphere
    is_southern = any(loc in location_lower for loc in southern_locations)
    
    # Define seasons based on hemisphere
    if is_southern:
        # Southern hemisphere
        if 3 <= month <= 5:
            return "autumn"
        elif 6 <= month <= 8:
            return "winter"
        elif 9 <= month <= 11:
            return "spring"
        else:
            return "summer"
    else:
        # Northern hemisphere (default)
        if 3 <= month <= 5:
            return "spring"
        elif 6 <= month <= 8:
            return "summer"
        elif 9 <= month <= 11:
            return "autumn"
        else:
            return "winter"

def get_user_gender(username):
    """Get user gender from profile or return default"""
    try:
        # Try to load user profile data
        with open("user_profiles.json", "r") as f:
            user_profiles = json.load(f)
            if username in user_profiles and "gender" in user_profiles[username]:
                return user_profiles[username]["gender"].lower()
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        pass
    
    # If we can't determine gender, check wardrobe data for clues
    try:
        with open("wardrobe_data.json", "r") as f:
            wardrobe_data = json.load(f)
            if username in wardrobe_data:
                # Look for gender-specific categories that might indicate gender
                items = wardrobe_data[username].get("clothing_items", [])
                for item in items:
                    if "category" in item:
                        if item["category"] in ["Men's Shirts", "Men's Pants"]:
                            return "male"
                        elif item["category"] in ["Women's Dresses", "Women's Blouses"]:
                            return "female"
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    
    return "neutral"  # Changed from "other" to "neutral" for better recommendations

def get_generic_outfit_recommendations(occasion, weather_condition, temperature, username, location=""):
    """Generate outfit recommendations based on JSON data"""
    gender = get_user_gender(username)
    cultural_context = get_cultural_context(location)
    temp_category = get_temperature_category(temperature)
    season = get_season(location)
    
    # Occasion-specific default recommendations
    occasion_defaults = {
        "interview": {
            "top": "Professional button-up shirt or blouse",
            "bottom": "Formal trousers or skirt",
            "shoes": "Polished formal shoes",
            "accessory": "Minimal professional accessories"
        },
        "formal": {
            "top": "Formal shirt or blouse",
            "bottom": "Formal trousers or skirt",
            "shoes": "Formal dress shoes",
            "accessory": "Elegant formal accessories"
        },
        "casual": {
            "top": "Comfortable casual top",
            "bottom": "Casual pants or shorts",
            "shoes": "Casual footwear",
            "accessory": "Simple casual accessories"
        },
        "work": {
            "top": "Professional work-appropriate top",
            "bottom": "Professional work-appropriate bottom",
            "shoes": "Comfortable professional footwear",
            "accessory": "Simple professional accessories"
        },
        "wedding": {
            "top": "Formal wedding-appropriate top",
            "bottom": "Formal wedding-appropriate bottom",
            "shoes": "Formal dress shoes",
            "accessory": "Elegant wedding-appropriate accessories"
        },
        "party": {
            "top": "Stylish party top",
            "bottom": "Fashionable party bottom",
            "shoes": "Stylish party footwear",
            "accessory": "Trendy party accessories"
        },
        "beach": {
            "top": "Light breathable beach top",
            "bottom": "Comfortable beach shorts or skirt",
            "shoes": "Sandals or flip-flops",
            "accessory": "Beach hat and sunglasses"
        }
    }
    
    # Default recommendations in case we don't find a match
    default_recommendations = occasion_defaults.get(
        occasion.lower(),
        {
            "top": "Appropriate top for the occasion",
            "bottom": "Appropriate bottom for the occasion",
            "shoes": "Comfortable footwear suitable for the occasion",
            "accessory": "Suitable accessories for the occasion"
        }
    )
    
    # Adjust for temperature
    if temp_category == "hot":
        for key in default_recommendations:
            if key == "top":
                default_recommendations[key] = "Light breathable " + default_recommendations[key].split(" ", 1)[1]
            elif key == "bottom":
                default_recommendations[key] = "Light breathable " + default_recommendations[key].split(" ", 1)[1]
    elif temp_category == "cold":
        for key in default_recommendations:
            if key == "top":
                default_recommendations[key] = "Warm layered " + default_recommendations[key].split(" ", 1)[1]
            elif key == "bottom":
                default_recommendations[key] = "Warm " + default_recommendations[key].split(" ", 1)[1]
    
    # Adjust for season
    seasonal_adjustments = {
        "spring": {
            "top": "Spring-appropriate ",
            "bottom": "Spring-appropriate ",
            "accessory": "Spring-themed "
        },
        "summer": {
            "top": "Summer-friendly ",
            "bottom": "Summer-friendly ",
            "accessory": "Summer-themed "
        },
        "autumn": {
            "top": "Fall-appropriate ",
            "bottom": "Fall-appropriate ",
            "accessory": "Fall-themed "
        },
        "winter": {
            "top": "Winter-ready ",
            "bottom": "Winter-ready ",
            "accessory": "Winter-themed "
        }
    }
    
    # Apply seasonal adjustments if they don't conflict with temperature
    if season in seasonal_adjustments:
        for key, prefix in seasonal_adjustments[season].items():
            # Only apply if it doesn't already have a temperature adjustment
            if not (temp_category == "hot" and "Light breathable" in default_recommendations[key]) and \
               not (temp_category == "cold" and "Warm" in default_recommendations[key]):
                default_recommendations[key] = prefix + default_recommendations[key]
    
    # Try to find the most specific recommendation from JSON data
    try:
        # First check if we have the specific occasion
        if occasion.lower() in clothing_recommendations:
            occasion_recs = clothing_recommendations[occasion.lower()]
            
            # Check for cultural context
            if cultural_context in occasion_recs:
                culture_recs = occasion_recs[cultural_context]
            else:
                culture_recs = occasion_recs.get("generic", {})
            
            # Check for gender
            if gender in culture_recs:
                gender_recs = culture_recs[gender]
            else:
                gender_recs = culture_recs.get("neutral", culture_recs.get("other", {}))
            
            # Check for temperature category
            if temp_category in gender_recs:
                return gender_recs[temp_category]
            else:
                # If specific temperature not found, use normal
                return gender_recs.get("normal", default_recommendations)
        
        # If we don't have the specific occasion, fall back to defaults
        return default_recommendations
    
    except (KeyError, TypeError) as e:
        print(f"Error finding recommendation: {e}")
    
    # If all else fails, return default recommendations
    return default_recommendations

def recommend_outfit(username, occasion, location, weather_data):
    """Main function to recommend outfits based on occasion and weather"""
    # Extract weather data
    weather_condition = weather_data.get("weather", [{}])[0].get("main", "Clear")
    temperature = weather_data.get("main", {}).get("temp", 22)  # Default to 22°C if not available
    
    # Get user's wardrobe items
    user_items = get_user_wardrobe_items(username)
    
    # Filter items by occasion
    occasion_items = filter_items_by_occasion(user_items, occasion)
    
    # Check outfit history to avoid recent repeats
    filtered_items = avoid_recent_outfits(username, occasion_items)
    
    # If no items found for the occasion, provide generic recommendations
    if not filtered_items:
        generic_outfit = get_generic_outfit_recommendations(occasion, weather_condition, temperature, username, location)
        
        # Format the response
        response = {
            "outfit": generic_outfit,
            "message": f"We don't see items tagged for {occasion} in your wardrobe, but here's what we recommend:",
            "weather_info": f"🌤 Weather in {location}: {weather_condition}, {temperature}°C",
            "is_generic": True,
            "occasion": occasion
        }
        
        # Add weather-specific advice
        if temperature > 28:
            response["weather_advice"] = "☀️ It's hot. Wear light, breathable fabrics."
        elif temperature < 15:
            response["weather_advice"] = "❄️ It's cold. Layer up and stay warm."
        else:
            response["weather_advice"] = "🌡️ The temperature is moderate. Dress comfortably."
        
        # Add seasonal advice
        season = get_season(location)
        response["season_info"] = f"🍂 Current season in {location}: {season.capitalize()}"
        
        return response
    
    # If we have items for the occasion, create a personalized outfit
    else:
        # Logic to select appropriate items based on weather and occasion
        selected_outfit = select_items_for_weather(filtered_items, weather_condition, temperature, username)
        
        # Check if we have all necessary categories
        missing_categories = check_missing_categories(selected_outfit)
        
        if not missing_categories:
            # We have a complete outfit
            # Record this outfit in history
            record_outfit_history(username, selected_outfit, occasion)
            
            # Get season information
            season = get_season(location)
            
            return {
                                "outfit": selected_outfit,
                "message": f"Here's your personalized outfit for {occasion}:",
                "weather_info": f"🌤 Weather in {location}: {weather_condition}, {temperature}°C",
                "season_info": f"🍂 Current season in {location}: {season.capitalize()}",
                "is_generic": False,
                "occasion": occasion
            }
        elif len(missing_categories) >= 3:  # All three main categories are missing
            # Fall back to generic recommendations
            generic_outfit = get_generic_outfit_recommendations(occasion, weather_condition, temperature, username, location)
            shopping_recommendations = get_shopping_recommendations(missing_categories, weather_condition, temperature, occasion, username)
            
            # Get season information
            season = get_season(location)
            
            return {
                "outfit": generic_outfit,
                "message": f"We don't have enough items in your wardrobe for a complete {occasion} outfit. Here's what we recommend:",
                "weather_info": f"🌤 Weather in {location}: {weather_condition}, {temperature}°C",
                "season_info": f"🍂 Current season in {location}: {season.capitalize()}",
                "shopping_recommendations": shopping_recommendations,
                "is_generic": True,
                "occasion": occasion
            }
        else:
            # We have some items but not all - combine with generic recommendations
            combined_outfit = combine_with_generic(selected_outfit, missing_categories, occasion, weather_condition, temperature, username, location)
            
            # Record this outfit in history
            record_outfit_history(username, combined_outfit, occasion)
            
            # Get season information
            season = get_season(location)
            
            return {
                "outfit": combined_outfit,
                "message": f"Here's your outfit for {occasion}, with some recommendations for missing items:",
                "weather_info": f"🌤 Weather in {location}: {weather_condition}, {temperature}°C",
                "season_info": f"🍂 Current season in {location}: {season.capitalize()}",
                "missing_categories": missing_categories,
                "is_generic": False,
                "occasion": occasion
            }

def record_outfit_history(username, outfit, occasion):
    """Record an outfit in the user's history"""
    if username not in outfit_history:
        outfit_history[username] = []
    
    try:
        # Create a simplified version of the outfit for history
        outfit_record = {
            "date": datetime.now().isoformat(),
            "occasion": occasion,
            "items": {}
        }
        
        for category, item in outfit.items():
            if isinstance(item, dict):
                outfit_record["items"][category] = {
                    "item_name": item.get("item_name", "Unknown"),
                    "id": item.get("id", None)
                }
            else:
                outfit_record["items"][category] = {
                    "item_name": item,
                    "is_recommendation": True
                }
        
        # Add to history
        outfit_history[username].append(outfit_record)
        
        # Limit history to last 30 outfits
        if len(outfit_history[username]) > 30:
            outfit_history[username] = outfit_history[username][-30:]
        
        # Save to file
        save_outfit_history()
    except Exception as e:
        print(f"Error recording outfit history: {e}")
        # Continue without recording history if there's an error

# Fix the avoid_recent_outfits function to handle date errors
def avoid_recent_outfits(username, items):
    """Filter out items that were recently used in outfits"""
    if not username in outfit_history or not outfit_history[username]:
        return items
    
    try:
        # Get items used in the last 7 days
        recent_date = datetime.now() - timedelta(days=7)
        recent_outfits = []
        
        for outfit in outfit_history[username]:
            try:
                outfit_date = datetime.fromisoformat(outfit["date"])
                if outfit_date > recent_date:
                    recent_outfits.append(outfit)
            except (ValueError, TypeError, KeyError):
                # Skip outfits with invalid dates
                continue
        
        # Extract item IDs from recent outfits
        recent_item_ids = set()
        for outfit in recent_outfits:
            for category, item_info in outfit["items"].items():
                if not item_info.get("is_recommendation", False) and item_info.get("id"):
                    recent_item_ids.add(item_info["id"])
        
        # Filter out recently used items, but ensure we have at least some items left
        filtered_items = [item for item in items if item.get("id") not in recent_item_ids]
        
        # If filtering removed too many items, return at least half of the original items
        if len(filtered_items) < len(items) / 2:
            return items
        
        return filtered_items
    except Exception as e:
        print(f"Error filtering recent outfits: {e}")
        # Return original items if there's an error
        return items

def save_outfit(username, outfit, occasion, name=None):
    """Save an outfit to the user's saved outfits"""
    if username not in saved_outfits:
        saved_outfits[username] = []
    
    # Create a record of the outfit
    outfit_record = {
        "date_saved": datetime.now().isoformat(),
        "name": name or f"{occasion} outfit {len(saved_outfits[username]) + 1}",
        "occasion": occasion,
        "items": {}
    }
    
    for category, item in outfit.items():
        if isinstance(item, dict):
            outfit_record["items"][category] = {
                "item_name": item.get("item_name", "Unknown"),
                "id": item.get("id", None)
            }
        else:
            outfit_record["items"][category] = {
                "item_name": item,
                "is_recommendation": True
            }
    
    # Add to saved outfits
    saved_outfits[username].append(outfit_record)
    
    # Save to file
    save_saved_outfits()
    
    return f"Outfit saved as '{outfit_record['name']}'"

def add_event(username, event_name, date, occasion, location=None):
    """Add an event to the user's calendar"""
    if username not in events_calendar:
        events_calendar[username] = []
    
    # Create event record
    event = {
        "name": event_name,
        "date": date,
        "occasion": occasion,
        "location": location,
        "outfit_recommended": False
    }
    
    # Add to calendar
    events_calendar[username].append(event)
    
    # Save to file
    save_events_calendar()
    
    return f"Event '{event_name}' added to calendar for {date}"

# Fix for the date error in the recommend_outfit function
def check_upcoming_events(username):
    """Check for upcoming events and return notifications"""
    if username not in events_calendar:
        return []
    
    notifications = []
    now = datetime.now()
    
    for event in events_calendar[username]:
        try:
            # Handle both string dates and datetime objects
            if isinstance(event["date"], str):
                # Try to parse the date string
                event_date = datetime.fromisoformat(event["date"].replace('Z', '+00:00'))
            else:
                event_date = event["date"]
                
            days_until = (event_date - now).days
            
            # Notify about events in the next 3 days
            if 0 <= days_until <= 3 and not event.get("outfit_recommended", False):
                notifications.append({
                    "message": f"Upcoming event: {event['name']} on {event_date.strftime('%Y-%m-%d')}",
                    "event": event
                })
                event["outfit_recommended"] = True
        except (ValueError, TypeError, KeyError) as e:
            # Handle date parsing errors gracefully
            print(f"Error processing event date: {e}")
            continue
    
    # Save updated event status
    save_events_calendar()
    
    return notifications

def record_feedback(username, outfit, rating, comments=None):
    """Record user feedback on an outfit recommendation"""
    if username not in outfit_feedback:
        outfit_feedback[username] = []
    
    # Create feedback record
    feedback = {
        "date": datetime.now().isoformat(),
        "rating": rating,  # 1-5 or thumbs up/down
        "comments": comments,
        "outfit": outfit
    }
    
    # Add to feedback
    outfit_feedback[username].append(feedback)
    
    # Save to file
    save_outfit_feedback()
    
    return "Thank you for your feedback!"

# Helper functions for the main recommendation logic
def get_user_wardrobe_items(username):
    """Get user's wardrobe items from database"""
    # This would fetch from your wardrobe_data.json or database
    try:
        with open("wardrobe_data.json", "r") as f:
            wardrobe_data = json.load(f)
            return wardrobe_data.get(username, {}).get("clothing_items", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def filter_items_by_occasion(items, occasion):
    """Filter wardrobe items by occasion"""
    return [item for item in items if item.get("occasion", "").lower() == occasion.lower()]

def select_items_for_weather(occasion_items, weather_condition, temperature, username):
    """Select appropriate items based on weather, prioritizing favorite items"""
    selected_outfit = {
        "top": None,
        "bottom": None,
        "shoes": None,
        "accessory": None
    }
    
    # Group items by category
    categorized_items = {
        "top": [],
        "bottom": [],
        "shoes": [],
        "accessory": []
    }
    
    # Map wardrobe categories to outfit categories
    category_mapping = {
        "Tops": "top",
        "Bottoms": "bottom",
        "Shoes": "shoes",
        "Accessories": "accessory",
        "Dresses": "top",  # Dresses can count as both top and bottom
        "Outerwear": "top",
        "Jewelry": "accessory",
        "Sportswear": "top",  # Simplified mapping
        "Sleepwear": "top",   # Simplified mapping
    }
    
    # Categorize items
    for item in occasion_items:
        wardrobe_category = item.get("category", "")
        outfit_category = category_mapping.get(wardrobe_category)
        
        if outfit_category:
            categorized_items[outfit_category].append(item)
            # Special case for dresses - they count as both top and bottom
            if wardrobe_category == "Dresses":
                categorized_items["bottom"].append(item)
    
    # Select one item from each category, considering weather and favorites
    for category in selected_outfit:
        items = categorized_items[category]
        if items:
            # First, filter by weather appropriateness
            if weather_condition in ["Rain", "Thunderstorm", "Drizzle"]:
                weather_appropriate = [i for i in items if i.get("material") not in ["Suede", "Silk"]]
                if weather_appropriate:
                    items = weather_appropriate
            
            # Then prioritize favorite items
            favorite_items = [i for i in items if i.get("favorite", False)]
            if favorite_items:
                selected_outfit[category] = random.choice(favorite_items)
            else:
                selected_outfit[category] = random.choice(items)
    
    # Check for color harmony
    ensure_color_harmony(selected_outfit)
    
    # Check for style consistency
    ensure_style_consistency(selected_outfit)
    
    return selected_outfit

def ensure_color_harmony(outfit):
    """Ensure colors in the outfit are harmonious"""
    # Extract colors from items
    colors = []
    for category, item in outfit.items():
        if isinstance(item, dict) and "color" in item:
            if isinstance(item["color"], list):
                colors.extend(item["color"])
            else:
                colors.append(item["color"])
    
    # If we don't have enough colors to check harmony, return
    if len(colors) < 2:
        return
    
    # Convert colors to HSV for harmony checking
    color_hsv = []
    for color in colors:
        if color.lower() == "black":
            continue  # Black goes with everything
        if color.lower() == "white":
            continue  # White goes with everything
        
        # Map color names to approximate HSV values
        color_map = {
            "red": (0, 1, 1),
            "blue": (240/360, 1, 1),
            "green": (120/360, 1, 1),
            "yellow": (60/360, 1, 1),
            "purple": (270/360, 1, 1),
            "orange": (30/360, 1, 1),
            "pink": (330/360, 0.7, 1),
            "brown": (30/360, 0.8, 0.5),
            "grey": (0, 0, 0.5),
            "beige": (30/360, 0.2, 0.9)
        }
        
        if color.lower() in color_map:
            color_hsv.append(color_map[color.lower()])
    
    # Check for clashing colors (colors opposite on color wheel)
    # This is a simplified check - a real implementation would be more sophisticated
    for i in range(len(color_hsv)):
        for j in range(i+1, len(color_hsv)):
            h1 = color_hsv[i][0]
            h2 = color_hsv[j][0]
            
            # Check if colors are approximately opposite (difference around 0.5)
            if 0.4 < abs(h1 - h2) < 0.6:
                # Colors might clash, try to replace one item
                for category, item in outfit.items():
                    if isinstance(item, dict) and "color" in item:
                        if any(c.lower() == colors[i].lower() for c in item["color"]):
                            # Try to find a replacement
                            # In a real implementation, you would replace the item
                            # For now, we'll just note the clash
                            print(f"Color clash detected: {colors[i]} and {colors[j]}")
                            break

def ensure_style_consistency(outfit):
    """Ensure styles in the outfit are consistent"""
    # Extract styles from items
    styles = []
    for category, item in outfit.items():
        if isinstance(item, dict) and "style" in item:
            styles.append(item["style"])
    
    # If we don't have enough styles to check consistency, return
    if len(styles) < 2:
        return
    
    # Define style groups that work well together
    style_groups = [
        ["Modern", "Minimalist", "Chic"],
        ["Classic", "Preppy", "Formal"],
        ["Bohemian", "Vintage", "Artistic"],
        ["Streetwear", "Athleisure", "Casual"],
        ["Trendy", "Chic", "Modern"]
    ]
    
    # Check if styles are from different incompatible groups
    for i in range(len(styles)):
        for j in range(i+1, len(styles)):
            style1 = styles[i]
            style2 = styles[j]
            
            # Check if styles are in the same group
            compatible = False
            for group in style_groups:
                if style1 in group and style2 in group:
                    compatible = True
                    break
            
            if not compatible:
                # Styles might clash, try to replace one item
                # In a real implementation, you would replace the item
                # For now, we'll just note the clash
                print(f"Style inconsistency detected: {style1} and {style2}")

def check_missing_categories(outfit):
    """Check which categories are missing from the outfit"""
    return [category for category, item in outfit.items() if item is None]

def get_shopping_recommendations(missing_categories, weather_condition, temperature, occasion, username):
    """Generate shopping recommendations for missing categories"""
    recommendations = {}
    generic_outfit = get_generic_outfit_recommendations(occasion, weather_condition, temperature, username)
    
    # Popular brands for different categories
        # Popular brands for different categories
    brand_suggestions = {
        "top": ["Zara", "H&M", "Uniqlo", "Gap"],
        "bottom": ["Levi's", "Zara", "H&M", "Uniqlo"],
        "shoes": ["Nike", "Adidas", "Clarks", "Aldo"],
        "accessory": ["Fossil", "Swarovski", "Pandora", "Tiffany & Co."]
    }
    
    for category in missing_categories:
        base_recommendation = generic_outfit.get(category, "Item appropriate for the occasion")
        brands = ", ".join(random.sample(brand_suggestions.get(category, ["Various brands"]),
                                         min(2, len(brand_suggestions.get(category, [])))))
        recommendations[category] = f"{base_recommendation} (Suggested brands: {brands})"
    
    return recommendations

def combine_with_generic(selected_outfit, missing_categories, occasion, weather_condition, temperature, username, location):
    """Combine existing items with generic recommendations for missing categories"""
    generic_outfit = get_generic_outfit_recommendations(occasion, weather_condition, temperature, username, location)
    
    combined_outfit = selected_outfit.copy()
    for category in missing_categories:
        combined_outfit[category] = generic_outfit.get(category, "Item appropriate for the occasion")
    
    return combined_outfit

# Function to format the outfit recommendation for display
def format_outfit_recommendation(recommendation):
    """Format the outfit recommendation for display"""
    outfit = recommendation["outfit"]
    message = recommendation["message"]
    weather_info = recommendation["weather_info"]
    weather_advice = recommendation.get("weather_advice", "")
    season_info = recommendation.get("season_info", "")
    is_generic = recommendation.get("is_generic", False)
    occasion = recommendation.get('occasion', 'Today')
    
    formatted_output = f"👗 Recommended Outfit for {occasion}:\n"
    formatted_output += f"{weather_info}\n"
    
    if season_info:
        formatted_output += f"{season_info}\n"
    
    if weather_advice:
        formatted_output += f"{weather_advice}\n"
    
    formatted_output += f"{message}\n"
    
    # Format outfit items
    for category, item in outfit.items():
        if isinstance(item, dict):  # This is an actual wardrobe item
            favorite_star = "⭐ " if item.get("favorite", False) else ""
            formatted_output += f"- {favorite_star}{item.get('item_name', 'Unknown')} ({category})\n"
        else:  # This is a recommendation string
            # Remove any mentions of gender
            item_text = item.replace("for your gender expression", "").replace("appropriate for your gender", "")
            formatted_output += f"- {item_text} ({category}) 🛍️ [Consider purchasing]\n"
    
    # Add shopping or tip message if generic
    if is_generic:
        formatted_output += f"\n💡 Tip: Add items with the occasion '{occasion}' to your wardrobe for personalized recommendations."
        formatted_output += f"\n🛍️ Shopping suggestion: Consider purchasing the items listed above to complete your {occasion} wardrobe."
    
    # Add feedback and save options
    formatted_output += "\n\n📋 Options: Use the buttons below to save this outfit or provide feedback."
    
    return formatted_output

# Real weather API function with caching
def get_weather_data(location):
    """Get real weather data for a location using OpenWeatherMap API with caching"""
    if not location.strip():
        # Return default weather data if location is empty
        return {
            "weather": [{"main": "Clear"}],
            "main": {"temp": 22, "humidity": 50},
            "wind": {"speed": 10}
        }
    
    # Check cache first
    cache_key = location.lower()
    current_time = datetime.now().timestamp()
    
    if cache_key in weather_cache:
        cache_time, cache_data = weather_cache[cache_key]
        # If cache is still valid (less than 30 minutes old)
        if current_time - cache_time < CACHE_EXPIRY:
            return cache_data
    
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        
        if response.status_code != 200:
            # Return default weather data if API call fails
            print(f"Weather API error: {response.status_code} - {response.text}")
            default_data = {
                "weather": [{"main": "Clear"}],
                "main": {"temp": 22, "humidity": 50},
                "wind": {"speed": 10}
            }
            # Cache the default data too to avoid repeated failed calls
            weather_cache[cache_key] = (current_time, default_data)
            return default_data
        
        # Get the weather data from the API
        weather_data = response.json()
        
        # Cache the data
        weather_cache[cache_key] = (current_time, weather_data)
        
        # Return the full weather data
        return weather_data
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        # Return default weather data if API call fails
        default_data = {
            "weather": [{"main": "Clear"}],
            "main": {"temp": 22, "humidity": 50},
            "wind": {"speed": 10}
        }
        # Cache the default data too to avoid repeated failed calls
        weather_cache[cache_key] = (current_time, default_data)
        return default_data

def generate_outfit_name(outfit, occasion, weather_condition=None, location=None):
    """
    Generate a descriptive name for an outfit based on its components and context
    
    Args:
        outfit: Dictionary containing outfit items
        occasion: String representing the occasion
        weather_condition: Optional weather condition string
        location: Optional location string for season determination
    
    Returns:
        A descriptive outfit name string
    """
    # Get current date for timestamp
    current_date = datetime.now()
    month_name = current_date.strftime("%B")
    year = current_date.strftime("%Y")
    
    # Determine season if location is provided
    season = ""
    if location:
        season = get_season(location).capitalize()
    
    # Extract key items from the outfit
    key_items = []
    color_adjectives = []
    
    # Look for distinctive items and colors
    for category, item in outfit.items():
        if isinstance(item, dict):
            # Extract color information
            if "color" in item and item["color"]:
                if isinstance(item["color"], list) and item["color"]:
                    color = item["color"][0]  # Take first color if multiple
                else:
                    color = item["color"]
                
                if color and color not in color_adjectives:
                    color_adjectives.append(color)
            
            # Extract item name
            if "item_name" in item and item["item_name"]:
                # Only add distinctive items (typically bottoms and tops are most distinctive)
                if category in ["top", "bottom"] or item.get("favorite", False):
                    key_items.append(item["item_name"])
    
    # Build the name components
    name_parts = []
    
    # Add color if available
    if color_adjectives and len(color_adjectives) <= 2:  # Limit to 2 colors for brevity
        name_parts.append(" & ".join(color_adjectives))
    
    # Add a key item if available (limit to one key item for brevity)
    if key_items:
        name_parts.append(key_items[0])
    
    # Add weather condition if available
    weather_part = ""
    if weather_condition:
        if isinstance(weather_condition, str):
            weather_part = weather_condition
        elif isinstance(weather_condition, dict) and "main" in weather_condition:
            weather_part = weather_condition["main"]
        
        if weather_part in ["Rain", "Thunderstorm", "Drizzle"]:
            name_parts.append("Rainy Day")
        elif weather_part in ["Snow", "Blizzard"]:
            name_parts.append("Snowy")
        elif weather_part == "Clear" and season.lower() in ["summer", "spring"]:
            name_parts.append("Sunny")
    
    # Add season if available and not already covered by weather
    if season and "Rainy" not in " ".join(name_parts) and "Snowy" not in " ".join(name_parts):
        name_parts.append(season)
    
    # Add occasion
    name_parts.append(occasion.capitalize())
    
    # Combine all parts
    base_name = " ".join(name_parts)
    
    # Add date element
    final_name = f"{base_name} - {month_name} {year}"
    
    return final_name




# Gradio UI function for outfit recommendations
def gradio_recommend_outfit(username, occasion, location):
    """Gradio interface function for outfit recommendations"""
    if not username or not occasion or not location:
        return "Please fill in all fields: username, occasion, and location.", "" # Return empty string for outfit_name

    try:
        # Get weather data
        weather_data = get_weather_data(location)

        # Get outfit recommendation
        recommendation = recommend_outfit(username, occasion, location, weather_data)

        # Format the recommendation for display
        formatted_recommendation = format_outfit_recommendation(recommendation)

        # Generate outfit name
        outfit = recommendation["outfit"]
        weather_condition = weather_data.get("weather", [{}])[0].get("main", "Clear")
        outfit_name = generate_outfit_name(outfit, occasion, weather_condition, location)

        return formatted_recommendation, outfit_name # Return both the formatted recommendation and the outfit name

    except Exception as e:
        error_message = f"Error generating outfit recommendation: {str(e)}"
        print(f"Detailed error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return f"Sorry, we encountered an error while generating your outfit recommendation. Please try again later.\n\nError details: {error_message}", "" # Return empty string for outfit_name


# Function to save an outfit from the UI
def gradio_save_outfit(username, recommendation_text, outfit_name=None):
    """Save an outfit from the Gradio UI"""
    if not username or not recommendation_text:
        return "Missing username or outfit information."
    
    # Extract occasion from the recommendation text
    occasion_match = recommendation_text.split("Recommended Outfit for ", 1)
    if len(occasion_match) > 1:
        occasion = occasion_match[1].split(":", 1)[0].strip()
    else:
        occasion = "Custom"
    
    # Extract weather information if available
    weather_condition = None
    location = None
    weather_match = recommendation_text.split("Weather in ", 1)
    if len(weather_match) > 1:
        location_weather = weather_match[1].split(":", 1)[0].strip()
        location = location_weather
        
        if ":" in weather_match[1]:
            weather_info = weather_match[1].split(":", 1)[1].strip()
            weather_condition = weather_info.split(",")[0].strip()
    
    # Parse the outfit items from the recommendation text
    outfit = {}
    lines = recommendation_text.split("\n")
    for line in lines:
        if line.startswith("- "):
            item_text = line[2:]  # Remove the "- " prefix
            
            # Extract category from parentheses
            if "(" in item_text and ")" in item_text:
                category = item_text.split("(")[-1].split(")")[0].strip().lower()
                item_name = item_text.split("(")[0].strip()
                
                # Remove favorite star if present
                if item_name.startswith("⭐ "):
                    item_name = item_name[2:].strip()
                    is_favorite = True
                else:
                    is_favorite = False
                
                # Create item dictionary
                outfit[category] = {
                    "item_name": item_name,
                    "favorite": is_favorite
                }
                
                # Add color if it can be detected from the item name
                common_colors = ["red", "blue", "green", "black", "white", "yellow", "pink", 
                                "purple", "orange", "brown", "grey", "gray", "beige"]
                for color in common_colors:
                    if color in item_name.lower():
                        outfit[category]["color"] = color.capitalize()
                        break
    
    # Generate a descriptive name if not provided
    if not outfit_name:
        outfit_name = generate_outfit_name(outfit, occasion, weather_condition, location)
    
    # Save the outfit
    result = save_outfit(username, outfit, occasion, outfit_name)
    
    return f"Outfit saved as '{outfit_name}'"


# Function to provide feedback on an outfit
def gradio_provide_feedback(username, recommendation_text, rating, comments):
    """Provide feedback on an outfit from the Gradio UI"""
    if not username or not recommendation_text:
        return "Missing username or outfit information."
    
    # Extract occasion from the recommendation text
    occasion_match = recommendation_text.split("Recommended Outfit for ", 1)
    if len(occasion_match) > 1:
        occasion = occasion_match[1].split(":", 1)[0].strip()
    else:
        occasion = "Custom"
    
    # Create a simplified outfit record
    outfit = {
        "occasion": occasion,
        "recommendation_text": recommendation_text
    }
    
    # Record the feedback
    result = record_feedback(username, outfit, rating, comments)
    
    return result

def add_event_to_calendar(username, event_name, year, month, day, event_occasion, event_location):
        if not username or not event_name or not year or not month or not day or not event_occasion:
            return "Please fill in all required fields: username, event name, date, and occasion."
        
        try:
            # Convert separate date components to ISO format string
            month_num = months.index(month) + 1
            event_date = datetime(int(year), month_num, int(day)).isoformat()
            
            result = add_event(username, event_name, event_date, event_occasion, event_location)
            return result
        except Exception as e:
            return f"Error adding event: {str(e)}"
    
    # Function to display the calendar with events
def display_calendar(username):
    if not username:
        return "Please enter a username to view the calendar."

    try:
        if username not in events_calendar:
            return "<p>No events found for this user.</p>"

        # Get current date and calculate start of month
        today = date.today()

        # Generate HTML for upcoming events list view (simpler approach)
        html = f"""
        <div style="font-family: Arial, sans-serif;">
            <h3>Upcoming Events for {username}</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Date</th>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Event</th>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Occasion</th>
                    <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Location</th>
                </tr>
        """

        # Add list of upcoming events
        upcoming_events = []
        for event in events_calendar[username]:
            try:
                event_date = datetime.fromisoformat(event["date"].replace('Z', '+00:00'))
                if event_date >= datetime.now():
                    upcoming_events.append((event_date, event))
            except (ValueError, TypeError, KeyError):
                continue

        # Sort events by date
        upcoming_events.sort(key=lambda x: x[0])

        # Display upcoming events
        if upcoming_events:
            for event_date, event in upcoming_events:
                formatted_date = event_date.strftime("%A, %B %d, %Y")
                location = event.get("location", "")
                google_maps_link = ""
                if location:
                    # Create Google Maps link
                    google_maps_link = f'<a href="https://www.google.com/maps/search/?api=1&query={location}" target="_blank">{location}</a>'
                else:
                    google_maps_link = "No location provided"

                html += f"""
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">{formatted_date}</td>
                    <td style="border: 1px solid #ddd; padding: 8px;"><strong>{event["name"]}</strong></td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{event["occasion"]}</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{google_maps_link}</td>
                </tr>
                """
        else:
            html += """
            <tr>
                <td colspan="4" style="border: 1px solid #ddd; padding: 8px; text-align: center;">No upcoming events</td>
            </tr>
            """

        html += """
            </table>
        </div>
        """

        return html
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"<p>Error displaying calendar: {str(e)}</p>"
 


with gr.Blocks(title="Smart Wardrobe - Weather-Based Outfit Recommendations") as outfit_recommendation_interface:
    gr.Markdown("# 👗 Weather-Based Outfit Recommendations")
    gr.Markdown("Get personalized outfit recommendations based on the occasion, location, and current weather.")

    with gr.Row():
        with gr.Column(scale=1):
            username = gr.Textbox(label="Username", placeholder="Enter your username")
            occasion = gr.Dropdown(
                ["Casual", "Formal", "Party", "Work", "Wedding", "Interview", "Travel",
                 "Festival", "Beach", "Night Out", "Religious Event", "Date", "Business",
                 "Gym", "Brunch", "Outdoor Adventure"],
                label="Occasion"
            )
            location = gr.Textbox(label="Location", placeholder="Enter city or country")

            recommend_btn = gr.Button("Get Outfit Recommendation", variant="primary")

        with gr.Column(scale=2):
            recommendation_output = gr.Textbox(
                label="Your Outfit Recommendation",
                placeholder="Outfit recommendations will appear here...",
                lines=15
            )


    # Reduced examples for quick testing - just 3 common scenarios
    gr.Examples(
        examples=[
            ["user123", "Casual", "New York"],
            ["user123", "Work", "London"],
            ["user123", "Party", "Tokyo"]
        ],
        inputs=[username, occasion, location]
    )

    # Add feedback and save outfit options
    with gr.Row():
        with gr.Column():
            outfit_name = gr.Textbox(label="Outfit Name", placeholder="Enter a name for this outfit") # Moved outfit_name definition above
            with gr.Row(): # Added a nested row
             save_btn = gr.Button("Save This Outfit")
            save_output = gr.Textbox(label="Save Status", visible=True)

        with gr.Column():
            rating = gr.Radio(["👍 Like", "👎 Dislike"], label="Rate this outfit")
            feedback_text = gr.Textbox(label="Comments (optional)", placeholder="Tell us what you think...")
            feedback_btn = gr.Button("Submit Feedback")
            feedback_output = gr.Textbox(label="Feedback Status")

    # Set up save and feedback button events
    save_btn.click(
        fn=gradio_save_outfit,
        inputs=[username, recommendation_output, outfit_name],
        outputs=save_output
    )

    feedback_btn.click(
        fn=gradio_provide_feedback,
        inputs=[username, recommendation_output, rating, feedback_text],
        outputs=feedback_output
    )

    # Set up the recommendation button click event
    recommend_btn.click(
        fn=gradio_recommend_outfit,
        inputs=[username, occasion, location],
        outputs=[recommendation_output, outfit_name] # Modified outputs
    )

    # Also trigger recommendations when pressing Enter in the location field
    location.submit(
        fn=gradio_recommend_outfit,
        inputs=[username, occasion, location],
        outputs=[recommendation_output, outfit_name] # Modified outputs
    )
    # More concise "How it works" section
    with gr.Accordion("How it works", open=False):
        gr.Markdown("""
        ## How it works

            Our system combines your wardrobe data with real-time weather information to suggest appropriate outfits.
        We consider:

            • Current weather at your location
            • Cultural norms for different regions
            • Items in your wardrobe tagged for the occasion

            **Tip:** Add items to your wardrobe with occasion tags for personalized recommendations.
        """)
    # Add upcoming events with calendar functionality
    with gr.Accordion("Upcoming Events & Calendar", open=False):
        gr.Markdown("### 📅 Event Calendar")

        # Use separate components for date selection instead of Datepicker
        current_year = datetime.now().year
        years = list(range(current_year, current_year + 5))
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        days = list(range(1, 32))

        # Avoid nested Row inside Column
        event_year = gr.Dropdown(choices=years, value=current_year, label="Year")
        event_month = gr.Dropdown(choices=months, value=months[datetime.now().month - 1], label="Month")
        event_day = gr.Dropdown(choices=days, value=datetime.now().day, label="Day")
        event_name = gr.Textbox(label="Event Name", placeholder="Enter event name")
        event_occasion = gr.Dropdown(
            ["Casual", "Formal", "Party", "Work", "Wedding", "Interview", "Travel",
             "Festival", "Beach", "Night Out", "Religious Event", "Date", "Business",
             "Gym", "Brunch", "Outdoor Adventure"],
            label="Event Occasion"
        )
        event_location = gr.Textbox(label="Event Location (optional)", placeholder="Enter location") # Define event_location here!
        add_event_btn = gr.Button("Add Event to Calendar")
        add_event_status = gr.Textbox(label="Add Event Status", visible=True)

        # Calendar view of upcoming events
        calendar_view = gr.HTML(label="Your Calendar")
        check_events_btn = gr.Button("View Calendar")

        # Function to add an event to the calendar with separate date components
        # Connect the buttons to their functions
        add_event_btn.click(
            fn=add_event_to_calendar,
            inputs=[username, event_name, event_year, event_month, event_day, event_occasion, event_location],
            outputs=add_event_status
        )

        check_events_btn.click(
            fn=display_calendar,
            inputs=[username],
            outputs=calendar_view
        )