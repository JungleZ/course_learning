import subprocess
import sys
import os

def install_requirements():
    """Install required packages from requirements.txt"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Requirements installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install requirements: {e}")
        sys.exit(1)

def run_app():
    """Run the Flask application"""
    try:
        # Set environment variables for Flask
        os.environ['FLASK_APP'] = 'app.py'
        os.environ['FLASK_ENV'] = 'development'
        # Get port from environment variable, default to 8081 to avoid 8080 and 8090
        port = os.environ.get('PORT', 8081)
        # Run the app
        subprocess.check_call([sys.executable, "-m", "flask", "run", "--host=0.0.0.0", "--port=" + str(port)])
    except subprocess.CalledProcessError as e:
        print(f"Failed to run the application: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")

if __name__ == "__main__":
    print("Starting deployment of Love App...")
    install_requirements()
    print("Starting Flask application...")
    run_app()