from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from . import db
from .models import User, Client, Product, Sale, Supplier
from sqlalchemy.sql import func
from sqlalchemy import desc
from datetime import datetime
from .forms import ClientForm, ProductForm, ChangePasswordForm, ChangeEmailForm, DeleteAccountForm, SupplierForm
from flask_wtf import FlaskForm

main = Blueprint('main', __name__)

# ---------- PÁGINAS GERAIS E DASHBOARD ----------
@main.route('/')
def index():
    return redirect(url_for('main.dashboard'))

@main.route('/dashboard')
@login_required
def dashboard():
    clientes_count = Client.query.count()
    users_count = User.query.count()
    produtos_count = Product.query.count()
    fornecedores_count = Supplier.query.count()
    
    vendas_total = db.session.query(func.sum(Sale.total)).scalar() or 0
    ultimos_clientes = Client.query.order_by(Client.created_at.desc()).limit(5).all()
    ultimos_produtos = Product.query.order_by(Product.created_at.desc()).limit(5).all()
    ultimas_vendas = Sale.query.order_by(Sale.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                            clientes_count=clientes_count, 
                            users_count=users_count,
                            produtos_count=produtos_count,
                            vendas_total=vendas_total, 
                            ultimos_clientes=ultimos_clientes,
                            ultimos_produtos=ultimos_produtos,
                            ultimas_vendas=ultimas_vendas,
                            fornecedores_count=fornecedores_count)

# ---------- CLIENTES CRUD (AJUSTADO PARA PESQUISA) ----------
@main.route('/clientes')
@login_required
def clientes():
    search_query = request.args.get('search_query')
    if search_query:
        all_clients = Client.query.filter(
            Client.nome.ilike(f'%{search_query}%') | 
            Client.email.ilike(f'%{search_query}%')
        ).order_by(Client.nome).all()
    else:
        all_clients = Client.query.order_by(Client.nome).all()
    return render_template('clientes.html', clientes=all_clients, search_query=search_query)

@main.route('/clientes/novo', methods=['GET', 'POST'])
@login_required
def novo_cliente():
    form = ClientForm()
    if form.validate_on_submit():
        c = Client(
            nome=form.nome.data, 
            email=form.email.data, 
            telefone=form.telefone.data, 
            notas=form.notas.data
        )
        db.session.add(c)
        db.session.commit()
        flash('Cliente criado com sucesso', 'success')
        return redirect(url_for('main.clientes'))
    return render_template('client_form.html', form=form, client=None)

@main.route('/clientes/editar/<int:cid>', methods=['GET', 'POST'])
@login_required
def editar_cliente(cid):
    client = Client.query.get_or_404(cid)
    form = ClientForm(obj=client)
    if form.validate_on_submit():
        form.populate_obj(client)
        db.session.commit()
        flash('Cliente atualizado', 'success')
        return redirect(url_for('main.clientes'))
    return render_template('client_form.html', form=form, client=client)

@main.route('/clientes/deletar/<int:cid>', methods=['POST'])
@login_required
def deletar_cliente(cid):
    client = Client.query.get_or_404(cid)
    db.session.delete(client)
    db.session.commit()
    flash('Cliente removido', 'success')
    return redirect(url_for('main.clientes'))

# ---------- PRODUTOS CRUD (AJUSTADO PARA PESQUISA) ----------
@main.route('/produtos')
@login_required
def produtos():
    search_query = request.args.get('search_query')
    if search_query:
        all_products = Product.query.filter(Product.nome.ilike(f'%{search_query}%')).order_by(Product.nome).all()
    else:
        all_products = Product.query.order_by(Product.nome).all()
    return render_template('products.html', produtos=all_products, search_query=search_query)

@main.route('/produtos/novo', methods=['GET', 'POST'])
@login_required
def novo_produto():
    form = ProductForm()
    form.fornecedor.choices = [(s.id, s.nome) for s in Supplier.query.order_by(Supplier.nome).all()]
    
    if form.validate_on_submit():
        p = Product(
            nome=form.nome.data, 
            preco=form.preco.data, 
            descricao=form.descricao.data, 
            fornecedor_id=form.fornecedor.data,
            estoque=form.estoque.data
        )
        db.session.add(p)
        db.session.commit()
        flash('Produto criado com sucesso', 'success')
        return redirect(url_for('main.produtos'))
    
    return render_template('product_form.html', form=form, produto=None)

