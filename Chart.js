var ctx = document.getElementById('expenseChart').getContext('2d');
var expenseChart = new Chart(ctx, {
    type: 'pie',
    data: {
        labels: Object.keys(chartData),  // Dynamic labels from category keys
        datasets: [{
            data: Object.values(chartData),  // Dynamic data from category values
            backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56'],
        }]
    },
});
