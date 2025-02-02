from flask import Flask, render_template, jsonify
import requests
from collections import defaultdict
import os

app = Flask(__name__)

def get_all_results(tipo):
    url = "https://loteriascaixa-api.herokuapp.com/api/megasena"
    response = requests.get(url)
    resultados = response.json()
    numeros_por_posicao = defaultdict(lambda: defaultdict(int))
    
    for resultado in resultados:
        if tipo in resultado:
            numeros = resultado[tipo]
            for posicao, numero in enumerate(numeros, 1):
                numeros_por_posicao[f'col{posicao}'][int(numero)] += 1
                
    return numeros_por_posicao, len(resultados)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/dados/<tipo>')
def get_dados(tipo):
    try:
        numeros_por_posicao, total_concursos = get_all_results(tipo)
        
        frequencias = {}
        for coluna, frequencias_coluna in numeros_por_posicao.items():
            numeros_ordenados = [
                {"numero": num, "frequencia": freq}
                for num, freq in frequencias_coluna.items()
            ]
            numeros_ordenados.sort(key=lambda x: (-x["frequencia"], x["numero"]))
            frequencias[coluna] = numeros_ordenados[:10]
        
        return jsonify({
            "frequencias": frequencias,
            "totalConcursos": total_concursos
        })
        
    except Exception as e:
        print(f"Erro na rota /api/dados: {e}")
        return jsonify({"error": str(e)}), 500

"""
if __name__ == '__main__':
    app.run(debug=True)

"""
    # Configuração da porta
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Obtém a porta do ambiente ou usa 5000 como padrão
    app.run(host="0.0.0.0", port=port)  # Inicia o servidor Flask na porta correta



