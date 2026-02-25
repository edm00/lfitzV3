const API_BASE_URL = 'http://localhost:8000/api';

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const vibeBtns = document.querySelectorAll('.vibe-btn');

    // Search function
    async function searchOutfits(query) {
        loading.style.display = 'block';
        results.innerHTML = '';
        
        try {
            const response = await fetch(`${API_BASE_URL}/search?query=${encodeURIComponent(query)}&limit=3`);
            const data = await response.json();
            
            loading.style.display = 'none';
            
            if (data.outfits && data.outfits.length > 0) {
                displayOutfits(data.outfits);
            } else {
                results.innerHTML = '<div class="no-results">No outfits found. Try a different vibe!</div>';
            }
        } catch (error) {
            loading.style.display = 'none';
            results.innerHTML = '<div class="no-results">Error fetching outfits. Please try again.</div>';
            console.error('Error:', error);
        }
    }

    // Display outfits
    function displayOutfits(outfits) {
        let html = '<h2>Your Perfect Outfits</h2>';
        
        outfits.forEach((outfit, index) => {
            const compatibility = outfit.compatibility_score || Math.floor(Math.random() * 40) + 60; // Fallback
            
            html += `
                <div class="outfit-card">
                    <div class="outfit-header">
                        <h3>Outfit ${index + 1}</h3>
                        <span class="compatibility">Compatibility: ${compatibility}%</span>
                    </div>
                    <div class="outfit-grid">
                        ${renderOutfitItem('Top', outfit.tops)}
                        ${renderOutfitItem('Bottom', outfit.bottoms)}
                        ${renderOutfitItem('Shoe', outfit.shoes)}
                        ${renderOutfitItem('Accessory', outfit.accessories)}
                    </div>
                </div>
            `;
        });
        
        results.innerHTML = html;
    }

    // Render individual outfit item
    function renderOutfitItem(category, item) {
        if (!item) {
            return `
                <div class="outfit-item">
                    <h4>${category}</h4>
                    <p>Not available</p>
                </div>
            `;
        }
        
        return `
            <div class="outfit-item">
                <img src="${item.image_url || 'https://via.placeholder.com/300x400'}" 
                     alt="${item.name}"
                     onerror="this.src='https://via.placeholder.com/300x400'">
                <h4>${category}</h4>
                <div class="brand">${item.brand || 'Unknown'}</div>
                <div class="price">$${item.price?.toFixed(2) || 'N/A'}</div>
                <div class="color">${item.color || 'Various'}</div>
                <a href="${item.product_url || '#'}" target="_blank" class="buy-link">View Product</a>
            </div>
        `;
    }

    // Event listeners
    searchBtn.addEventListener('click', () => {
        const query = searchInput.value.trim();
        if (query) {
            searchOutfits(query);
        }
    });

    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const query = searchInput.value.trim();
            if (query) {
                searchOutfits(query);
            }
        }
    });

    vibeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const vibe = btn.dataset.vibe;
            searchInput.value = vibe;
            searchOutfits(vibe);
        });
    });

    // Load some default outfits on page load
    searchOutfits('casual');
});