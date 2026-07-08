"""
Server Flask per il Correttore Ortografico e Grammaticale Italiano.
Espone API REST per l'analisi dei testi.
"""

import sys
import os

# Aggiungi la directory corrente al path
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request, jsonify, send_from_directory
from checker import ItalianChecker

app = Flask(__name__, static_folder="static", static_url_path="")

# Inizializza il controllore
checker = ItalianChecker()


@app.route("/api/check", methods=["POST"])
def check_text():
    """Analizza il testo inviato e restituisce errori e suggerimenti."""
    data = request.get_json(silent=True)
    if not data or "text" not in data:
        return jsonify({"error": "Campo 'text' mancante"}), 400

    text = data["text"]
    if not text or not text.strip():
        return jsonify({"error": "Testo vuoto"}), 400

    result = checker.check(text)
    return jsonify(result)


@app.route("/")
def index():
    """Serve la pagina principale."""
    return send_from_directory(app.static_folder, "index.html")


@app.route("/robots.txt")
def robots():
    return send_from_directory(".", "robots.txt")


@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory(".", "sitemap.xml")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 4599))
    app.run(host="0.0.0.0", port=port, debug=False)
