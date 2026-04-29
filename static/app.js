document.addEventListener('DOMContentLoaded', () => {
    // State
    const state = {
        selectedConcerns: new Set()
    };

    // DOM Elements
    const skinTypeSelect = document.getElementById('skin_type');
    const concernsContainer = document.getElementById('concerns-container');
    const form = document.getElementById('recommend-form');
    const submitBtn = form.querySelector('.cta-button');
    const spinner = document.getElementById('loading-spinner');
    const btnText = submitBtn.querySelector('span');
    const resultsSection = document.getElementById('results-section');
    const routineContainer = document.getElementById('routine-container');
    const totalCostEl = document.getElementById('total-cost');

    // 1. Fetch Metadata
    async function loadMeta() {
        try {
            const res = await fetch('/api/meta');
            if (res.ok) {
                const data = await res.json();
                
                // Populate Skin Types
                skinTypeSelect.innerHTML = '<option value="" disabled selected>Select your skin type</option>';
                data.skin_types.forEach(st => {
                    const opt = document.createElement('option');
                    opt.value = st.id;
                    opt.textContent = st.name;
                    skinTypeSelect.appendChild(opt);
                });

                // Populate Concerns as Chips
                concernsContainer.innerHTML = '';
                data.concerns.forEach(c => {
                    const chip = document.createElement('span');
                    chip.className = 'chip';
                    chip.textContent = c.name;
                    chip.dataset.id = c.id;
                    
                    // Chip Click Handler
                    chip.addEventListener('click', () => {
                        if (state.selectedConcerns.has(c.id)) {
                            state.selectedConcerns.delete(c.id);
                            chip.classList.remove('active');
                        } else {
                            state.selectedConcerns.add(c.id);
                            chip.classList.add('active');
                        }
                    });
                    
                    concernsContainer.appendChild(chip);
                });
            } else {
                concernsContainer.innerHTML = '<span class="loading-text">Error loading data. Is the backend running?</span>';
            }
        } catch (error) {
            console.error('Error fetching meta:', error);
            concernsContainer.innerHTML = '<span class="loading-text">Error connecting to server.</span>';
        }
    }

    // 2. Handle Form Submit
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const skin_type_id = skinTypeSelect.value;
        const budget = parseFloat(document.getElementById('budget').value);
        
        if (state.selectedConcerns.size === 0) {
            alert('Please select at least one skin concern.');
            return;
        }

        // UI Loading State
        btnText.textContent = 'Generating...';
        spinner.classList.remove('hidden');
        submitBtn.disabled = true;
        
        resultsSection.classList.remove('visible');

        try {
            const res = await fetch('/api/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    skin_type_id: skin_type_id,
                    concern_ids: Array.from(state.selectedConcerns),
                    budget: budget
                })
            });

            if (res.ok) {
                const recommendations = await res.json();
                renderResults(recommendations);
            } else {
                const err = await res.json();
                alert('Error: ' + (err.detail || 'Failed to generate recommendation.'));
            }
        } catch (error) {
            console.error('Submit error:', error);
            alert('Network error. Be sure the backend and database are running.');
        } finally {
            // Restore UI State
            btnText.textContent = 'Generate Routine';
            spinner.classList.hidden = true;
            submitBtn.disabled = false;
        }
    });

    // 3. Render Results
    function renderResults(products) {
        routineContainer.innerHTML = '';
        let totalCost = 0;

        if (products.length === 0) {
            routineContainer.innerHTML = '<p>No products found within this budget. Try increasing it.</p>';
            totalCostEl.textContent = 'LKR 0';
            resultsSection.classList.add('visible');
            return;
        }

        products.forEach(p => {
            totalCost += p.price;
            
            const card = document.createElement('div');
            card.className = 'card';
            
            card.innerHTML = `
                <div class="score">Match: ${Math.round(p.score * 100)}%</div>
                <div class="category">${p.category}</div>
                <div class="name">${p.name}</div>
                <div class="brand">${p.brand}</div>
                <div class="price">LKR ${p.price.toLocaleString()}</div>
                <div class="reasoning">${p.reasoning}</div>
            `;
            
            routineContainer.appendChild(card);
        });

        totalCostEl.textContent = \`LKR \${totalCost.toLocaleString()}\`;
        
        // Show section
        setTimeout(() => {
            resultsSection.classList.add('visible');
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
    }

    // Init
    loadMeta();
});
