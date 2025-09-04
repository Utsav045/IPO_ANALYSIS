// Main JavaScript for IPO Compass

document.addEventListener('DOMContentLoaded', function() {
    console.log('IPO Compass loaded successfully!');
    
    // Initialize all components
    initScrollAnimations();
    initTabSwitching();
    initAIAssistant();
    initNavbar();
    initTestimonials();
    initFloatingElements();
    
    // Add fade-in animation to elements
    const fadeElements = document.querySelectorAll('.card, .feature-icon, h1, h2, h5, .stat-card, .testimonial-card');
    fadeElements.forEach((element, index) => {
        setTimeout(() => {
            element.classList.add('fade-in');
        }, 100 * index);
    });
});

// Enhanced Scroll Animations
function initScrollAnimations() {
    const scrollElements = document.querySelectorAll('.js-scroll');
    
    const elementInView = (el, dividend = 1) => {
        const elementTop = el.getBoundingClientRect().top;
        return (
            elementTop <= (window.innerHeight || document.documentElement.clientHeight) / dividend
        );
    };
    
    const displayScrollElement = (element) => {
        element.classList.add('scrolled');
    };
    
    const hideScrollElement = (element) => {
        element.classList.remove('scrolled');
    };
    
    const handleScrollAnimation = () => {
        scrollElements.forEach((el) => {
            if (elementInView(el, 1.25)) {
                displayScrollElement(el);
            } else {
                hideScrollElement(el);
            }
        });
    };
    
    window.addEventListener('scroll', () => {
        handleScrollAnimation();
    });
    
    // Trigger on load
    handleScrollAnimation();
}

// Enhanced Tab Switching
function initTabSwitching() {
    const triggerTabList = [].slice.call(document.querySelectorAll('#ipoTabs button'));
    triggerTabList.forEach(function (triggerEl) {
        const tabTrigger = new bootstrap.Tab(triggerEl);
        
        triggerEl.addEventListener('click', function (event) {
            event.preventDefault();
            tabTrigger.show();
            
            // Add animation to tab content
            const target = document.querySelector(triggerEl.getAttribute('data-bs-target'));
            if (target) {
                target.classList.add('fade-in');
            }
        });
    });
}

