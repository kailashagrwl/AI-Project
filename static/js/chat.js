// DOM Elements
const chatContainer = document.getElementById('chat-container');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-btn');

// Chat state
let isWaitingForResponse = false;

// Initialize chat
window.addEventListener('DOMContentLoaded', () => {
    initializeChat();
});

// Initialize chat with welcome message
async function initializeChat() {
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: '' })
        });
        const data = await response.json();
        addMessage(data.response, 'bot');
    } catch (error) {
        console.error('Error initializing chat:', error);
        addMessage('Sorry, there was an error connecting to the server. Please try again.', 'bot');
    }
}

// Format the message for better display
function formatMessage(message, sender) {
    // Check if this is a visa response by looking for key visa information patterns
    if (sender === 'bot' && 
        (message.includes('COUNTRY:') || 
         message.includes('🛂 COUNTRY:') || 
         message.includes('VISA TYPE:') || 
         message.includes('REQUIREMENTS:'))) {
        
        // Create a nicely formatted visa response card
        let formattedHTML = '<div class="visa-response-card">';
        
        // Split by newlines to process each line
        const lines = message.split('\n');
        let inVisaSection = false;
        let beforeVisaInfo = true;
        let introText = '';
        let inBulletList = false;
        
        lines.forEach(line => {
            // Capture introduction text before the visa information
            if (beforeVisaInfo && !line.includes('COUNTRY:') && !line.includes('🛂') && line.trim() !== '') {
                introText += `<p>${line}</p>`;
            }
            
            // Check if this line contains visa section information
            if (line.includes('COUNTRY:') || 
                line.includes('VISA TYPE:') || 
                line.includes('REQUIREMENTS:') || 
                line.includes('PROCESSING TIME:') || 
                line.includes('FEES:') || 
                line.includes('ENTRY TYPE:') || 
                line.includes('TIP:') ||
                line.match(/^🛂|^🧳|^📋|^⏱️|^💵|^✅|^💡/)) {
                
                beforeVisaInfo = false;
                inVisaSection = true;
                
                // If we were in a bullet list, close it
                if (inBulletList) {
                    formattedHTML += '</ul>';
                    inBulletList = false;
                }
                
                // Extract label and value
                let label, value;
                
                // Handle both formats: with emoji or text only
                if (line.includes(':')) {
                    // Handle lines with emojis
                    if (line.match(/^[^\w\s]/)) {
                        const emoji = line.match(/^[^\w\s]+/)[0].trim();
                        const remainder = line.replace(emoji, '').trim();
                        
                        if (remainder.includes(':')) {
                            [label, value] = remainder.split(':').map(part => part.trim());
                            label = emoji + ' ' + label;
                        } else {
                            label = emoji;
                            value = remainder;
                        }
                    } else {
                        // Handle text labels without emojis
                        [label, value] = line.split(':').map(part => part.trim());
                        
                        // Add emojis based on the label
                        if (label.includes('COUNTRY')) label = '🛂 ' + label;
                        else if (label.includes('VISA TYPE')) label = '🧳 ' + label;
                        else if (label.includes('REQUIREMENTS')) label = '📋 ' + label;
                        else if (label.includes('PROCESSING TIME')) label = '⏱️ ' + label;
                        else if (label.includes('FEES')) label = '💵 ' + label;
                        else if (label.includes('ENTRY TYPE')) label = '✅ ' + label;
                        else if (label.includes('TIP')) label = '💡 ' + label;
                    }
                    
                    formattedHTML += `
                        <div class="visa-info-row">
                            <div class="visa-label">${label}:</div>
                            <div class="visa-value">${value || ''}</div>
                        </div>
                    `;
                }
            } else if (line.trim() === '') {
                // Empty line handling
                if (inVisaSection) {
                    // Do nothing in visa section to avoid extra space
                } else {
                    formattedHTML += '<br>';
                }
            } else if (line.trim().startsWith('- ')) {
                // Bullet point handling
                if (!inBulletList) {
                    // Start a new bullet list
                    formattedHTML += '<ul class="requirements-list">';
                    inBulletList = true;
                }
                
                // Add the bullet point
                formattedHTML += `<li>${line.trim().substring(2)}</li>`;
            } else {
                // Regular text
                if (inVisaSection) {
                    // If we were in a bullet list but this line isn't a bullet, close the list
                    if (inBulletList) {
                        formattedHTML += '</ul>';
                        inBulletList = false;
                    }
                    
                    // This is likely continuation of the previous visa field
                    formattedHTML += `
                        <div class="visa-info-continuation">
                            <div class="visa-value">${line}</div>
                        </div>
                    `;
                } else if (!beforeVisaInfo) {
                    // Text after visa information (e.g. additional notes)
                    formattedHTML += `<p class="additional-info">${line}</p>`;
                }
            }
        });
        
        // Close any open bullet list
        if (inBulletList) {
            formattedHTML += '</ul>';
        }
        
        // Close the visa card
        formattedHTML += '</div>';
        
        // Add any intro text before the card
        return introText + formattedHTML;
    }
    
    // Regular message formatting with paragraph breaks
    // Handle bullet points in regular messages too
    let inBulletList = false;
    let formattedHTML = '';
    
    message.split('\n').forEach(line => {
        if (line.trim() === '') {
            // Empty line
            if (!inBulletList) {
                formattedHTML += '<br>';
            }
        } else if (line.trim().startsWith('- ')) {
            // Bullet point
            if (!inBulletList) {
                // Start a new bullet list
                formattedHTML += '<ul class="bullet-list">';
                inBulletList = true;
            }
            
            // Add the bullet point
            formattedHTML += `<li>${line.trim().substring(2)}</li>`;
        } else {
            // Regular text
            if (inBulletList) {
                // Close the bullet list
                formattedHTML += '</ul>';
                inBulletList = false;
            }
            
            formattedHTML += `<p>${line}</p>`;
        }
    });
    
    // Close any open bullet list
    if (inBulletList) {
        formattedHTML += '</ul>';
    }
    
    return formattedHTML;
}

// Add message to chat
function addMessage(message, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', `${sender}-message`);
    
    // Format the message content
    messageDiv.innerHTML = formatMessage(message, sender);
    
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Show typing indicator
function showTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.classList.add('typing-indicator');
    indicator.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;
    indicator.id = 'typing-indicator';
    chatContainer.appendChild(indicator);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Remove typing indicator
function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// Send message
async function sendMessage() {
    const message = userInput.value.trim();
    
    if (message && !isWaitingForResponse) {
        // Clear input and add user message
        userInput.value = '';
        addMessage(message, 'user');
        
        // Show typing indicator and disable input
        isWaitingForResponse = true;
        showTypingIndicator();
        userInput.disabled = true;
        sendButton.disabled = true;

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            
            // Remove typing indicator and add bot response
            removeTypingIndicator();
            addMessage(data.response, 'bot');
        } catch (error) {
            console.error('Error sending message:', error);
            removeTypingIndicator();
            addMessage('Sorry, there was an error processing your request. Please try again.', 'bot');
        } finally {
            // Re-enable input
            isWaitingForResponse = false;
            userInput.disabled = false;
            sendButton.disabled = false;
            userInput.focus();
        }
    }
}

// Event listeners
sendButton.addEventListener('click', sendMessage);

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Prevent empty submissions and enable/disable send button
userInput.addEventListener('input', () => {
    sendButton.disabled = userInput.value.trim() === '';
});

// Handle visibility change to maintain connection
document.addEventListener('visibilitychange', () => {
    if (!document.hidden && chatContainer.children.length === 0) {
        initializeChat();
    }
}); 