// Variáveis globais
let tipoAtual = "dezenasOrdemSorteio";
let isLoading = false;

// Funções utilitárias
function formatNumber(num) {
    return num.toString().padStart(2, '0');
}

function atualizarTipoOrdemTexto() {
    const textoOrdem = tipoAtual === "dezenasOrdemSorteio" ? "Ordem do Sorteio" : "Ordem Crescente";
    document.getElementById("tipoOrdemAtual").textContent = textoOrdem;
}

function atualizarBotao(isLoading) {
    const botao = document.getElementById("toggleTipo");
    if (botao) {
        botao.disabled = isLoading;
        botao.textContent = isLoading ? "Alterando Ordem..." : "Alternar Ordem";
    }
}

// Funções de criação de elementos
function criarTop10Geral(dados) {
    const container = document.getElementById('top10Geral');
    if (!container || !dados) return;

    const html = dados.map((item, index) => `
        <div class="numero-item ${index < 3 ? 'numero-destaque' : ''}">
            <span>${index + 1}º - Número ${formatNumber(item.numero)}</span>
            <span>${item.frequencia}x</span>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

function criarTabelaJogos(jogos, elementId) {
    const container = document.getElementById(elementId);
    if (!container || !jogos) return;

    const table = document.createElement('table');
    table.className = 'tabela';

    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    ['Concurso', '1ª', '2ª', '3ª', '4ª', '5ª', '6ª'].forEach(texto => {
        const th = document.createElement('th');
        th.textContent = texto;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement('tbody');
    jogos.forEach((jogo, index) => {
        const row = document.createElement('tr');
        
        const tdConcurso = document.createElement('td');
        tdConcurso.textContent = jogos.length - index;
        row.appendChild(tdConcurso);

        jogo.forEach(numero => {
            const td = document.createElement('td');
            td.textContent = formatNumber(numero);
            row.appendChild(td);
        });
        tbody.appendChild(row);
    });

    table.appendChild(tbody);
    container.innerHTML = '';
    container.appendChild(table);
}

// Função principal de atualização
async function atualizarDados() {
    if (isLoading) return;
    
    isLoading = true;
    atualizarBotao(true);
    
    const elementosParaAtualizar = document.querySelectorAll('.numeros, .tabela, #top10Geral');
    elementosParaAtualizar.forEach(el => {
        el.innerHTML = '<div class="loading">Carregando dados...</div>';
    });

    try {
        const response = await fetch(`/api/dados/${tipoAtual}`);
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }

        // Atualiza total de concursos
        const totalConcursosElement = document.getElementById("totalConcursos");
        if (totalConcursosElement) {
            totalConcursosElement.value = data.totalConcursos || 0;
        }
        
        // Atualiza frequências por coluna
        if (data.frequencias) {
            Object.entries(data.frequencias).forEach(([coluna, numeros]) => {
                const elemento = document.getElementById(coluna);
                if (elemento && Array.isArray(numeros)) {
                    elemento.innerHTML = numeros
                        .map((item, index) => `
                            <div class="numero-item ${index < 3 ? 'numero-destaque' : ''}">
                                <span>Número ${formatNumber(item.numero)}</span>
                                <span>${item.frequencia}x</span>
                            </div>
                        `)
                        .join("");
                }
            });
        }

        // Atualiza últimos jogos e top 10
        if (data.ultimosJogos?.ordemSorteio) {
            criarTabelaJogos(data.ultimosJogos.ordemSorteio, 'ultimosJogosSorteio');
        }
        if (data.ultimosJogos?.ordemCrescente) {
            criarTabelaJogos(data.ultimosJogos.ordemCrescente, 'ultimosJogosCrescente');
        }
        if (data.top10Geral) {
            criarTop10Geral(data.top10Geral);
        }

    } catch (error) {
        console.error('Erro ao carregar dados:', error);
        elementosParaAtualizar.forEach(el => {
            el.innerHTML = `<div class="error">Erro ao carregar dados: ${error.message}</div>`;
        });
    } finally {
        isLoading = false;
        atualizarBotao(false);
    }
}

// Inicialização e eventos
document.addEventListener('DOMContentLoaded', () => {
    atualizarTipoOrdemTexto();
    atualizarDados();

    // Adiciona evento ao botão
    const botao = document.getElementById("toggleTipo");
    if (botao) {
        botao.addEventListener("click", () => {
            tipoAtual = tipoAtual === "dezenasOrdemSorteio" ? "dezenas" : "dezenasOrdemSorteio";
            atualizarTipoOrdemTexto();
            atualizarDados();
        });
    }
});

// Atualização automática
setInterval(atualizarDados, 5 * 60 * 1000);