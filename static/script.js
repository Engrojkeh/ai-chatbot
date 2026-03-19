document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const chatScroller = document.getElementById('chat-scroller');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const typingIndicator = document.getElementById('typing-indicator');

    // Expected context for multi-turn flow
    let orderTrackingContext = null;

    function scrollToBottom() {
        chatScroller.scrollTop = chatScroller.scrollHeight;
    }

    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.textContent = text;
        
        messageDiv.appendChild(bubble);
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    }

    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        // 1. Add user message
        addMessage(text, 'user');
        userInput.value = '';
        
        // 2. Show typing indicator (incorporating 1-2s delay for UX requirement)
        typingIndicator.classList.remove('hidden');
        scrollToBottom();

        // 3. Fake delay parameter (1000 - 2000 ms)
        const typingDelay = Math.floor(Math.random() * 1000) + 1000;

        try {
            // Check if user is typing an order ID directly (only digits)
            const isDigit = /^\d+$/.test(text.trim());
            let requestData = { message: text };
            
            if (isDigit) {
                // We assume a pure number is tracking an order
                requestData.order_id = text.trim();
            }
            
            // Send payload to backend Flask API
            // Change this line:
// const fetchPromise = fetch('/api/chat', {

// To exactly this:
const fetchPromise = fetch('https://naija-support-bot.onrender.com/api/chat', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(requestData)
});
            // Wait for both fetch and min artificial delay
            const [response] = await Promise.all([
                fetchPromise,
                new Promise(resolve => setTimeout(resolve, typingDelay))
            ]);

            const data = await response.json();
            
            // Hide typing indicator
            typingIndicator.classList.add('hidden');

            if (data.response) {
                addMessage(data.response, 'bot');
            } else {
                addMessage("Sorry, we experienced an issue connecting to our servers.", 'bot');
            }

        } catch (error) {
            console.error("Error communicating with backend API:", error);
            typingIndicator.classList.add('hidden');
            addMessage("There was an error connecting to the server. Is the Flask app running?", 'bot');
        }
    }

    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});
