document.addEventListener('DOMContentLoaded', function () {
    function sendMessage() {
        const messageInput = document.getElementById('message-input');
        const message = messageInput.value.trim();
        if (!message) return; // Exit if input is empty

        // Display the user's message in the chatbox
        const chatbox = document.getElementById('chat-box');
        chatbox.innerHTML += `<div class="message user-message">You: ${message}</div>`;

        // Clear the input field
        messageInput.value = '';

        // Send the message to the server
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message }),
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errData => {
                    throw new Error(errData.error || 'Unknown error');
                });
            }
            return response.json();
        })
        .then(data => {
            // Display the bot's response in the chatbox
            chatbox.innerHTML += `<div class="message bot-message">Bot: ${data.response}</div>`;
            chatbox.scrollTop = chatbox.scrollHeight; // Auto-scroll to the bottom
        })
        .catch(error => {
            console.error('Error:', error);
            chatbox.innerHTML += `<div class="message bot-message">Error: ${error.message}</div>`;
        });
    }

    // Add event listener for sending messages
    document.getElementById('send-message').addEventListener('click', sendMessage);
    document.getElementById('message-input').addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            sendMessage(); // Send message on Enter key press
        }
    });
});
