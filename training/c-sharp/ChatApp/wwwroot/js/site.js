// ChatApp JavaScript functionality

// Utility functions
function scrollToBottom(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.scrollTop = container.scrollHeight;
    }
}

function focusElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.focus();
    }
}

// Initialize page functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('ChatApp loaded successfully');
    
    // Auto-scroll messages container if it exists
    if (document.getElementById('messagesContainer')) {
        scrollToBottom('messagesContainer');
    }
    
    // Auto-focus username input if it exists
    if (document.getElementById('username')) {
        focusElement('username');
    }
    
    // Auto-focus message input if it exists
    if (document.getElementById('messageContent')) {
        focusElement('messageContent');
    }
});

// Export functions for use in other scripts
window.ChatApp = {
    scrollToBottom: scrollToBottom,
    focusElement: focusElement
};