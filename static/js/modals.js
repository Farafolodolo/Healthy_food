let currentIngredient = '';
const modal = document.getElementById('SpecificModal');

// Set up when DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Set up ingredient button listeners
    document.querySelectorAll('.ingredient-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            currentIngredient = e.currentTarget.getAttribute('data-ingredient');
            console.log("Selected ingredient:", currentIngredient);
        });
    });

    // Set up modal header buttons
    document.querySelectorAll('.btn-header').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.btn-header').forEach(b => b.classList.remove('active'));
            e.currentTarget.classList.add('active');
            
            if(e.currentTarget.dataset.content === 'substitutes') {
                showSubstitutes();
            } else {
                showProducts();
            }
        });
    });
});

// Configurar eventos cuando el modal se muestra
modal.addEventListener('show.bs.modal', () => {
    resetModal();
    showSubstitutes(); // Mostrar sustitutos por defecto
});

// Funciones para manejar el contenido del modal
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

// Función para mostrar sustitutos
async function showSubstitutes() {
    try {
        resetModal();
        console.log("Fetching substitutes for:", currentIngredient);
        const response = await fetch(`/get_substitutes?ingredient=${encodeURIComponent(currentIngredient)}`);
        const data = await response.json();
        
        if(data.error) throw new Error(data.error);
        
        const substitutesList = document.getElementById('substitutesList');
        
        // Manejar caso de sin sustitutos
        if(data.substitutes && data.substitutes.length > 0) {
            substitutesList.innerHTML = data.substitutes.map(sub => `
                <li class="list-group-item">${sub}</li>
            `).join('');
        } else {
            substitutesList.innerHTML = `<li class="list-group-item text-muted">No substitutes were found for ${data.ingredient}</li>`;
        }
        
        substitutesList.classList.remove('d-none');
        hideLoading();
    } catch(error) {
        console.error("Error fetching substitutes:", error);
        // Mostrar mensaje amigable para el usuario
        showError("The substitutes could not be loaded. Please try again.");
    }
}

// Función para mostrar productos
async function showProducts() {
    try {
        resetModal();
        console.log("Fetching products for:", currentIngredient);
        const response = await fetch(`/search_ingredient?q=${encodeURIComponent(currentIngredient)}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if(data.error) throw new Error(data.error);
        
        const productsList = document.getElementById('productsList');
        
        if(data.results && data.results.length > 0) {
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
                                        ${product.rating} (${product.totalRatings} valoraciones)
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
            productsList.innerHTML = `<li class="list-group-item text-muted">No products found for ${currentIngredient}</li>`;
        }
        
        productsList.classList.remove('d-none');
        hideLoading();
    } catch(error) {
        console.error("Error fetching products:", error);
        showError(`Error when searching for products: ${error.message}. Try again later.`);
    }
}

// Función para mostrar errores
function showError(message) {
    const errorText = document.querySelector('.error-text');
    errorText.textContent = message;
    document.getElementById('errorMessage').classList.remove('d-none');
    hideLoading();
}