from flask import Flask, request, render_template_string
from utils.api_router import APIRouter
import os

app = Flask(__name__)
api_router = APIRouter()

DASHBOARD = """
<!DOCTYPE html>
<html>
<head>
    <title>Moraqlo AI Dashboard</title>
    <style>body { background: #444; color: white; font-family: Arial; }</style>
</head>
<body>
    <h1><img src="{{ logo }}" width="50"> Moraqlo AI Dashboard</h1>
    <h2>Agents Working</h2>
    <ul>
        <li>Analyzer - Finding hot products</li>
        <li>OrderProcessor - Shipping to UAE</li>
    </ul>
    <h2>Chat with Us</h2>
    <form method="POST">
        <input type="text" name="query" placeholder="Ask or feedback...">
        <button>Send</button>
    </form>
    {% if response %}<p><b>Team:</b> {{ response }}</p>{% endif %}
</body>
</html>
"""

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    response = None
    if request.method == "POST":
        query = request.form["query"]
        prompt = f"Respond as Moraqlo AI team for UAE focus: {query}"
        response = api_router.generate(prompt, model="gemmi/2.0-flash")
    logo = os.getenv("MORAQLO_LOGO_PATH", "/app/moraqlo_logo.png")
    return render_template_string(DASHBOARD, logo=logo, response=response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)