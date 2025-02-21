from flask import Flask, render_template, jsonify
import requests
from collections import defaultdict
import os

app = Flask(__name__)

def get_all_results():
    """Busca todos os resultados da Mega Sena"""
    try:
        url = "https://loteriascaixa-api.herokuapp.com/api/megasena"
        response = requests.get(url, timeout=10)  # Adicionado timeout
        response.raise_for_status()
        dados = response.json()
        
        # Validação da resposta
        if not isinstance(dados, list) or not dados:
            print("Resposta da API em formato inválido")
            return None
            
        # Ordena os resultados pelo número do concurso
        dados_ordenados = sorted(dados, key=lambda x: int(x['concurso']), reverse=True)
        print(f"Último concurso obtido: {dados_ordenados[0]['concurso']}")
        
        return dados_ordenados
    except requests.exceptions.Timeout:
        print("Timeout ao acessar a API")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar dados da API: {str(e)}")
        return None
    except ValueError as e:
        print(f"Erro ao decodificar JSON: {str(e)}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/dados/<tipo>')
def get_dados(tipo):
    try:
        resultados = get_all_results()
        if not resultados:
            print("Nenhum resultado obtido da API")  # Adicionado log conforme codigo2
            return jsonify({"error": "Não foi possível obter dados da API"}), 500

        total_concursos = len(resultados)
        
        # Pega o último resultado conforme codigo2
        ultimo_resultado = resultados[0] if resultados else None

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
            if 'dezenasOrdemSorteio' in resultado:
                # Converte números para inteiros
                nums_sorteio = [int(n) for n in resultado['dezenasOrdemSorteio']]
                nums_crescente = sorted(nums_sorteio)  # Ordena para ordem crescente
                
                # Guarda últimos jogos em ambas as ordens
                ultimos_jogos_sorteio.append(nums_sorteio)
                ultimos_jogos_crescente.append(nums_crescente)
                
                # Conta frequências baseado no tipo solicitado
                numeros = nums_sorteio if tipo == 'dezenasOrdemSorteio' else nums_crescente
                for pos, num in enumerate(numeros):
                    frequencias[f'col{pos+1}'][num] += 1
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

        # Inverte a ordem dos últimos jogos para mostrar mais recentes primeiro
        ultimos_jogos_sorteio.reverse()
        ultimos_jogos_crescente.reverse()
        
        # Adiciona a matriz de frequência completa
        matriz_frequencia = criar_matriz_frequencia(resultados, tipo)
       
       # Gera jogos sugeridos baseados nas frequências
        jogos_sugeridos = gerar_jogos_mais_frequentes(top_frequencias)

        
        return jsonify({
            "frequencias": top_frequencias,
            "totalConcursos": total_concursos,
            "ultimosJogos": {
                "ordemSorteio": ultimos_jogos_sorteio[:10],
                "ordemCrescente": ultimos_jogos_crescente[:10]
            },
            "top10Geral": top10_geral,
            "ultimoResultado": ultimo_resultado,  # Adicionado último resultado conforme codigo2
            "matrizFrequencia": matriz_frequencia,  # Adicione esta linha
            "jogosSugeridos": jogos_sugeridos  # Adiciona os jogos sugeridos
        })

    except Exception as e:
        print(f"Erro ao processar dados: {str(e)}")
        return jsonify({"error": f"Erro ao processar dados: {str(e)}"}), 500
        
def criar_matriz_frequencia(resultados, tipo):
    """
        Cria uma matriz de frequência que respeita a ordem crescente dos números
    """
    # Inicializa matriz 60x6 com zeros
    matriz = [[0 for _ in range(6)] for _ in range(60)]
    
    for resultado in resultados:
        if 'dezenasOrdemSorteio' in resultado:
            # Importante: Sempre usar ordem crescente aqui
            numeros = sorted([int(n) for n in resultado['dezenasOrdemSorteio']])
            
            # Agora sim conta a frequência na posição correta
            for pos, num in enumerate(numeros):
                matriz[num-1][pos] += 1
    
    # Formata a matriz para retorno
    matriz_formatada = []
    for num in range(60):
        linha = {
            'numero': num + 1,
            'frequencias': matriz[num],
            'total': sum(matriz[num])
        }
        matriz_formatada.append(linha)
    
    return matriz_formatada
        
def gerar_jogos_mais_frequentes(top_frequencias):
    """Gera jogos baseados nos números mais frequentes de cada coluna"""
    jogos_ordem_sorteio = []
    jogos_ordem_crescente = []
    
    # Pega os números mais frequentes de cada coluna
    numeros_frequentes = {
        f'col{i+1}': [item["numero"] for item in dados[:3]]  # Pega os 3 mais frequentes
        for i, (col, dados) in enumerate(top_frequencias.items())
    }
    
    # Gera jogos com os números mais frequentes
    for i in range(min(10, len(numeros_frequentes['col1']))):
        jogo = [
            numeros_frequentes[f'col{pos+1}'][min(i, len(numeros_frequentes[f'col{pos+1}'])-1)]
            for pos in range(6)
        ]
        jogo_crescente = sorted(jogo)
        
        # Adiciona apenas se ainda não existe
        if jogo_crescente not in jogos_ordem_crescente:
            jogos_ordem_sorteio.append(jogo)
            jogos_ordem_crescente.append(jogo_crescente)
    
    return {
        'ordemSorteio': jogos_ordem_sorteio,
        'ordemCrescente': jogos_ordem_crescente
    }



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)