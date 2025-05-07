// Form validation for preference form

document.addEventListener('DOMContentLoaded', function() {
    // Get the form element
    const form = document.getElementById('preference-form');
    
    if (form) {
        // Update budget display when slider changes
        const budgetSlider = document.getElementById('budget');
        const budgetDisplay = document.getElementById('budget-display');
        
        if (budgetSlider && budgetDisplay) {
            budgetSlider.addEventListener('input', function() {
                budgetDisplay.textContent = '₹' + this.value;
            });
        }
        
        // Form validation
        form.addEventListener('submit', function(event) {
            if (!validateForm()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        });
    }
});

function validateForm() {
    let isValid = true;
    
    // College validation
    const college = document.getElementById('college');
    if (!college.value) {
        setInvalidFeedback(college, 'Please select your college');
        isValid = false;
    } else {
        setValidFeedback(college);
    }
    
    // Room type validation
    const roomTypes = document.querySelectorAll('input[name="room_type"]');
    let roomTypeSelected = false;
    
    roomTypes.forEach(function(radio) {
        if (radio.checked) {
            roomTypeSelected = true;
        }
    });
    
    if (!roomTypeSelected) {
        document.getElementById('room-type-feedback').textContent = 'Please select a room type';
        document.getElementById('room-type-feedback').classList.add('invalid-feedback');
        isValid = false;
    } else {
        document.getElementById('room-type-feedback').textContent = '';
    }
    
    // Hostel type validation
    const hostelTypes = document.querySelectorAll('input[name="hostel_type"]');
    let hostelTypeSelected = false;
    
    hostelTypes.forEach(function(radio) {
        if (radio.checked) {
            hostelTypeSelected = true;
        }
    });
    
    if (!hostelTypeSelected) {
        document.getElementById('hostel-type-feedback').textContent = 'Please select a hostel type';
        document.getElementById('hostel-type-feedback').classList.add('invalid-feedback');
        isValid = false;
    } else {
        document.getElementById('hostel-type-feedback').textContent = '';
    }
    
    return isValid;
}

function setInvalidFeedback(element, message) {
    element.classList.add('is-invalid');
    element.classList.remove('is-valid');
    
    // Get the next sibling which should be the feedback div
    const feedback = element.nextElementSibling;
    if (feedback && feedback.classList.contains('invalid-feedback')) {
        feedback.textContent = message;
    }
}

function setValidFeedback(element) {
    element.classList.remove('is-invalid');
    element.classList.add('is-valid');
}