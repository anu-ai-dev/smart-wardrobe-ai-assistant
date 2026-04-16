import requests

API_KEY = "fbaf322ed08f82b7204d10fc531bf608"
city = "Mumbai"
url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
response = requests.get(url)
print(response.status_code)
print(response.json())
