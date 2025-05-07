// Form validation for the preference form

document.addEventListener('DOMContentLoaded', function() {
    const preferenceForm = document.getElementById('preference-form');
    
    if (preferenceForm) {
        preferenceForm.addEventListener('submit', function(event) {
            if (!validateForm()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            preferenceForm.classList.add('was-validated');
        });
    }
    
    // Update budget value display when slider changes
    const budgetSlider = document.getElementById('budget');
    const budgetDisplay = document.getElementById('budget-display');
    
    if (budgetSlider && budgetDisplay) {
        budgetSlider.addEventListener('input', function() {
            budgetDisplay.textContent = '₹' + this.value;
        });
        
        // Set initial value
        budgetDisplay.textContent = '₹' + budgetSlider.value;
    }
});

function validateForm() {
    let isValid = true;
    
    // College validation
    const college = document.getElementById('college');
    if (!college.value) {
        isValid = false;
        setInvalidFeedback(college, 'Please select your college');
    } else {
        setValidFeedback(college);
    }
    
    // Budget validation
    const budget = document.getElementById('budget');
    if (!budget.value || budget.value < 1000) {
        isValid = false;
        setInvalidFeedback(budget, 'Please set a valid budget (minimum ₹1000)');
    } else {
        setValidFeedback(budget);
    }
    
    // Room type validation
    const roomType = document.querySelector('input[name="room_type"]:checked');
    if (!roomType) {
        isValid = false;
        document.getElementById('room-type-feedback').textContent = 'Please select a room type';
        document.getElementById('room-type-feedback').style.display = 'block';
    } else {
        document.getElementById('room-type-feedback').style.display = 'none';
    }
    
    // Hostel type validation
    const hostelType = document.querySelector('input[name="hostel_type"]:checked');
    if (!hostelType) {
        isValid = false;
        document.getElementById('hostel-type-feedback').textContent = 'Please select a hostel type';
        document.getElementById('hostel-type-feedback').style.display = 'block';
    } else {
        document.getElementById('hostel-type-feedback').style.display = 'none';
    }
    
    // Amenities validation (at least one should be selected)
    const amenities = document.querySelectorAll('input[name="amenities"]:checked');
    if (amenities.length === 0) {
        isValid = false;
        document.getElementById('amenities-feedback').textContent = 'Please select at least one amenity';
        document.getElementById('amenities-feedback').style.display = 'block';
    } else {
        document.getElementById('amenities-feedback').style.display = 'none';
    }
    
    return isValid;
}

function setInvalidFeedback(element, message) {
    element.setCustomValidity('Invalid');
    const feedback = element.nextElementSibling;
    if (feedback && feedback.classList.contains('invalid-feedback')) {
        feedback.textContent = message;
    }
}

function setValidFeedback(element) {
    element.setCustomValidity('');
}
