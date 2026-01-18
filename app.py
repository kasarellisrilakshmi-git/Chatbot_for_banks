from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Simple greeting detection
GREETINGS = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon"]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "").lower()

    # Greeting response
    for greet in GREETINGS:
        if greet in user_message:
            return jsonify({"response": "Hello! Lakshmi Garu😊 How can I assist you with your banking needs today?"})

    # Default response
    return jsonify({"response": "Hello! Lakshmi👋 Welcome to Smart Banking Assistant. Please choose an option from the menu."})

@app.route("/option", methods=["POST"])
def option():
    return jsonify({"response": "Hi pichi 🤖, chatbot coming soon......"})

if __name__ == "__main__":
    app.run(debug=True)
