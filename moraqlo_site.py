from flask import Flask, request, render_template_string
from utils.api_router import APIRouter
import os

app = Flask(__name__)
api_router = APIRouter()

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Moraqlo - Shop Smart</title>
    <style>body { font-family: Arial; background: white; } .chat { position: fixed; bottom: 10px; right: 10px; }</style>
</head>
<body>
    <h1><img src="{{ logo }}" width="100"> Moraqlo</h1>
    <h2>3 Reasons to Shop Moraqlo</h2>
    <ul>
        <li><b>Fast Deals:</b> Quick shipping for Ramadan!</li>
        <li><b>Top Picks:</b> Best tech, fashion, home stuff!</li>
        <li><b>Trusted:</b> Premium boxes with our logo!</li>
    </ul>
    <a href="#collections">See Collections</a>
    <h2 id="collections">Collections</h2>
    <p>Tech Gadgets - Coming soon!</p>
    <p>Fashion Finds - Coming soon!</p>
    <p>Home Essentials - Coming soon!</p>
    <p><a href="mailto:you@moraqlo.com">Contact Us</a></p>
    <div class="chat">
        <form method="POST">
            <input type="text" name="query" placeholder="Ask me...">
            <button>Send</button>
        </form>
        {% if response %}<p><b>Moraqlo:</b> {{ response }}</p>{% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    response = None
    if request.method == "POST":
        query = request.form["query"]
        prompt = f"Answer as Moraqlo’s assistant for UAE shoppers: {query}"
        response = api_router.generate(prompt, model="gemini/2.0-flash")
    logo = os.getenv("MORAQLO_LOGO_PATH", "/app/moraqlo_logo.png")
    return render_template_string(HTML, logo=logo, response=response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)