from flask import Flask, render_template, request, redirect, url_for, session
import uuid
import json
import os

app = Flask(__name__)

app.secret_key = "fc_company"

CARROS_FILE = "database/carros_cadastrados.json"
CAMBIOS_FILE = "database/cambio.json"
MARCAS_FILE = "database/marca.json"
TIPO_COMBUSTIVEL_FILE = "database/tipo_combustivel.json"
CORES_FILE = "database/cor.json"
ANOS_FILE = "database/anos.json"
USUARIOS_FILE = "database/usuarios.json"

def carregar_json(arquivo):
    if not os.path.exists(arquivo):
        return []
    
    with open(arquivo, "r", encoding="utf-8") as f:
        return json.load(f)
    
def salvar_json(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

carros = carregar_json(CARROS_FILE)
cambios = carregar_json(CAMBIOS_FILE)
marcas = carregar_json(MARCAS_FILE)
combustiveis = carregar_json(TIPO_COMBUSTIVEL_FILE)
cores = carregar_json(CORES_FILE)
anos = carregar_json(ANOS_FILE)
usuarios = carregar_json(USUARIOS_FILE)

if not cambios:
    cambios = [
        "Automático",
        "Manual"
    ]

    salvar_json(CAMBIOS_FILE, cambios)

if not marcas:
    marcas = [
        "Chevrolet",
        "Fiat", 
        "Ford", 
        "Hyundai",
        "Toyota",
        "Volkswagen",
        "Ferrari"
    ]

    salvar_json(MARCAS_FILE, marcas)

if not combustiveis:
    combustiveis = [
        "Gasolina",
        "Etanol",
        "Diesel",
        "Híbrido",
        "Elétrico"
    ]

    salvar_json(TIPO_COMBUSTIVEL_FILE, combustiveis)

if not cores:
    cores = [
        "Branco",
        "Preto",
        "Prata",
        "Cinza",
        "Vermelho"
    ]

    salvar_json(CORES_FILE, cores)

def usuario_logado():
    return session.get("usuario")

def gerar_id():
    return str(uuid.uuid4())

def buscar_carro(id):
    return next((carro for carro in carros if carro["id"] == id), None)

@app.route("/")
def home():
    return render_template("home.html")
    
@app.route("/login", methods=["GET", "POST"])
def login():

    erro = None

    if request.method == "POST":

        usuario = request.form.get("usuario")
        senha = request.form.get("senha")

        if usuario:
            usuario = usuario.strip()
        if senha:
            senha = senha.strip()

        for user in usuarios:

            if (
                user["usuario"] == usuario
                and
                user["senha"] == senha
            ):

                session["usuario"] = usuario

                return redirect(url_for("carros_page"))

        erro = "Usuário ou senha inválidos"

    return render_template(
        "login.html",
        erro=erro
    )
    
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():

    erro = None

    if request.method == "POST":

        usuario = request.form.get("usuario")
        senha = request.form.get("senha")

        if usuario:
            usuario = usuario.strip()
        if senha:
            senha = senha.strip()

        for user in usuarios:

            if user["usuario"] == usuario:

                erro = "Usuário já existe"

                return render_template(
                    "cadastro.html",
                    erro=erro
                )

        usuarios.append({
            "usuario": usuario,
            "senha": senha
        })

        salvar_json(
            USUARIOS_FILE,
            usuarios
        )

        return redirect(url_for("home"))

    return render_template(
        "cadastro.html",
        erro=erro
    )

@app.route("/carros", methods=["GET"])
@app.route("/carros", methods=["GET"])
def carros_page():

    if not usuario_logado():
        return redirect(url_for("login"))
    ano = request.args.get("ano")
    cambio = request.args.get("cambio")
    marca = request.args.get("marca")
    combustivel = request.args.get("combustivel")
    cor = request.args.get("cor")

    carros_filtrados = carros

    if ano:
        carros_filtrados = [
            carro for carro in carros_filtrados
            if carro["ano"] == ano
        ]

    if cambio:
        carros_filtrados = [
            carro for carro in carros_filtrados
            if carro["cambio"] == cambio
        ]
    
    if marca:
        carros_filtrados = [
            carro for carro in carros_filtrados
            if carro["marca"] == marca
        ]
    
    if combustivel:
        carros_filtrados = [
            carro for carro in carros_filtrados
            if carro["combustivel"] == combustivel
        ]
    
    if cor:
        carros_filtrados = [
            carro for carro in carros_filtrados
            if carro["cor"] == cor
        ]
    
    return render_template(
        "carros.html",
        anos = anos,
        cores = cores,
        carros = carros_filtrados,
        cambios = cambios,
        marcas = marcas,
        combustiveis = combustiveis
    )

@app.route("/cadastrar", methods=["POST"])
def cadastrar():

    nome = request.form.get("nome")
    ano = request.form.get("ano")
    preco = request.form.get("preco")
    cor = request.form.get("cor")
    cambio = request.form.get("cambio")
    marca = request.form.get("marca")
    combustivel = request.form.get("combustivel")

    erro_nome = None
    erro_preco = None

    if nome:
        nome = nome.strip()
        if len(nome) < 10:
            erro_nome = "Nome inválido. O nome deve ter pelo menos 10 caracteres. Tente novamente!"
            nome = None 

    if preco:
        try:
            preco_digitado = float(preco)
            if preco_digitado <= 5000:
                erro_preco = "O preço digitado é inválido. O valor mínimo é de R$ 5.000,00."
                preco = None

            elif preco_digitado > 1000000:
                erro_preco = "O preço digitado é inválido. O valor máximo é de R$ 1.000.000,00"
                preco = None

        except ValueError:
            erro_preco = "O valor digitado é inválido. O preço deve ser um número. Tente novamente!"
            preco = None

    if nome and preco:
        if not ano:
            ano = "Não informado"
        if not cor:
            cor = "Não informada"
        if not cambio:
            cambio = "Não informado"
        if not marca:
            marca = "Não informada"
        if not combustivel:
            combustivel = "Não informado"
            
        carros.append({
            "id": gerar_id(),
            "nome": nome,
            "ano": ano,
            "preco": preco,
            "cor": cor,
            "cambio": cambio,
            "marca": marca,
            "combustivel": combustivel,
        }) 

        salvar_json(CARROS_FILE, carros)
        return redirect(url_for("carros_page"))
    
    return render_template(
        "carros.html",
        anos=anos,
        cores=cores,
        cambios=cambios,
        marcas=marcas,
        combustiveis=combustiveis,
        carros=carros,
        erro_nome=erro_nome,
        erro_preco=erro_preco,

        valor_nome=nome,
        valor_ano=ano,
        valor_preco=preco,
        valor_cor=cor,
        valor_cambio=cambio,
        valor_marca=marca,
        valor_combustivel=combustivel
    )

@app.route("/deletar/<string:id>")
def deletar(id):
    carro = buscar_carro(id)
    if carro:
        carros.remove(carro)

        salvar_json(CARROS_FILE, carros)
    return redirect(url_for("carros_page"))

@app.route("/editar/<string:id>", methods=["GET", "POST"])
def editar(id):

    carro = buscar_carro(id)

    if not carro:
        return redirect(url_for("carros_page"))

    erro_nome = None
    erro_preco = None

    if request.method == "POST":

        nome = request.form.get("nome")
        ano = request.form.get("ano")
        preco = request.form.get("preco")
        cor = request.form.get("cor")
        cambio = request.form.get("cambio")
        marca = request.form.get("marca")
        combustivel = request.form.get("combustivel")

        if nome:
            nome = nome.strip()
            if len(nome) < 10:
                erro_nome = "Nome inválido. O nome deve ter pelo menos 10 caracteres. Tente novamente!"
                nome = None 

        if preco:
            try:
                preco_digitado = float(preco)
                if preco_digitado <= 5000:
                    erro_preco = "O preço digitado é inválido. O valor mínimo é de R$ 5.000,00."
                    preco = None

                elif preco_digitado > 1000000:
                    erro_preco = "O preço digitado é inválido. O valor máximo é de R$ 1.000.000,00"
                    preco = None

            except ValueError:
                erro_preco = "O valor digitado é inválido. O preço deve ser um número. Tente novamente!"
                preco = None

        if not erro_nome and not erro_preco:

            carro["nome"] = nome
            carro["ano"] = ano
            carro["preco"] = preco
            carro["cor"] = cor
            carro["cambio"] = cambio
            carro["marca"] = marca
            carro["combustivel"] = combustivel

            salvar_json(CARROS_FILE, carros)

            return redirect(url_for("carros_page"))

    return render_template(
        "editar.html",
        carro=carro,
        anos=anos,
        cores=cores,
        cambios=cambios,
        marcas=marcas,
        combustiveis=combustiveis,
        erro_nome=erro_nome,
        erro_preco=erro_preco
    )

@app.route("/gerenciar")
def gerenciar():

    return render_template(
        "gerenciar.html",
        cores=cores,
        cambios=cambios,
        marcas=marcas,
        combustiveis=combustiveis
    )
    
@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)