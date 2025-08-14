// Dados de exemplo - você pode substituir pelos valores do backend
const receitaData = {
    labels: ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio'],
    datasets: [{
        label: 'Receita',
        data: [500, 700, 800, 600, 900],
        backgroundColor: '#05036bff'
    }]
};

const despesaData = {
    labels: ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio'],
    datasets: [{
        label: 'Despesa',
        data: [300, 400, 500, 350, 450],
        backgroundColor: '#ff0000ff'
    }]
};

// Função para calcular total
function calcularTotal(dados) {
    return dados.datasets[0].data.reduce((a, b) => a + b, 0);
}

// Atualiza o saldo nos cards
document.querySelector('.card-saldo').textContent = `R$ ${calcularTotal(receitaData)}`;

// Se tiver mais de um card-saldo, atualizamos manualmente
const saldoCards = document.querySelectorAll('.card-saldo');
saldoCards[0].textContent = `R$ ${calcularTotal(receitaData)}`; // Receita
saldoCards[1].textContent = `R$ ${calcularTotal(despesaData)}`; // Despesa

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
