import json
import numpy as np
import pickle
import nltk
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
import os

# Ensure we have the necessary NLTK data for preprocessing
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
# Handle potential nltk download issues by explicitly downloading 'punkt_tab'
nltk.download('punkt_tab', quiet=True) 

lemmatizer = WordNetLemmatizer()

def load_data(filepath='intents.json'):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def preprocess_data(data):
    sentences = []
    labels = []
    
    for intent in data['intents']:
        tag = intent['tag']
        for pattern in intent['patterns']:
            # Tokenize: Break sentence into words
            words = nltk.word_tokenize(pattern)
            # Lemmatize: Reduce words to root form
            words = [lemmatizer.lemmatize(word.lower()) for word in words]
            sentences.append(' '.join(words))
            labels.append(tag)
            
    return sentences, labels

def train_model():
    data = load_data()
    sentences, labels = preprocess_data(data)
    
    # Encode labels to numerical values
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(labels)
    
    # TF-IDF Vectorization (handles Bag-of-Words and term frequency)
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(sentences).toarray()
    
    # Define Feed-Forward Artificial Neural Network
    model = Sequential()
    
    # Hidden Layers with ReLU activation
    model.add(Dense(128, input_shape=(len(X[0]),), activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.5))
    
    # Output Layer with Softmax for probability distribution / Confidence Score
    model.add(Dense(len(set(y)), activation='softmax'))
    
    # Compile the model
    model.compile(loss='sparse_categorical_crossentropy', optimizer=Adam(learning_rate=0.001), metrics=['accuracy'])
    
    print("Training the Deep Learning Model...")
    model.fit(X, y, epochs=200, batch_size=5, verbose=1)
    
    # Save required objects for the inference script
    model.save('chatbot_model.keras')
    with open('vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)
    with open('label_encoder.pkl', 'wb') as f:
        pickle.dump(label_encoder, f)
        
    print("Model and preprocessing objects saved successfully!")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    train_model()
