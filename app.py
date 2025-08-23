from flask import Flask, request, jsonify
from flask_cors import CORS
from routes.chat import chat_bp

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(chat_bp, url_prefix="/api/chat")

@app.route("/")
def index():
    return "✅ XmPrepNEETGuru Flask API is running!"

if __name__ == "__main__":
    app.run(debug=True)
