from flask import Flask
from routes import main_bp
#Initializes the flask as main
app = Flask(__name__)
#It registers the endpoints of the blueprint created
app.register_blueprint(main_bp)

if __name__ == "__main__":
    app.run(debug=True)