from flask import Flask, render_template, jsonify
import requests
from collections import defaultdict
import os

app = Flask(__name__)

def get_all_results():
    """Busca todos os resultados da Mega Sena"""
    try:
        url = "https://loteriascaixa-api.herokuapp.com/api/megasena"
        response = requests.get(url)
        response.raise_for_status()  # Vai lançar exceção se não for 200
        return response.json()
    except Exception as e:
        print(f"Erro ao buscar dados da API: {str(e)}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/dados/<tipo>')
def get_dados(tipo):
    try:
        # Busca dados
        resultados = get_all_results()
        if not resultados:
            return jsonify({"error": "Não foi possível obter dados da API"}), 500

        # Contadores
        total_concursos = len(resultados)
        frequencias = {
            'col1': defaultdict(int),
            'col2': defaultdict(int),
            'col3': defaultdict(int),
            'col4': defaultdict(int),
            'col5': defaultdict(int),
            'col6': defaultdict(int)
        }
        ultimos_jogos_sorteio = []
        ultimos_jogos_crescente = []
        frequencia_geral = defaultdict(int)

        # Processa cada resultado
        for resultado in resultados:
            if tipo in resultado and resultado[tipo]:
                numeros = [int(n) for n in resultado[tipo]]
                numeros_ordenados = sorted(numeros)
                
                # Guarda últimos jogos
                ultimos_jogos_sorteio.append(numeros)
                ultimos_jogos_crescente.append(numeros_ordenados)
                
                # Conta frequências
                for pos, num in enumerate(numeros if tipo == 'dezenasOrdemSorteio' else numeros_ordenados):
                    coluna = f'col{pos+1}'
                    frequencias[coluna][num] += 1
                    frequencia_geral[num] += 1

        # Processa top 10 por coluna
        top_frequencias = {}
        for coluna, contagem in frequencias.items():
            ordenado = sorted(
                [{"numero": num, "frequencia": freq} 
                 for num, freq in contagem.items()],
                key=lambda x: (-x["frequencia"], x["numero"])
            )
            top_frequencias[coluna] = ordenado[:10]

        # Top 10 geral
        top10_geral = sorted(
            [{"numero": num, "frequencia": freq} 
             for num, freq in frequencia_geral.items()],
            key=lambda x: (-x["frequencia"], x["numero"])
        )[:10]

        return jsonify({
            "frequencias": top_frequencias,
            "totalConcursos": total_concursos,
            "ultimosJogos": {
                "ordemSorteio": ultimos_jogos_sorteio[-10:],  # últimos 10 jogos
                "ordemCrescente": ultimos_jogos_crescente[-10:]
            },
            "top10Geral": top10_geral
        })

    except Exception as e:
        print(f"Erro ao processar dados: {str(e)}")
        return jsonify({"error": f"Erro ao processar dados: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)