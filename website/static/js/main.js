// Main JavaScript file for Pet Health
document.addEventListener('DOMContentLoaded', function() {
    // Initialize animations
    initAnimations();
    
    // Initialize form validations
    initFormValidations();
    
    // Initialize mobile menu
    initMobileMenu();
    
    // Initialize tooltips
    initTooltips();
});

// Animation functions
function initAnimations() {
    // Add fade-in animation to elements with .fade-in class
    const fadeElements = document.querySelectorAll('.fade-in');
    fadeElements.forEach(element => {
        element.style.opacity = '0';
        setTimeout(() => {
            element.style.transition = 'opacity 0.5s ease-in-out';
            element.style.opacity = '1';
        }, 100);
    });
    
    // Add slide-in-up animation to elements with .slide-in-up class
    const slideElements = document.querySelectorAll('.slide-in-up');
    slideElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(50px)';
        setTimeout(() => {
            element.style.transition = 'opacity 0.5s ease-in-out, transform 0.5s ease-in-out';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, 100);
    });
}

// Form validation functions
function initFormValidations() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!validateForm(form)) {
                event.preventDefault();
            }
        });
        
        // Add real-time validation for inputs
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateInput(input);
            });
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
        if (!validateInput(input)) {
            isValid = false;
        }
    });
    
    return isValid;
}

function validateInput(input) {
    // Skip validation for optional fields
    if (!input.required && input.value === '') {
        removeError(input);
        return true;
    }
    
    // Validate required fields
    if (input.required && input.value === '') {
        showError(input, 'Este campo é obrigatório');
        return false;
    }
    
    // Validate email format
    if (input.type === 'email' && input.value !== '') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(input.value)) {
            showError(input, 'Por favor, insira um email válido');
            return false;
        }
    }
    
    // Validate password length
    if (input.type === 'password' && input.value !== '') {
        if (input.value.length < 6) {
            showError(input, 'A senha deve ter pelo menos 6 caracteres');
            return false;
        }
    }
    
    // Validate password confirmation
    if (input.id === 'confirmar_senha') {
        const password = document.getElementById('senha');
        if (password && input.value !== password.value) {
            showError(input, 'As senhas não coincidem');
            return false;
        }
    }
    
    // If all validations pass, remove any error messages
    removeError(input);
    return true;
}

function showError(input, message) {
    // Remove any existing error first
    removeError(input);
    
    // Create error message element
    const errorElement = document.createElement('div');
    errorElement.className = 'error-message';
    errorElement.textContent = message;
    errorElement.style.color = 'var(--danger-color)';
    errorElement.style.fontSize = '0.8rem';
    errorElement.style.marginTop = '5px';
    
    // Add error class to input
    input.classList.add('is-invalid');
    
    // Insert error message after input
    input.parentNode.insertBefore(errorElement, input.nextSibling);
}

function removeError(input) {
    // Remove error class from input
    input.classList.remove('is-invalid');
    
    // Remove error message if it exists
    const errorElement = input.nextElementSibling;
    if (errorElement && errorElement.className === 'error-message') {
        errorElement.remove();
    }
}

// Mobile menu functions
function initMobileMenu() {
    const menuToggle = document.querySelector('.menu-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            menuToggle.classList.toggle('active');
        });
    }
}

// Tooltip functions
function initTooltips() {
    const tooltips = document.querySelectorAll('.tooltip');
    
    tooltips.forEach(tooltip => {
        const tooltipText = tooltip.querySelector('.tooltip-text');
        
        if (tooltipText) {
            tooltip.addEventListener('mouseenter', function() {
                tooltipText.style.visibility = 'visible';
                tooltipText.style.opacity = '1';
            });
            
            tooltip.addEventListener('mouseleave', function() {
                tooltipText.style.visibility = 'hidden';
                tooltipText.style.opacity = '0';
            });
        }
    });
}

// Tab functionality
function openTab(event, tabId) {
    // Hide all tab content
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.style.display = 'none';
        content.classList.remove('active');
    });
    
    // Remove active class from all tab items
    const tabItems = document.querySelectorAll('.tab-item');
    tabItems.forEach(item => {
        item.classList.remove('active');
    });
    
    // Show the selected tab content and add active class to the clicked tab
    document.getElementById(tabId).style.display = 'block';
    document.getElementById(tabId).classList.add('active');
    event.currentTarget.classList.add('active');
}

// Accordion functionality
function toggleAccordion(element) {
    const content = element.nextElementSibling;
    
    if (content.style.display === 'block') {
        content.style.display = 'none';
        content.classList.remove('active');
    } else {
        content.style.display = 'block';
        content.classList.add('active');
    }
}

// Dropdown functionality
function toggleDropdown(element) {
    const dropdownMenu = element.nextElementSibling;
    
    if (dropdownMenu.classList.contains('show')) {
        dropdownMenu.classList.remove('show');
    } else {
        // Close all other dropdowns first
        const allDropdowns = document.querySelectorAll('.dropdown-menu');
        allDropdowns.forEach(dropdown => {
            dropdown.classList.remove('show');
        });
        
        dropdownMenu.classList.add('show');
    }
}

// Close dropdowns when clicking outside
document.addEventListener('click', function(event) {
    if (!event.target.matches('.dropdown-toggle')) {
        const dropdowns = document.querySelectorAll('.dropdown-menu');
        dropdowns.forEach(dropdown => {
            if (dropdown.classList.contains('show')) {
                dropdown.classList.remove('show');
            }
        });
    }
});

// Modal functionality
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// Close modal when clicking outside the modal content
window.addEventListener('click', function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});

// Pet protocol specific functions
function switchPet(petId) {
    // Redirect to the protocol page with the selected pet
    window.location.href = `/protocolo/${petId}`;
}

// Animation for pet cards
function animatePetCards() {
    const petCards = document.querySelectorAll('.pet-card');
    
    petCards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in');
        }, index * 100);
    });
}

// Initialize pet cards animation if they exist
if (document.querySelector('.pet-card')) {
    animatePetCards();
}
