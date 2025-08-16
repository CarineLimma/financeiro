// ========================
// Dados de exemplo
const receitaData = {
    labels: ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio'],
    datasets: [{
        label: 'Receita',
        data: [500, 700, 800, 600, 900],
        backgroundColor: 'rgba(19, 2, 117, 0.2)',
        borderColor: 'rgba(19, 2, 117, 1)',
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
        backgroundColor: 'rgba(204, 0, 0, 0.2)',
        borderColor: 'rgba(204, 0, 0, 0.99)',
        borderWidth: 2,
        fill: true,
        tension: 0.4
    }]
};

// Configuração do gráfico Receita
const configReceita = {
    type: 'line',
    data: receitaData,
    options: {
        responsive: true,
        maintainAspectRatio: false,
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

// Configuração do gráfico Despesa
const configDespesa = {
    type: 'line',
    data: despesaData,
    options: {
        responsive: true,
        maintainAspectRatio: false,
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

// ========================
// Inicialização após carregar o DOM
window.addEventListener('DOMContentLoaded', () => {
    const receitaCanvas = document.getElementById('graficoReceita').getContext('2d');
    new Chart(receitaCanvas, configReceita);

    const despesaCanvas = document.getElementById('graficoDespesa').getContext('2d');
    new Chart(despesaCanvas, configDespesa);
});
