document.addEventListener('DOMContentLoaded', () => {
    // Check if we are on the profile page
    const profileContainer = document.querySelector('.profile-container');
    if (!profileContainer) return;

    console.log('Initializing profile page data fetch...');

    async function fetchStats() {
        try {
            const response = await fetch('/api/profile/stats');
            if (!response.ok) throw new Error('Failed to fetch stats');
            const data = await response.json();

            document.getElementById('total-spent').textContent = `₹${data.total_spent.toFixed(2)}`;
            document.getElementById('tx-count').textContent = data.tx_count;
            document.getElementById('top-category').textContent = data.top_category;
        } catch (error) {
            console.error('Error fetching stats:', error);
        }
    }

    async function fetchCategories() {
        try {
            const response = await fetch('/api/profile/categories');
            if (!response.ok) throw new Error('Failed to fetch categories');
            const data = await response.json();

            const container = document.getElementById('category-breakdown');
            container.innerHTML = ''; // Clear existing

            if (data.length === 0) {
                container.innerHTML = '<p class="empty-msg">No category data available</p>';
                return;
            }

            data.forEach(cat => {
                const row = document.createElement('div');
                row.className = 'cat-row';
                row.innerHTML = `
                    <div class="cat-info">
                        <span class="cat-name">${cat.name}</span>
                        <span class="cat-val">₹${cat.amount.toFixed(2)}</span>
                    </div>
                    <div class="cat-bar-container">
                        <div class="cat-bar-fill" style="width: ${cat.percentage}%"></div>
                    </div>
                `;
                container.appendChild(row);
            });
        } catch (error) {
            console.error('Error fetching categories:', error);
        }
    }

    async function fetchTransactions() {
        try {
            const response = await fetch('/api/profile/transactions');
            if (!response.ok) throw new Error('Failed to fetch transactions');
            const data = await response.json();

            const tbody = document.getElementById('tx-body');
            tbody.innerHTML = ''; // Clear existing

            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;">No transactions found</td></tr>';
                return;
            }

            data.forEach(tx => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${tx.date}</td>
                    <td>${tx.description}</td>
                    <td><span class="cat-badge">${tx.category}</span></td>
                    <td class="tx-amt">₹${tx.amount.toFixed(2)}</td>
                `;
                tbody.appendChild(row);
            });
        } catch (error) {
            console.error('Error fetching transactions:', error);
        }
    }

    // Run all fetches
    Promise.all([fetchStats(), fetchCategories(), fetchTransactions()])
        .then(() => console.log('Profile data loaded successfully'))
        .catch(err => console.error('Error loading profile data:', err));
});
