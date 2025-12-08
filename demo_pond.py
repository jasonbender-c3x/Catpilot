#!/usr/bin/env python3
"""
Simplified demo version of The Pond for Replit environment.
This version runs without the full openpilot/hardware dependencies.
"""
from flask import Flask, render_template, jsonify, request, send_from_directory
import secrets
import os
import sys

# Set up project root in path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Create Flask app
app = Flask(__name__,
            static_folder="catpilot/system/the_pond/assets",
            static_url_path="/assets",
            template_folder="catpilot/system/the_pond/templates")

# Configure secret key
app.secret_key = secrets.token_hex(32)

@app.errorhandler(404)
def not_found(_):
    return render_template("index.html")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/api/status", methods=["GET"])
def status():
    """API endpoint to show that the server is running"""
    return jsonify({
        "status": "running",
        "mode": "demo",
        "message": "The Pond demo is running on Replit. Full hardware features are not available in this environment."
    })

@app.route("/api/info", methods=["GET"])
def info():
    """Provide basic info about the deployment"""
    return jsonify({
        "project": "CatPilot - The Pond",
        "description": "Web interface for CatPilot (openpilot fork)",
        "environment": "Replit Demo",
        "note": "This is a demo version. Full functionality requires comma.ai hardware."
    })

# Stub endpoints for features that require hardware
@app.route("/api/doors_available", methods=["GET"])
def doors_available():
    return jsonify({"result": False, "reason": "Hardware not available in demo mode"})

@app.route("/api/toggles", methods=["GET"])
def get_toggles():
    return jsonify({
        "toggles": {},
        "note": "Demo mode - toggle management requires full openpilot environment"
    })

@app.route("/api/error_logs", methods=["GET"])
def get_error_logs():
    if request.accept_mimetypes["application/json"]:
        return jsonify([]), 200
    return jsonify({"logs": [], "note": "No logs in demo mode"})

@app.route("/api/routes", methods=["GET"])
def get_routes():
    return jsonify({
        "routes": [],
        "note": "Demo mode - routes require comma device with recorded drives"
    })

if __name__ == "__main__":
    print("=" * 60)
    print("🐱 CatPilot - The Pond Web Interface (Demo Mode)")
    print("=" * 60)
    print("Starting server on http://0.0.0.0:5000")
    print("\nNote: This is a demo version running on Replit.")
    print("Full features require comma.ai hardware (comma 3/3X device).")
    print("=" * 60)
    
    # Run on port 5000 for Replit
    app.run(host="0.0.0.0", port=5000, debug=True)