@main.route('/produtos/editar/<int:pid>', methods=['GET', 'POST'])
@login_required
def editar_produto(pid):
    produto = Product.query.get_or_404(pid)
    form = ProductForm(obj=produto)
    form.fornecedor.choices = [(s.id, s.nome) for s in Supplier.query.order_by(Supplier.nome).all()]
    
    if form.validate_on_submit():
        produto.nome = form.nome.data
        produto.preco = form.preco.data
        produto.descricao = form.descricao.data
        produto.estoque = form.estoque.data
        produto.fornecedor_id = form.fornecedor.data
        db.session.commit()
        flash('Produto atualizado', 'success')
        return redirect(url_for('main.produtos'))
    
    return render_template('product_form.html', form=form, produto=produto)

@main.route('/produtos/deletar/<int:pid>', methods=['POST'])
@login_required
def deletar_produto(pid):
    produto = Product.query.get_or_404(pid)
    db.session.delete(produto)
    db.session.commit()
    flash('Produto removido', 'success')
    return redirect(url_for('main.produtos'))

# ---------- VENDAS CRUD (CORREÇÃO DE ERRO) ----------
@main.route('/vendas')
@login_required
def vendas():
    all_sales = Sale.query.order_by(Sale.created_at.desc()).all()
    return render_template('sales.html', vendas=all_sales)

@main.route('/vendas/nova', methods=['GET', 'POST'])
@login_required
def nova_venda():
    class SaleForm(FlaskForm):
        pass
        
    form = SaleForm()
    clientes = Client.query.order_by(Client.nome).all()
    produtos = Product.query.order_by(Product.nome).filter(Product.estoque > 0).all()
    
    if request.method == 'POST':
        cliente_id = request.form.get('cliente_id')
        produto_id = request.form.get('produto_id')
        quantidade = request.form.get('quantidade')

        if not cliente_id or not produto_id or not quantidade:
            flash('Todos os campos são obrigatórios', 'warning')
            return redirect(url_for('main.nova_venda'))

        try:
            quantidade = int(quantidade)
            if quantidade <= 0:
                flash('A quantidade deve ser maior que zero', 'danger')
                return redirect(url_for('main.nova_venda'))
        except ValueError:
            flash('A quantidade deve ser um número válido', 'danger')
            return redirect(url_for('main.nova_venda'))

        produto = Product.query.get(produto_id)
        if not produto:
            flash('Produto não encontrado', 'danger')
            return redirect(url_for('main.nova_venda'))
        
        if produto.estoque < quantidade:
            flash(f'Estoque insuficiente. Disponível: {produto.estoque}', 'danger')
            return redirect(url_for('main.nova_venda'))
        
        produto.estoque -= quantidade

        total = produto.preco * quantidade
        
        venda = Sale(cliente_id=cliente_id, produto_id=produto_id, quantidade=quantidade, total=total)
        db.session.add(venda)
        db.session.commit()
        flash('Venda registrada com sucesso', 'success')
        return redirect(url_for('main.vendas'))
        
    return render_template('sale_form.html', clientes=clientes, produtos=produtos, form=form)

@main.route('/vendas/deletar/<int:sid>', methods=['POST'])
@login_required
def deletar_venda(sid):
    venda = Sale.query.get_or_404(sid)
    db.session.delete(venda)
    db.session.commit()
    flash('Venda removida', 'success')
    return redirect(url_for('main.vendas'))

# ---------- FORNECEDORES CRUD (AJUSTADO PARA PESQUISA) ----------
@main.route('/fornecedores')
@login_required
def fornecedores():
    search_query = request.args.get('search_query')
    if search_query:
        all_suppliers = Supplier.query.filter(Supplier.nome.ilike(f'%{search_query}%')).order_by(Supplier.nome).all()
    else:
        all_suppliers = Supplier.query.order_by(Supplier.nome).all()
    return render_template('suppliers.html', fornecedores=all_suppliers, search_query=search_query)

@main.route('/fornecedores/novo', methods=['GET', 'POST'])
@login_required
def novo_fornecedor():
    form = SupplierForm()
    if form.validate_on_submit():
        s = Supplier(
            nome=form.nome.data,
            email=form.email.data,
            telefone=form.telefone.data,
            endereco=form.endereco.data
        )
        db.session.add(s)
        db.session.commit()
        flash('Fornecedor criado com sucesso', 'success')
        return redirect(url_for('main.fornecedores'))
    
    return render_template('supplier_form.html', fornecedor=None, form=form)

@main.route('/fornecedores/editar/<int:sid>', methods=['GET', 'POST'])
@login_required
def editar_fornecedor(sid):
    fornecedor = Supplier.query.get_or_404(sid)
    form = SupplierForm(obj=fornecedor)
    
    if form.validate_on_submit():
        form.populate_obj(fornecedor)
        db.session.commit()
        flash('Fornecedor atualizado', 'success')
        return redirect(url_for('main.fornecedores'))
        
    return render_template('supplier_form.html', fornecedor=fornecedor, form=form)

