#!/usr/bin/env python3
"""
Wrapper script to run The Pond web interface with proper environment setup.
This script sets up the PYTHONPATH and runs The Pond on port 5000.
"""
import os
import sys

# Set up PYTHONPATH to include the project root
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.environ['PYTHONPATH'] = project_root

# Import and run The Pond
if __name__ == "__main__":
    # Set PC mode to enable debug mode
    os.environ['PC'] = '1'
    
    # Import the main function from the_pond.py
    from catpilot.system.the_pond.the_pond import main, setup, Flask
    import secrets
    
    # Create Flask app
    app = Flask(__name__, 
                static_folder="catpilot/system/the_pond/assets",
                static_url_path="/assets",
                template_folder="catpilot/system/the_pond/templates")
    
    # Set up routes
    setup(app)
    
    # Configure app
    app.secret_key = secrets.token_hex(32)
    
    # Run on port 5000 with all hosts allowed (required for Replit)
    print("Starting The Pond web interface on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
