// Main JavaScript for the hostel recommendation system

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Filter functionality on recommendations page
    const filterForm = document.getElementById('filter-form');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            filterRecommendations();
        });
        
        // Also filter when any input changes
        const filterInputs = filterForm.querySelectorAll('input, select');
        filterInputs.forEach(input => {
            input.addEventListener('change', function() {
                filterRecommendations();
            });
        });
    }
    
    // Budget range slider
    const budgetSlider = document.getElementById('budget-slider');
    const budgetValue = document.getElementById('budget-value');
    if (budgetSlider && budgetValue) {
        budgetSlider.addEventListener('input', function() {
            budgetValue.textContent = '₹' + this.value;
        });
    }
});

function filterRecommendations() {
    const minScore = parseInt(document.getElementById('min-score').value) || 0;
    const maxRent = parseInt(document.getElementById('max-rent').value) || Infinity;
    const roomType = document.getElementById('filter-room-type').value;
    const hostelType = document.getElementById('filter-hostel-type').value;
    
    const recommendationCards = document.querySelectorAll('.recommendation-card');
    
    recommendationCards.forEach(card => {
        const score = parseFloat(card.dataset.score);
        const rent = parseInt(card.dataset.rent);
        const cardRoomTypes = card.dataset.roomTypes.split(',');
        const cardHostelType = card.dataset.hostelType;
        
        let shouldShow = true;
        
        // Check score
        if (score < minScore) shouldShow = false;
        
        // Check rent
        if (rent > maxRent) shouldShow = false;
        
        // Check room type
        if (roomType && roomType !== 'any' && !cardRoomTypes.includes(roomType)) shouldShow = false;
        
        // Check hostel type
        if (hostelType && hostelType !== 'any' && cardHostelType !== hostelType) shouldShow = false;
        
        // Show or hide the card
        if (shouldShow) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
    
    // Show empty state if no results
    const visibleCards = document.querySelectorAll('.recommendation-card[style="display: block"]');
    const emptyState = document.getElementById('empty-results');
    
    if (visibleCards.length === 0 && emptyState) {
        emptyState.style.display = 'block';
    } else if (emptyState) {
        emptyState.style.display = 'none';
    }
}

// Function to display more details in a modal
function showHostelDetails(hostelId) {
    const card = document.querySelector(`.recommendation-card[data-id="${hostelId}"]`);
    const name = card.dataset.name;
    const rent = card.dataset.rent;
    const roomTypes = card.dataset.roomTypes;
    const hostelType = card.dataset.hostelType;
    const amenities = card.dataset.amenities.split(',');
    const address = card.dataset.address;
    const contact = card.dataset.contact;
    const safety = card.dataset.safety;
    const cleanliness = card.dataset.cleanliness;
    const colleges = card.dataset.colleges.split(',');
    
    // Populate modal
    const modal = document.getElementById('hostelDetailModal');
    modal.querySelector('.modal-title').textContent = name;
    
    let amenitiesList = amenities.map(amenity => 
        `<span class="badge bg-info me-1 mb-1">${amenity}</span>`
    ).join('');
    
    let collegesList = colleges.map(college => 
        `<span class="badge bg-secondary me-1 mb-1">${college}</span>`
    ).join('');
    
    const modalBody = modal.querySelector('.modal-body');
    modalBody.innerHTML = `
        <div class="row">
            <div class="col-md-8">
                <h5>Details</h5>
                <p><strong>Type:</strong> ${hostelType}</p>
                <p><strong>Monthly Rent:</strong> ₹${rent}</p>
                <p><strong>Room Types:</strong> ${roomTypes}</p>
                <p><strong>Address:</strong> ${address}</p>
                <p><strong>Contact:</strong> ${contact}</p>
                <p><strong>Safety Rating:</strong> ${safety}/5</p>
                <p><strong>Cleanliness:</strong> ${cleanliness}/5</p>
                <h5>Amenities</h5>
                <div class="mb-3">${amenitiesList}</div>
                <h5>Colleges Nearby</h5>
                <div>${collegesList}</div>
            </div>
        </div>
    `;
    
    // Show modal
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}
