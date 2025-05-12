from flask import Flask, request, render_template_string
import logging
import requests
import datetime

app = Flask(__name__)

# Dane autora
AUTHOR_NAME = "Bahdan Chumak"
TCP_PORT = 5001

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='a',
                    format='%(asctime)s - %(message)s')
x = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"Starting app with AUTHOR_NAME=Bahdan Chumak, TCP_PORT=5001, {x}")

# Lista krajów i miast
LOCATIONS = {
    "PL": ["Warszawa", "Kraków", "Gdańsk"],
    "DE": ["Berlin", "Monachium", "Hamburg"],
    "FR": ["Paryż", "Marsylia", "Lyon"]
}

# Strona główna - wybór kraju i miasta
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        country = request.form['country']
        city = request.form['city']
        weather = get_weather(city, country)
        return render_template_string(RESULT_TEMPLATE, city=city, country=country, weather=weather)
    return render_template_string(FORM_TEMPLATE, locations=LOCATIONS)

# Funkcja pobierania pogody
def get_weather(city, country):
    API_KEY = "7bbdfbba46560bb3dd10c4d9512b353e"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city},{country}&appid={API_KEY}&units=metric&lang=pl"
    print(f"Zapytanie URL: {url}")
    response = requests.get(url)
    print(f"Odpowiedź status code: {response.status_code}")
    print(f"Odpowiedź tekst: {response.text}")
    if response.status_code == 200:
        data = response.json()
        return {
            'description': data['weather'][0]['description'],
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity']
        }
    else:
        return {"error": "Nie udało się pobrać pogody."}

# Szablony HTML (bez zmian)
FORM_TEMPLATE = """
<!doctype html>
<title>Wybierz lokalizację</title>
<h1>Wybierz kraj i miasto</h1>
<form method="post">
    <select name="country" id="country" onchange="updateCities()">
    {% for country in locations %}
        <option value="{{ country }}">{{ country }}</option>
    {% endfor %}
    </select>

    <select name="city" id="city">
    {% for city in locations[locations|list|first] %}
        <option value="{{ city }}">{{ city }}</option>
    {% endfor %}
    </select>

    <input type="submit" value="Pokaż pogodę">
</form>

<script>
    const locations = {{ locations|tojson }};
    function updateCities() {
        const country = document.getElementById('country').value;
        const citySelect = document.getElementById('city');
        citySelect.innerHTML = '';
        locations[country].forEach(function(city) {
            const option = document.createElement('option');
            option.text = city;
            citySelect.add(option);
        });
    }
</script>
"""

RESULT_TEMPLATE = """
<!doctype html>
<title>Wynik</title>
<h1>Pogoda w {{ city }}, {{ country }}</h1>
{% if weather.error %}
<p>{{ weather.error }}</p>
{% else %}
<p>Opis: {{ weather.description }}</p>
<p>Temperatura: {{ weather.temperature }} °C</p>
<p>Wilgotność: {{ weather.humidity }}%</p>
{% endif %}
<br><a href="/">Wróć</a>
"""

if __name__ == "__main__":
    logging.info(f"Application started by {AUTHOR_NAME} on TCP port {TCP_PORT}")
    app.run(host="0.0.0.0", port=TCP_PORT)