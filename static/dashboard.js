// Dados de exemplo - você pode substituir pelos valores do backend
const receitaData = {
    labels: ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio'],
    datasets: [{
        label: 'Receita',
        data: [500, 700, 800, 600, 900],
        backgroundColor: '#5b2be0'
    }]
};

const despesaData = {
    labels: ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio'],
    datasets: [{
        label: 'Despesa',
        data: [300, 400, 500, 350, 450],
        backgroundColor: '#00c6ff'
    }]
};

// Configurações dos gráficos
const configReceita = {
    type: 'bar',
    data: receitaData,
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
            y: { beginAtZero: true },
        }
    }
};

const configDespesa = {
    type: 'bar',
    data: despesaData,
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
            y: { beginAtZero: true },
        }
    }
};

// Renderizando os gráficos
const receitaChart = new Chart(
    document.getElementById('receita-chart'),
    configReceita
);

const despesaChart = new Chart(
    document.getElementById('despesa-chart'),
    configDespesa
);
