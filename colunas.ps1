# colunas.ps1
$pythonCode = @'
from flask import Flask, render_template, jsonify
import requests
from collections import defaultdict

app = Flask(__name__)

def get_all_results():
    url = "https://loteriascaixa-api.herokuapp.com/api/megasena/latest"
    response = requests.get(url)
    return response.json()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/dados/<tipo>")
def get_dados(tipo):
    resultado = get_all_results()
    numeros = resultado[tipo]
    
    frequencias = {
        "col1": defaultdict(int),
        "col2": defaultdict(int),
        "col3": defaultdict(int),
        "col4": defaultdict(int),
        "col5": defaultdict(int),
        "col6": defaultdict(int)
    }
    
    for i, num in enumerate(numeros):
        coluna = f"col{i+1}"
        frequencias[coluna][int(num)] += 1
    
    top10 = {}
    for coluna, contagem in frequencias.items():
        top10[coluna] = sorted(
            [{"numero": num, "frequencia": freq} 
             for num, freq in contagem.items()],
            key=lambda x: x["frequencia"],
            reverse=True
        )[:10]
    
    return jsonify(top10)

if __name__ == "__main__":
    app.run(debug=True)
'@

$htmlCode = @'
<!DOCTYPE html>
<html>
<head>
    <title>Análise Mega Sena - Frequência por Posição</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <h1>Análise de Frequência por Posição - Mega Sena</h1>
        <button id="toggleTipo">Alternar Ordem (Sorteio/Crescente)</button>
        
        <div class="colunas">
            <div class="col-container">
                <h3>1ª Posição</h3>
                <div id="col1" class="numeros"></div>
            </div>
            <div class="col-container">
                <h3>2ª Posição</h3>
                <div id="col2" class="numeros"></div>
            </div>
            <div class="col-container">
                <h3>3ª Posição</h3>
                <div id="col3" class="numeros"></div>
            </div>
            <div class="col-container">
                <h3>4ª Posição</h3>
                <div id="col4" class="numeros"></div>
            </div>
            <div class="col-container">
                <h3>5ª Posição</h3>
                <div id="col5" class="numeros"></div>
            </div>
            <div class="col-container">
                <h3>6ª Posição</h3>
                <div id="col6" class="numeros"></div>
            </div>
        </div>
    </div>
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</body>
</html>
'@

$cssCode = @'
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.colunas {
    display: flex;
    justify-content: space-between;
    margin: 20px 0;
    flex-wrap: wrap;
}

.col-container {
    flex: 1;
    min-width: 150px;
    margin: 10px;
    padding: 15px;
    border: 1px solid #ccc;
    border-radius: 5px;
    background-color: #f5f5f5;
}

.numeros {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.numero-item {
    display: flex;
    justify-content: space-between;
    padding: 5px;
    background-color: #fff;
    border-radius: 3px;
    transition: all 0.3s;
}

.numero-item:hover {
    background-color: #209869;
    color: white;
    transform: scale(1.02);
}

button {
    padding: 10px 20px;
    font-size: 16px;
    background-color: #209869;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s;
}

button:hover {
    background-color: #1a7f57;
}

h1 {
    color: #209869;
    text-align: center;
}

h3 {
    color: #209869;
    text-align: center;
    margin-bottom: 15px;
}
'@

$jsCode = @'
let tipoAtual = "dezenasOrdemSorteio";

function atualizarDados() {
    fetch(`/api/dados/${tipoAtual}`)
        .then(response => response.json())
        .then(data => {
            Object.entries(data).forEach(([coluna, numeros]) => {
                const elemento = document.getElementById(coluna);
                if (elemento) {
                    elemento.innerHTML = numeros
                        .map(item => `
                            <div class="numero-item">
                                <span>Número ${item.numero}</span>
                                <span>${item.frequencia}x</span>
                            </div>
                        `)
                        .join("");
                }
            });
        });
}

document.getElementById("toggleTipo").addEventListener("click", () => {
    tipoAtual = tipoAtual === "dezenasOrdemSorteio" ? "dezenas" : "dezenasOrdemSorteio";
    atualizarDados();
});

// Carregar dados iniciais
atualizarDados();
'@

$requirementsContent = @'
Flask==2.0.1
requests==2.26.0
python-dotenv==0.19.0
'@

# Criando diretórios
Write-Host "Criando diretórios..." -ForegroundColor Green
New-Item -ItemType Directory -Force -Path ".\static" | Out-Null
New-Item -ItemType Directory -Force -Path ".\templates" | Out-Null
New-Item -ItemType Directory -Force -Path ".\static\css" | Out-Null
New-Item -ItemType Directory -Force -Path ".\static\js" | Out-Null

# Criando arquivo Python
Write-Host "Criando arquivo Python..." -ForegroundColor Green
Set-Content -Path "app.py" -Value $pythonCode

# Criando arquivo HTML
Write-Host "Criando arquivo HTML..." -ForegroundColor Green
New-Item -ItemType Directory -Force -Path ".\templates" | Out-Null
Set-Content -Path ".\templates\index.html" -Value $htmlCode

# Criando arquivo CSS
Write-Host "Criando arquivo CSS..." -ForegroundColor Green
Set-Content -Path ".\static\css\style.css" -Value $cssCode

# Criando arquivo JavaScript
Write-Host "Criando arquivo JavaScript..." -ForegroundColor Green
Set-Content -Path ".\static\js\script.js" -Value $jsCode

# Criando requirements.txt
Write-Host "Criando requirements.txt..." -ForegroundColor Green
Set-Content -Path "requirements.txt" -Value $requirementsContent

# Criando ambiente virtual
Write-Host "Criando ambiente virtual..." -ForegroundColor Green
python -m venv venv
.\venv\Scripts\Activate

# Instalando dependências
Write-Host "Instalando dependências..." -ForegroundColor Green
pip install -r requirements.txt

Write-Host "`nConfiguração concluída!" -ForegroundColor Green
Write-Host "Para executar a aplicação:" -ForegroundColor Yellow
Write-Host "1. Certifique-se que o ambiente virtual está ativado (deve ver (venv) no início do prompt)" -ForegroundColor Yellow
Write-Host "2. Execute: python app.py" -ForegroundColor Yellow
Write-Host "3. Acesse: http://localhost:5000 no navegador" -ForegroundColor Yellow