// Initialize revenue chart
const ctx = document.getElementById('revenueChart').getContext('2d');
const revenueChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
            label: 'Monthly Revenue',
            data: [1200, 1900, 3000, 2100, 2800, 3200],
            borderColor: '#4e73df',
            tension: 0.4,
            fill: {
                target: 'origin',
                above: 'rgba(78, 115, 223, 0.1)'
            }
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: 'Revenue Overview'
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: {
                    borderDash: [2],
                    color: 'rgba(0, 0, 0, 0.1)'
                }
            },
            x: {
                grid: {
                    display: false
                }
            }
        }
    }
});

// Enhanced chart options
const gradientFill = ctx.createLinearGradient(0, 0, 0, 400);
gradientFill.addColorStop(0, 'rgba(108, 92, 231, 0.3)');
gradientFill.addColorStop(1, 'rgba(108, 92, 231, 0)');

revenueChart.data.datasets[0].backgroundColor = gradientFill;
revenueChart.options.plugins.tooltip = {
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    backdropFilter: 'blur(10px)',
    borderColor: 'rgba(255, 255, 255, 0.1)',
    borderWidth: 1,
    padding: 10,
};

// Add click handlers for sidebar navigation
document.querySelectorAll('.nav-links li').forEach(item => {
    item.addEventListener('click', function() {
        document.querySelector('.nav-links li.active').classList.remove('active');
        this.classList.add('active');
    });
});

// Add hover effect for cards
document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('mouseover', function() {
        this.style.transform = 'translateY(-5px)';
    });
    
    card.addEventListener('mouseout', function() {
        this.style.transform = 'translateY(0)';
    });
});

// Animate numbers
document.querySelectorAll('.counter').forEach(counter => {
    const target = parseInt(counter.innerText);
    const duration = 2000;
    let start = 0;
    const increment = target / (duration / 16);
    
    const updateCounter = () => {
        start += increment;
        counter.innerText = Math.floor(start);
        
        if(start < target) {
            requestAnimationFrame(updateCounter);
        } else {
            counter.innerText = target;
        }
    };
    
    updateCounter();
});

// Dark/Light theme toggle
const themeToggle = document.querySelector('.theme-toggle');
themeToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark-theme');
    themeToggle.querySelector('i').classList.toggle('fa-sun');
    themeToggle.querySelector('i').classList.toggle('fa-moon');
});
