# 📈 Sistema de Gestão Comercial

Este é um sistema de gestão comercial web completo, desenvolvido com Python e o framework Flask. O projeto foi criado como parte de meu portfólio para demonstrar habilidades em desenvolvimento back-end, manipulação de banco de dados (SQLite), e criação de interfaces de usuário com HTML, CSS e Bootstrap.

---

## 🚀 Funcionalidades

O sistema oferece as seguintes funcionalidades principais:

- **Dashboard**: Uma visão geral com métricas importantes, como número de clientes, produtos, usuários e o total de vendas.
- **Clientes**: CRUD (Criação, Leitura, Atualização e Exclusão) completo para gerenciar clientes.
- **Produtos**: CRUD completo com controle de estoque e associação a fornecedores.
- **Vendas**: Registro de vendas, debitando a quantidade do estoque do produto.
- **Fornecedores**: CRUD para gerenciamento de fornecedores.
- **Relatórios**: Página de relatórios com gráficos e tabelas de vendas mensais, produtos mais vendidos e top clientes, com filtro por período.
- **Autenticação de Usuários**: Sistema de login, cadastro, gerenciamento e exclusão de contas, com validação de formulários para garantir segurança.
- **Pesquisa**: Campos de busca em cada página de listagem (Clientes, Produtos e Fornecedores) para facilitar a localização de dados.

---

## 💻 Tecnologias Utilizadas

- **Backend**:
  - Python
  - Flask
  - Flask-SQLAlchemy (para ORM e banco de dados SQLite)
  - Flask-Login (para gestão de sessões de usuário)
  - Flask-WTF (para formulários e validação)
  - Werkzeug (para segurança de senhas)
  - SQLite (banco de dados leve e eficiente)
- **Frontend**:
  - HTML5
  - Bootstrap 5 (para um design responsivo e moderno)
  - CSS3

---

## ⚙️ Como Instalar e Rodar o Projeto

Siga os passos abaixo para configurar e executar o projeto em seu ambiente local.

### Pré-requisitos
Certifique-se de ter o Python 3 instalado.

### 1. Clonar o Repositório
```bash
git clone [https://github.com/SeuUsuario/SeuRepositorio.git](https://github.com/SeuUsuario/SeuRepositorio.git)
cd SeuRepositorio