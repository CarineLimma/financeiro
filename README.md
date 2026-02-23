 ## 🧮 Sistema de Controle Financeiro Pessoal e Empresarial

Um sistema completo de controle financeiro desenvolvido em Flask, com interface web moderna, responsiva e fácil de usar. Permite gerenciar receitas, despesas, histórico de transações, dashboard com gráficos, exportação de dados e mais.
<strong> Saiba mais:</strong>(https://financeiro-5tia.onrender.com/login)
## 📝 Funcionalidades

- Autenticação e Usuários

- Registro de novos usuários.

- Login seguro com verificação de senha.

- Recuperação de senha via e-mail com token temporário.

- Transações Financeiras

- Cadastro de receitas e despesas.

- Suporte a transações recorrentes (mensais, semanais, etc.).

- Histórico completo de transações com filtros por data, tipo e categoria.

- Dashboard

-Visualização de saldo atual.

- Gráficos interativos (barras) mostrando receitas e despesas.

- Layout responsivo, com gráficos lado a lado em telas grandes e empilhados em telas pequenas.

- Exportação de Dados

- Exportar transações para PDF ou Excel.

- Ideal para relatórios financeiros pessoais ou empresariais.

- Integração e Estrutura

- Banco de dados SQLite (database.db).

## Tabelas:

- usuarios: informações dos usuários (id, email, senha, nome…).

- transacoes: informações das transações (id, tipo, valor, categoria, data, usuário…).

- Suporte para múltiplos usuários, cada um com suas próprias transações.

- Layout e Estilo

- Interface moderna e responsiva usando Bootstrap e CSS customizado.

- Menu de navegação fixo no topo com links para Dashboard, Receita, Despesa, Histórico, Agendar Transação e Sair.

- Cards limpos e minimalistas para visualização de dados.

## 🛠️ Tecnologias Utilizadas

- Python 3.x

- Flask

- Flask-Mail (para envio de e-mails de recuperação de senha)

- SQLite (banco de dados)

- Bootstrap 5

- Chart.js (gráficos)

- HTML5, CSS3, JavaScript

Jinja2 (templates)
