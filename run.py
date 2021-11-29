from jukebox import app

# To run this:
# - "python -m pip install -r requirements.txt" in console
# - "python run.py" in console
# - click on https://127.0.0.1:9874/ in terminal

if __name__ == "__main__":
    app.run(port=9874, debug=True)