// Enhanced AI Assistant
function initAIAssistant() {
    const chatInput = document.querySelector('#ai-assistant input');
    const sendButton = document.querySelector('#ai-assistant button');
    const chatContainer = document.querySelector('#ai-assistant .chat-container');
    const suggestions = document.querySelectorAll('#ai-assistant .suggestions .badge');
    
    if (chatInput && sendButton) {
        // Send message on button click
        sendButton.addEventListener('click', sendMessage);
        
        // Send message on Enter key
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
        
        // Add suggestion click handlers
        suggestions.forEach(suggestion => {
            suggestion.addEventListener('click', function() {
                chatInput.value = this.textContent;
                sendMessage();
            });
        });
    }
    
    function sendMessage() {
        const message = chatInput.value.trim();
        if (message) {
            // Add user message to chat
            addChatMessage(message, 'user');
            chatInput.value = '';
            
            // Show typing indicator
            showTypingIndicator();
            
            // Send request to Django backend
            fetch(`/get-response/?message=${encodeURIComponent(message)}`)
                .then(response => response.json())
                .then(data => {
                    hideTypingIndicator();
                    addChatMessage(data.response, 'ai');
                })
                .catch(error => {
                    hideTypingIndicator();
                    addChatMessage("Sorry, I encountered an error processing your request. Please try again.", 'ai');
                    console.error('Error:', error);
                });
        }
    }
    
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message mb-4 typing-indicator';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="d-flex">
                <div class="flex-shrink-0">
                    <div class="bg-success bg-opacity-10 text-success rounded-circle d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                        <i class="fas fa-robot"></i>
                    </div>
                </div>
                <div class="flex-grow-1 ms-3">
                    <div class="alert alert-success bg-success bg-opacity-10 border-success mb-0">
                        <div class="typing-dots">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        chatContainer.appendChild(typingDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    function hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    function addChatMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message mb-4';
        
        const timestamp = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        // Format structured responses with better styling
        let formattedText = text;
        if (sender === 'ai') {
            // Convert markdown-style headers to HTML
            formattedText = text
                .replace(/^### (.*$)/gim, '<h5 class="mt-3 mb-2 text-success">$1</h5>')
                .replace(/^## (.*$)/gim, '<h4 class="mt-3 mb-2 text-primary">$1</h4>')
                .replace(/^# (.*$)/gim, '<h3 class="mt-3 mb-2 text-primary">$1</h3>')
                // Convert bullet points
                .replace(/^\s*-\s(.*)$/gim, '<li>$1</li>')
                // Wrap consecutive <li> elements in <ul>
                .replace(/(<li>.*<\/li>)+/gs, '<ul class="mb-2">$&</ul>')
                // Convert bold text
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                // Convert italic text
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                // Handle line breaks
                .replace(/\n/g, '<br>');
        }
        
        if (sender === 'user') {
            messageDiv.innerHTML = `
                <div class="d-flex justify-content-end">
                    <div class="flex-grow-1 me-3">
                        <div class="alert alert-primary bg-primary bg-opacity-10 border-primary mb-0 text-end">
                            ${formattedText}
                        </div>
                        <div class="text-muted text-end small mt-1">${timestamp}</div>
                    </div>
                    <div class="flex-shrink-0">
                        <div class="bg-primary bg-opacity-10 text-primary rounded-circle d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                            <i class="fas fa-user"></i>
                        </div>
                    </div>
                </div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="d-flex">
                    <div class="flex-shrink-0">
                        <div class="bg-success bg-opacity-10 text-success rounded-circle d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                            <i class="fas fa-robot"></i>
                        </div>
                    </div>
                    <div class="flex-grow-1 ms-3">
                        <div class="alert alert-success bg-success bg-opacity-10 border-success mb-0">
                            ${formattedText}
                        </div>
                        <div class="text-muted small mt-1">Nexa AI • ${timestamp}</div>
                    </div>
                </div>
            `;
        }
        
        // Insert before the input form
        chatContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}

// Enhanced Navbar Scroll Effect
function initNavbar() {
    const navbar = document.querySelector('.navbar');
    
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }
}

// Testimonial Carousel
function initTestimonials() {
    // In a real implementation, this would initialize a carousel
    console.log('Testimonials initialized');
}

// Floating Elements Animation
function initFloatingElements() {
    const elements = document.querySelectorAll('.floating-element');
    elements.forEach(element => {
        // Randomize animation duration and delay
        const duration = 6 + Math.random() * 4;
        const delay = Math.random() * 2;
        element.style.animationDuration = `${duration}s`;
        element.style.animationDelay = `${delay}s`;
    });
}

// Newsletter Subscription
document.addEventListener('DOMContentLoaded', function() {
    const newsletterForm = document.querySelector('footer .input-group');
    if (newsletterForm) {
        const subscribeButton = newsletterForm.querySelector('button');
        const emailInput = newsletterForm.querySelector('input');
        
        subscribeButton.addEventListener('click', function() {
            const email = emailInput.value.trim();
            if (email && validateEmail(email)) {
                // Show success message
                const originalText = subscribeButton.innerHTML;
                subscribeButton.innerHTML = '<i class="fas fa-check"></i> Subscribed!';
                subscribeButton.classList.remove('btn-warning');
                subscribeButton.classList.add('btn-success');
                
                // Reset after 2 seconds
                setTimeout(() => {
                    subscribeButton.innerHTML = originalText;
                    subscribeButton.classList.remove('btn-success');
                    subscribeButton.classList.add('btn-warning');
                    emailInput.value = '';
                }, 2000);
            } else {
                // Show error state
                emailInput.classList.add('is-invalid');
                setTimeout(() => {
                    emailInput.classList.remove('is-invalid');
                }, 2000);
            }
        });
    }
});

// Email Validation
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Theme Toggle (if needed in future)
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update theme toggle button
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.innerHTML = newTheme === 'dark' ? 
            '<i class="fas fa-sun"></i>' : 
            '<i class="fas fa-moon"></i>';
    }
}

// Initialize theme on load
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.innerHTML = savedTheme === 'dark' ? 
            '<i class="fas fa-sun"></i>' : 
            '<i class="fas fa-moon"></i>';
        
        themeToggle.addEventListener('click', toggleTheme);
    }
}