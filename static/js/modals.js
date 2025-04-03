let currentIngredient = '';
const modal = document.getElementById('SpecificModal');

// Set up when DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Set up ingredient button listeners
    document.querySelectorAll('.ingredient-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            //It stores the ingredient on the variable if the button is clicked
            currentIngredient = e.currentTarget.getAttribute('data-ingredient');
            console.log("Selected ingredient:", currentIngredient);
        });
    });

    // Set up modal header buttons
    document.querySelectorAll('.btn-header').forEach(btn => {
        btn.addEventListener('click', (e) => {
            //It deletes the active on the headers
            document.querySelectorAll('.btn-header').forEach(b => b.classList.remove('active'));
            //It adds the active only on the selected
            e.currentTarget.classList.add('active');
            //It will show de substitutes or the products
            if(e.currentTarget.dataset.content === 'substitutes') {
                showSubstitutes();
            } else {
                showProducts();
            }
        });
    });
});

// When the modal loads, it resets the modal
modal.addEventListener('show.bs.modal', () => {
    resetModal();
    showSubstitutes(); // It shows the substitutes 
});

// This part resets the modal and show the loader by classes
function resetModal() {
    document.getElementById('substitutesList').classList.add('d-none');
    document.getElementById('productsList').classList.add('d-none');
    document.getElementById('errorMessage').classList.add('d-none');
    document.getElementById('loading').classList.remove('d-none');
}

function showLoading() {
    document.getElementById('loading').classList.remove('d-none');
}

function hideLoading() {
    document.getElementById('loading').classList.add('d-none');
}

// Function to show the substitutes
async function showSubstitutes() {
    try {
        resetModal();
        console.log("Fetching substitutes for:", currentIngredient);
        //It calls the api
        const response = await fetch(`/get_substitutes?ingredient=${encodeURIComponent(currentIngredient)}`);
        const data = await response.json();
        //If there is an error, it will show the error
        if(data.error) throw new Error(data.error);
        //The container for the substitutes
        const substitutesList = document.getElementById('substitutesList');
        
        // If there are results, it will show it
        if(data.substitutes && data.substitutes.length > 0) {
            substitutesList.innerHTML = data.substitutes.map(sub => `
                <li class="list-group-item">${sub}</li>
            `).join('');
        } else {
            //If there are not results, it will show an error
            substitutesList.innerHTML = `<li class="list-group-item text-muted">No substitutes were found for ${data.ingredient}</li>`;
        }
        //It will show the list
        substitutesList.classList.remove('d-none');
        //It hides the loading
        hideLoading();
    } catch(error) {
        console.error("Error fetching substitutes:", error);
        // Mostrar mensaje amigable para el usuario
        showError("The substitutes could not be loaded. Please try again.");
    }
}

// function for showing the products from the Amazon API
async function showProducts() {
    try {
        resetModal();
        console.log("Fetching products for:", currentIngredient);
        //It calls the API
        const response = await fetch(`/search_ingredient?q=${encodeURIComponent(currentIngredient)}`);
        //If the response are bad it will show an error
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        //It converts the response
        const data = await response.json();
        //If the data has an error it shows the error
        if(data.error) throw new Error(data.error);
        //The container of the products
        const productsList = document.getElementById('productsList');
        //It stores all the information in a list
        if(data.results && data.results.length > 0) {
            //It inserts the data with the function map
            productsList.innerHTML = data.results.map(product => `
                <li class="list-group-item">
                    <div class="row align-items-center">
                        <div class="col-3">
                            <img src="${product.image}" alt="${product.title}" class="img-thumbnail">
                        </div>
                        <div class="col-9">
                            <h6>${product.title}</h6>
                            <div class="mb-2">
                                ${product.price ? `
                                    <span class="h5 text-success">${product.price}</span>
                                    ${product.originalPrice && product.originalPrice !== 'Not available' ? 
                                        `<small class="text-muted text-decoration-line-through ms-2">${product.originalPrice}</small>` : ''}
                                ` : '<span class="text-muted">Consult price</span>'}
                            </div>
                            <div class="d-flex align-items-center gap-3 mb-2">
                                ${product.rating ? `
                                    <div class="small">
                                        <i class="fas fa-star text-warning"></i>
                                        ${product.rating} (${product.totalRatings} valuations)
                                    </div>
                                ` : ''}
                                ${product.isPrime === 'true' ? `
                                    <span class="badge bg-primary">
                                        <i class="fas fa-box"></i> Prime
                                    </span>
                                ` : ''}
                            </div>
                            <a href="${product.link}" target="_blank" class="btn btn-sm btn-primary">
                                <i class="fas fa-external-link-alt me-2"></i>View on Amazon
                            </a>
                        </div>
                    </div>
                </li>
            `).join('');
        } else {
            //If there is not a product (That would be weird), It shows an error
            productsList.innerHTML = `<li class="list-group-item text-muted">No products found for ${currentIngredient}</li>`;
        }
        //It shows the container
        productsList.classList.remove('d-none');
        hideLoading();
    } catch(error) {
        console.error("Error fetching products:", error);
        showError(`Error when searching for products: ${error.message}. Try again later.`);
    }
}

// function to show the error from the tries and catches
function showError(message) {
    const errorText = document.querySelector('.error-text');
    errorText.textContent = message;
    document.getElementById('errorMessage').classList.remove('d-none');
    hideLoading();
}