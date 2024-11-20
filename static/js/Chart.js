// Select the canvas context
const ctx = document.getElementById('predictionChart').getContext('2d');

// Data variables
const predictionTimesData = JSON.parse(document.getElementById('predictionTimesData').textContent);
const actualValuesData = JSON.parse(document.getElementById('actualValuesData').textContent);
const predictedValuesData = JSON.parse(document.getElementById('predictedValuesData').textContent);

// Initialize the chart
const predictionChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: predictionTimesData, // X-axis labels (time)
        datasets: [
            {
                label: 'Actual Data',
                data: actualValuesData,
                borderColor: 'rgba(75, 192, 192, 1)',
                fill: false,
            },
            {
                label: 'Predicted Data',
                data: predictedValuesData,
                borderColor: 'rgba(255, 99, 132, 1)',
                fill: false,
            }
        ]
    },
    options: {
        responsive: true,
        plugins: {
            title: {
                display: true,
                text: 'Prediction vs Actual Data'
            }
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Time'
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'Value'
                }
            }
        }
    }
});