@main.route('/fornecedores/deletar/<int:sid>', methods=['POST'])
@login_required
def deletar_fornecedor(sid):
    fornecedor = Supplier.query.get_or_404(sid)
    if fornecedor.produtos:
        flash('Não é possível excluir fornecedor com produtos associados.', 'danger')
        return redirect(url_for('main.fornecedores'))
    db.session.delete(fornecedor)
    db.session.commit()
    flash('Fornecedor removido', 'success')
    return redirect(url_for('main.fornecedores'))

# ---------- RELATÓRIOS E CONFIGURAÇÕES (AJUSTADO PARA FILTRO DE DATA) ----------
@main.route('/relatorios')
@login_required
def relatorios():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query_base = Sale.query

    if start_date:
        query_base = query_base.filter(Sale.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query_base = query_base.filter(Sale.created_at <= datetime.strptime(end_date, '%Y-%m-%d'))
    
    vendas_mensais = query_base.with_entities(
        func.strftime('%Y-%m', Sale.created_at).label('mes'),
        func.sum(Sale.total).label('total_mes')
    ).group_by('mes').order_by('mes').all()

    produtos_mais_vendidos = query_base.with_entities(
        Product.nome,
        func.sum(Sale.quantidade).label('total_quantidade')
    ).join(Product).group_by(Product.nome).order_by(desc('total_quantidade')).limit(5).all()

    clientes_top = query_base.with_entities(
        Client.nome,
        func.sum(Sale.total).label('total_gasto')
    ).join(Client).group_by(Client.nome).order_by(desc('total_gasto')).limit(5).all()

    return render_template('relatorios.html', 
                            vendas_mensais=vendas_mensais,
                            produtos_mais_vendidos=produtos_mais_vendidos,
                            clientes_top=clientes_top,
                            start_date=start_date,
                            end_date=end_date)


@main.route('/configuracoes', methods=['GET', 'POST'])
@login_required
def configuracoes():
    password_form = ChangePasswordForm()
    email_form = ChangeEmailForm()
    delete_form = DeleteAccountForm()
    user = User.query.get(current_user.id)
    
    if password_form.validate_on_submit() and password_form.submit.data:
        user.set_password(password_form.nova_senha.data)
        db.session.commit()
        flash('Sua senha foi atualizada com sucesso!', 'success')
        return redirect(url_for('main.configuracoes'))

    if email_form.validate_on_submit() and email_form.submit.data:
        if User.query.filter_by(email=email_form.email.data).first():
            flash('Este e-mail já está em uso.', 'danger')
        else:
            user.email = email_form.email.data
            db.session.commit()
            flash('Seu e-mail foi atualizado com sucesso!', 'success')
        return redirect(url_for('main.configuracoes'))

    if delete_form.validate_on_submit() and delete_form.submit.data:
        if current_user.id == 1:
            flash('O usuário admin não pode ser deletado.', 'danger')
        else:
            db.session.delete(user)
            db.session.commit()
            flash('Sua conta foi deletada com sucesso.', 'info')
            return redirect(url_for('main.login'))
            
    return render_template('configuracoes.html', password_form=password_form, email_form=email_form, delete_form=delete_form)


# ---------- GESTÃO DE USUÁRIOS ----------
@main.route('/users')
@login_required
def users():
    all_users = User.query.all()
    return render_template('users.html', users=all_users)

@main.route('/users/delete/<int:uid>', methods=['POST'])
@login_required
def delete_user(uid):
    if uid == current_user.id:
        flash('Você não pode excluir a sua própria conta.', 'danger')
        return redirect(url_for('main.users'))
    
    user_to_delete = User.query.get_or_404(uid)
    db.session.delete(user_to_delete)
    db.session.commit()
    flash('Usuário removido com sucesso.', 'success')
    return redirect(url_for('main.users'))

# ---------- AUTENTICAÇÃO ----------
@main.route('/login', methods=['GET', 'POST'])
def login():
    class LoginForm(FlaskForm):
        pass

    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logado com sucesso', 'success')
            return redirect(url_for('main.dashboard'))
        flash('Usuário ou senha inválidos', 'danger')
    return render_template('login.html', form=form)

@main.route('/register', methods=['GET', 'POST'])
def register():
    class RegisterForm(FlaskForm):
        pass

    form = RegisterForm()
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if not username or not email or not password:
            flash('Preencha todos os campos', 'warning')
            return redirect(url_for('main.register'))
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Usuário ou e-mail já existe', 'warning')
            return redirect(url_for('main.register'))
        u = User(username=username, email=email)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        flash('Cadastro concluído. Faça login!', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu', 'info')
    return redirect(url_for('main.login'))