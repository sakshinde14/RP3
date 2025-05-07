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
    const budgetSlider = document.getElementById('budget');
    const budgetValue = document.getElementById('budget-display');
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

// Helper function to format amenity names
function formatAmenityName(amenity) {
    return amenity.replace(/_/g, ' ').split(' ').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
    ).join(' ');
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
    const rating = card.dataset.rating;
    const distance = card.dataset.distance;
    const colleges = card.dataset.colleges.split(',');
    
    // Populate modal
    const modal = document.getElementById('hostelDetailModal');
    modal.querySelector('.modal-title').textContent = name;
    
    // Format amenities with better display names
    let amenitiesList = amenities.map(amenity => 
        `<span class="badge bg-info me-1 mb-1">${formatAmenityName(amenity)}</span>`
    ).join('');
    
    let collegesList = colleges.map(college => 
        `<span class="badge bg-secondary me-1 mb-1">${college}</span>`
    ).join('');
    
    const modalBody = modal.querySelector('.modal-body');
    modalBody.innerHTML = `
        <div class="row">
            <div class="col-md-12">
                <div class="row mb-4">
                    <div class="col-md-8">
                        <h5>Details</h5>
                        <p><strong><i class="fas fa-home me-2"></i>Type:</strong> ${hostelType}</p>
                        <p><strong><i class="fas fa-rupee-sign me-2"></i>Monthly Rent:</strong> ₹${rent}</p>
                        <p><strong><i class="fas fa-bed me-2"></i>Room Types:</strong> ${roomTypes}</p>
                        <p><strong><i class="fas fa-map-marker-alt me-2"></i>Address:</strong> ${address}</p>
                        <p><strong><i class="fas fa-phone me-2"></i>Contact:</strong> ${contact}</p>
                        <p><strong><i class="fas fa-shield-alt me-2"></i>Safety Rating:</strong> ${safety}/5</p>
                        <p><strong><i class="fas fa-star me-2"></i>Overall Rating:</strong> ${rating}/5</p>
                        <p><strong><i class="fas fa-route me-2"></i>Distance from College:</strong> ${distance} km</p>
                    </div>
                    <div class="col-md-4">
                        <div class="card bg-dark">
                            <div class="card-body text-center">
                                <h5 class="card-title"><i class="fas fa-percent me-2"></i>Match Score</h5>
                                <div class="display-4 fw-bold text-${card.dataset.score >= 80 ? 'success' : (card.dataset.score >= 60 ? 'info' : (card.dataset.score >= 40 ? 'warning' : 'danger'))}">
                                    ${card.dataset.score}%
                                </div>
                                <p class="text-muted mt-2">Based on your preferences</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6">
                        <h5><i class="fas fa-clipboard-list me-2"></i>Amenities</h5>
                        <div class="mb-3">${amenitiesList}</div>
                    </div>
                    <div class="col-md-6">
                        <h5><i class="fas fa-university me-2"></i>Colleges Nearby</h5>
                        <div>${collegesList}</div>
                    </div>
                </div>
                
                <div class="mt-4">
                    <h5><i class="fas fa-info-circle me-2"></i>Note for Female Students</h5>
                    <p class="bg-dark p-3 rounded">This accommodation has been verified for safety standards suitable for female students. Always visit before finalizing and consider traveling with a friend for the first visit.</p>
                </div>
            </div>
        </div>
    `;
    
    // Set up contact button with proper link
    const contactButton = modal.querySelector('#contact-hostel');
    contactButton.href = `tel:${contact}`;
    
    // Show modal
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}
