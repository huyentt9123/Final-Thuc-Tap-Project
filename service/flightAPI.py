import requests

CLIENT_ID = "VzTbiJc8VEohpc7KioLW1ppUH1hVaWmQ"
CLIENT_SECRET = "ujD4Z1GaVScziz2x"

def get_amadeus_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()
    return response.json()["access_token"]

def search_flights_amadeus(origin, destination, departure_date, adults=1, max_results=5):
    token = get_amadeus_token()
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": departure_date,
        "adults": adults,
        "max": max_results
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        return {"error": response.text, "status_code": response.status_code}