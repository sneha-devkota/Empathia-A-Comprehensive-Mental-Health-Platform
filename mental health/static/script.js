function sendMessage() {
    let userInput = document.getElementById('user-input').value;
    let chatbox = document.getElementById('chatbox');

    // Display the user message
    chatbox.innerHTML += `<p><strong>You:</strong> ${userInput}</p>`;
    
    // Simple chatbot logic
    let botResponse = '';
    if (userInput.toLowerCase().includes("hello")) {
        botResponse = "Hi! How can I help you today?";
    } else if (userInput.toLowerCase().includes("appointment")) {
        botResponse = "Would you like to book an appointment?";
    } else {
        botResponse = "I'm sorry, I didn't understand that.";
    }

    // Display the bot's response
    chatbox.innerHTML += `<p><strong>Bot:</strong> ${botResponse}</p>`;

    // Clear input field after sending message
    document.getElementById('user-input').value = '';

    // Scroll to the bottom of the chatbox after new message is added
    chatbox.scrollTop = chatbox.scrollHeight;
}
