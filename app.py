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
        


# def gerar_jogos_mais_frequentes(top_frequencias):
#     """
#     Gera exatamente 10 jogos baseados nos números mais frequentes de cada coluna.
#     O primeiro jogo usa os números mais frequentes de cada posição.
#     """
#     jogos_ordem_sorteio = []
#     jogos_ordem_crescente = []
    
#     # Pega os números mais frequentes de cada coluna
#     numeros_por_coluna = {
#         f'col{i+1}': [item["numero"] for item in dados[:10]]  # Pega os 10 mais frequentes
#         for i, (col, dados) in enumerate(top_frequencias.items())
#     }
    
#     # Gera exatamente 10 jogos
#     for i in range(10):
#         # Para cada posição, pega o número na posição i da lista de frequências
#         jogo = []
#         for pos in range(6):
#             coluna = f'col{pos+1}'
#             numeros_disponiveis = numeros_por_coluna[coluna]
#             # Se acabarem os números frequentes, volta ao início da lista
#             numero_index = i % len(numeros_disponiveis)
#             numero = numeros_disponiveis[numero_index]
            
#             # Garante que não há números repetidos no jogo
#             while numero in jogo:
#                 numero_index = (numero_index + 1) % len(numeros_disponiveis)
#                 numero = numeros_disponiveis[numero_index]
            
#             jogo.append(numero)
        
#         jogo_crescente = sorted(jogo)
        
#         # Adiciona apenas se o jogo ainda não existe
#         if jogo_crescente not in jogos_ordem_crescente:
#             jogos_ordem_sorteio.append(jogo)
#             jogos_ordem_crescente.append(jogo_crescente)
    
#     # Se por algum motivo tivermos menos de 10 jogos (devido a duplicatas),
#     # geramos jogos adicionais até termos exatamente 10
#     while len(jogos_ordem_sorteio) < 10:
#         novo_jogo = []
#         for pos in range(6):
#             coluna = f'col{pos+1}'
#             numeros_disponiveis = numeros_por_coluna[coluna]
#             numero = numeros_disponiveis[len(jogos_ordem_sorteio) % len(numeros_disponiveis)]
            
#             # Evita números repetidos
#             while numero in novo_jogo:
#                 numero = numeros_disponiveis[(numeros_disponiveis.index(numero) + 1) % len(numeros_disponiveis)]
            
#             novo_jogo.append(numero)
        
#         novo_jogo_crescente = sorted(novo_jogo)
        
#         if novo_jogo_crescente not in jogos_ordem_crescente:
#             jogos_ordem_sorteio.append(novo_jogo)
#             jogos_ordem_crescente.append(novo_jogo_crescente)
    
#     return {
#         'ordemSorteio': jogos_ordem_sorteio[:10],  # Garante exatamente 10 jogos
#         'ordemCrescente': jogos_ordem_crescente[:10]
#     }

def gerar_jogos_mais_frequentes(top_frequencias):
    """
    Gera exatamente 10 jogos baseados nos números mais frequentes de cada coluna.
    O primeiro jogo usa os números mais frequentes de cada posição.
    """
    jogos_ordem_sorteio = []
    jogos_ordem_crescente = []
    
    try:
        # Verifica se temos todas as colunas necessárias
        colunas_necessarias = [f'col{i}' for i in range(1, 7)]
        for col in colunas_necessarias:
            if col not in top_frequencias:
                raise ValueError(f"Coluna {col} não encontrada nos dados")
        
        # Pega os números mais frequentes de cada coluna (garantindo que temos pelo menos 10)
        numeros_por_coluna = {}
        for col in colunas_necessarias:
            numeros = [item["numero"] for item in top_frequencias[col]]
            # Se não tivermos 10 números, repetimos os existentes
            while len(numeros) < 10:
                numeros.extend(numeros[:10-len(numeros)])
            numeros_por_coluna[col] = numeros[:10]  # Garantimos exatamente 10 números
        
        # Gera os 10 jogos
        for i in range(10):
            tentativas = 0
            while tentativas < 100:  # Limite de tentativas para evitar loop infinito
                # Para cada posição, pega o número na posição i da lista de frequências
                jogo = []
                for pos in range(6):
                    coluna = f'col{pos+1}'
                    numeros_disponiveis = numeros_por_coluna[coluna].copy()
                    # Tenta encontrar um número não usado no jogo atual
                    for j in range(len(numeros_disponiveis)):
                        numero_index = (i + j) % len(numeros_disponiveis)
                        numero = numeros_disponiveis[numero_index]
                        if numero not in jogo:
                            jogo.append(numero)
                            break
                
                # Verifica se temos 6 números únicos
                if len(jogo) == 6 and len(set(jogo)) == 6:
                    jogo_crescente = sorted(jogo)
                    if jogo_crescente not in jogos_ordem_crescente:
                        jogos_ordem_sorteio.append(jogo)
                        jogos_ordem_crescente.append(jogo_crescente)
                        break
                
                tentativas += 1
            
            # Se não conseguiu gerar um jogo válido após todas as tentativas
            if len(jogos_ordem_sorteio) < i + 1:
                # Gera um jogo garantido usando números diferentes
                numeros_disponiveis = list(range(1, 61))
                jogo = []
                for _ in range(6):
                    numero = numeros_disponiveis.pop(0)
                    jogo.append(numero)
                jogo_crescente = sorted(jogo)
                jogos_ordem_sorteio.append(jogo)
                jogos_ordem_crescente.append(jogo_crescente)
        
        return {
            'ordemSorteio': jogos_ordem_sorteio[:10],
            'ordemCrescente': jogos_ordem_crescente[:10]
        }
        
    except Exception as e:
        print(f"Erro ao gerar jogos: {str(e)}")
        # Retorna 10 jogos padrão em caso de erro
        jogos_padrao = []
        jogos_padrao_crescente = []
        for i in range(10):
            jogo = [(i * 6 + j) % 60 + 1 for j in range(6)]
            jogos_padrao.append(jogo)
            jogos_padrao_crescente.append(sorted(jogo))
        
        return {
            'ordemSorteio': jogos_padrao,
            'ordemCrescente': jogos_padrao_crescente
        }

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)