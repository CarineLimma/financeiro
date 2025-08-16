// ========================
// Dashboard Chart.js
// ========================

// Dados de exemplo - você pode substituir pelos valores do backend
const receitaData = {
    labels: ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio'],
    datasets: [{
        label: 'Receita',
        data: [500, 700, 800, 600, 900],
        backgroundColor: 'rgba(91, 43, 224, 0.6)',
        borderColor: 'rgba(91, 43, 224, 1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4
    }]
};

const despesaData = {
    labels: ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio'],
    datasets: [{
        label: 'Despesa',
        data: [300, 500, 400, 600, 700],
        backgroundColor: 'rgba(255, 99, 132, 0.6)',
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4
    }]
};

// Configuração do gráfico
const configReceita = {
    type: 'line',
    data: receitaData,
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
                labels: { color: '#333', font: { size: 14 } }
            },
            title: {
                display: true,
                text: 'Receita Mensal',
                color: '#333',
                font: { size: 18 }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: { color: '#333' }
            },
            x: {
                ticks: { color: '#333' }
            }
        }
    }
};

const configDespesa = {
    type: 'line',
    data: despesaData,
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
                labels: { color: '#333', font: { size: 14 } }
            },
            title: {
                display: true,
                text: 'Despesa Mensal',
                color: '#333',
                font: { size: 18 }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: { color: '#333' }
            },
            x: {
                ticks: { color: '#333' }
            }
        }
    }
};

window.addEventListener('DOMContentLoaded', () => {
    const receitaCanvas = document.getElementById('receitaChart').getContext('2d');
    new Chart(receitaCanvas, configReceita);

    const despesaCanvas = document.getElementById('despesaChart').getContext('2d');
    new Chart(despesaCanvas, configDespesa);
});
