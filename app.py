from flask import Flask, request, jsonify, render_template
import json
import pickle
import numpy as np
import tensorflow as tf
import nltk
from nltk.stem import WordNetLemmatizer
import sqlite3
import time
import os

# --- ADD THIS BLOCK FOR CLOUD PRODUCTION ---
# This ensures the cloud server downloads the required language data
import certifi
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
# -------------------------------------------

app = Flask(__name__)
lemmatizer = WordNetLemmatizer()

# ... (Keep the rest of your app.py code exactly the same!) ...
# Load Model and objects
def load_resources():
    try:
        model = tf.keras.models.load_model('chatbot_model.keras')
        with open('vectorizer.pkl', 'rb') as f:
            vectorizer = pickle.load(f)
        with open('label_encoder.pkl', 'rb') as f:
            label_encoder = pickle.load(f)
        with open('intents.json', 'r', encoding='utf-8') as f:
            intents = json.load(f)
        return model, vectorizer, label_encoder, intents
    except Exception as e:
        print(f"Error loading resources. Did you train the model? {e}")
        return None, None, None, None

model, vectorizer, label_encoder, intents = load_resources()

def log_metrics(latency, confidence, intent_tag):
    """Logs latency and confidence score to metrics.log for Chapter 4"""
    with open('metrics.log', 'a') as f:
        log_entry = f"{time.strftime('%Y-%m-%d %H:%M:%S')} | Intent: {intent_tag} | Confidence: {confidence:.4f} | Latency: {latency:.2f} ms\n"
        f.write(log_entry)

def preprocess_input(text):
    words = nltk.word_tokenize(text)
    words = [lemmatizer.lemmatize(word.lower()) for word in words]
    return ' '.join(words)

def get_order_status(order_id):
    """Query the simulated SQLite database for Order Tracking"""
    try:
        conn = sqlite3.connect('ecommerce.db')
        cursor = conn.cursor()
        cursor.execute("SELECT DeliveryStatus FROM Orders WHERE OrderID=?", (order_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return f"Your order (ID: {order_id}) is currently: {result[0]}."
        else:
            return f"I couldn't find an order with ID: {order_id}. Please check the number and try again."
    except Exception as e:
        return "There was an error accessing the database."

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    start_time = time.time()
    
    data = request.get_json()
    user_message = data.get('message', '')
    order_id_context = data.get('order_id', None) # If frontend already knows we need an ID
    
    if not user_message:
        return jsonify({"response": "Please write something."})
        
    # Hard override: If the message is purely numbers, assume it's an Order ID
    # This bypasses the browser's javascript caching issues!
    if user_message.strip().isdigit():
        latency_ms = (time.time() - start_time) * 1000
        log_metrics(latency_ms, 1.0, 'Order_Tracking')
        return jsonify({
            "response": get_order_status(user_message.strip()),
            "intent": "Order_Tracking",
            "confidence": 1.0,
            "latency_ms": latency_ms
        })
    # Preprocess
    processed_text = preprocess_input(user_message)
    X_input = vectorizer.transform([processed_text]).toarray()
    
    # Predict
    predictions = model.predict(X_input, verbose=0)[0]
    predicted_class_index = np.argmax(predictions)
    confidence_score = predictions[predicted_class_index]
    
    # Map index to intent
    intent_tag = label_encoder.inverse_transform([predicted_class_index])[0]
    
    # Calculate Latency
    end_time = time.time()
    latency_ms = (end_time - start_time) * 1000
    
    # Log Metrics (Crucial for Chapter 4)
    log_metrics(latency_ms, confidence_score, intent_tag)
    
    # Fallback if confidence is too low
    if confidence_score < 0.3:
        intent_tag = 'Fallback'
        
    # Find matching response
    response_text = ""
    for intent in intents['intents']:
        if intent['tag'] == intent_tag:
            import random
            response_text = random.choice(intent['responses'])
            break
            
    # Conditional logic for Order Tracking
    if intent_tag == 'Order_Tracking' or order_id_context:
        # Force the intent to log correctly if we skipped ML NLP
        if order_id_context:
            intent_tag = 'Order_Tracking' 
            
        # Simple extraction: if the user types just numbers, treat as order ID
        words = user_message.split()
        potential_ids = [w for w in words if w.isdigit()]
        
        if order_id_context:
             response_text = get_order_status(order_id_context)
        elif potential_ids:
             response_text = get_order_status(potential_ids[0])
        else:
             response_text = "Please provide your Order ID (e.g. 1001), and I will check the delivery status for you."

    return jsonify({
        "response": response_text,
        "intent": intent_tag,
        "confidence": float(confidence_score),
        "latency_ms": latency_ms
    })

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    app.run(debug=True, port=5000)
