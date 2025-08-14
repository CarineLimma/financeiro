// Dados de exemplo
const meses = ["Janeiro","Fevereiro","Março","Abril","Maio"];
const receitaData = [500, 700, 800, 600, 900];
const despesaData = [300, 400, 500, 350, 450];

// Gráfico Receita
new Chart(document.getElementById('graficoReceita'), {
    type: 'bar',
    data: {
        labels: meses,
        datasets: [{
            label: 'Receita',
            data: receitaData,
            backgroundColor: 'rgba(5,3,107,0.8)',
            borderColor: 'rgba(5,3,107,1)',
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: { y: { beginAtZero: true } }
    }
});

// Gráfico Despesa
new Chart(document.getElementById('graficoDespesa'), {
    type: 'bar',
    data: {
        labels: meses,
        datasets: [{
            label: 'Despesa',
            data: despesaData,
            backgroundColor: 'rgba(245, 0, 0, 0.9)',
            borderColor: 'rgba(245, 0, 0, 0.9)',
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: { y: { beginAtZero: true } }
    }
});
