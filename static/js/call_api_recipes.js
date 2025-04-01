// Variables de estado
let currentPage = 0; // Ahora lleva el control del offset (from)
let isLoading = false;
let has_next_loading = false;

// Funciones para mostrar/ocultar el loader
function showLoader() { document.getElementById('loader').style.display = 'block'; }
function hideLoader() { document.getElementById('loader').style.display = 'none'; }

// Función principal para cargar recetas
async function loadRecipes(reset = false) {
    if(isLoading) return;
    isLoading = true;
    showLoader();
    
    if(reset) currentPage = 0;

    const params = new URLSearchParams({
        q: document.getElementById('search').value.trim() || "Pasta",
        page: currentPage
    });

    try {
        
        const response = await fetch(`/get_recipes?${params.toString()}`);
        const data = await response.json();
        
        if(data.status !== 'success') throw new Error(data.error || 'Error fetching recipes');
        
        const container = document.getElementById('recipes-container');
        if(reset) container.innerHTML = '';

        if(data.recipes.length === 0 && currentPage === 0) {
            document.getElementById('no-results').style.display = 'block';
        } else {
            document.getElementById('no-results').style.display = 'none';
        }

        data.recipes.forEach(recipe => {
            const categories = recipe.categories.slice(0, 3)
                .map(cat => `<span class="badge bg-secondary me-1">${cat}</span>`).join('');
            
            const card = `
            <div class="col-lg-3 col-md-4 col-sm-6 mb-4">
                <div class="card h-100">
                        <a href="/specific_recipe/${recipe.id}" target="_blank">
                            <img src="${recipe.image_url || '../static/img/placeholder.jpg'}" 
                                 class="card-img-top" 
                                 alt="${recipe.name}">
                        </a>
                    <div class="card-body">
                        <h5 class="card-title">${recipe.name}</h5>
                        
                        <div class="d-flex justify-content-between small mb-2">
                            <div><i class="fas fa-clock me-1"></i>${recipe.cook_time || 'N/A'} min</div>
                            <div><i class="fas fa-users me-1"></i>${recipe.servings || 'N/A'}</div>
                        </div>
                        
                        <div class="ingredients mb-2">
                            ${recipe.ingredients.slice(0, 3).map(ing => `
                                <span class="d-block text-truncate" title="${ing}">
                                    <i class="fas fa-check-circle text-success me-1"></i>${ing}
                                </span>
                            `).join('')}
                        </div>
                        
                        <div class="categories">${categories}</div>
                    </div>
                </div>
            </div>
            `;
            
            container.insertAdjacentHTML('beforeend', card);
        });

        // Actualizar paginación
        has_next_loading = data.recipes.length >= 8;
        if(has_next_loading) currentPage += 8;

    } catch(error) {
        console.error('Error:', error);
        alert('Error cargando recetas: ' + error.message);
    } finally {
        hideLoader();
        isLoading = false;
    }
}

// Manejo del scroll infinito
window.addEventListener('scroll', () => {
    const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
    if (scrollTop + clientHeight >= scrollHeight - 600 && !isLoading && has_next_loading) {
        loadRecipes();
    }
});

// Event listeners
document.getElementById('search').addEventListener('input', () => loadRecipes(true));
document.querySelector('form').addEventListener('submit', e => {
    e.preventDefault();
    loadRecipes(true);
});

// Carga inicial
loadRecipes();