// Function to fetch dashboard data
async function fetchDashboardData() {
    try {
        const response = await fetch('/api/admin/dashboard-data/');
        const data = await response.json();
        
        // Update statistics
        document.getElementById('orderCount').textContent = data.totalOrders;
        document.getElementById('userCount').textContent = data.totalUsers;
        
        // Update recent orders
        const recentOrdersContainer = document.getElementById('recentOrders');
        recentOrdersContainer.innerHTML = data.recentOrders
            .map(order => `
                <div class="order-item">
                    <p>Order #${order.id} - ${order.date}</p>
                    <p>Customer: ${order.customerName}</p>
                    <p>Amount: $${order.amount}</p>
                </div>
            `).join('');
    } catch (error) {
        console.error('Error fetching dashboard data:', error);
    }
}

// Fetch data immediately and then every 5 minutes
fetchDashboardData();
setInterval(fetchDashboardData, 300000);
