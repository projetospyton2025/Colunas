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
    
    const elementosParaAtualizar = document.querySelectorAll('.numeros, .tabela, #top10Geral, #ultimoSorteio, #matrizFrequencia');
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

		if (data.matrizFrequencia) {
			criarTabelaFrequencia(data.matrizFrequencia);
		}
		
		if (data.jogosSugeridos) {
            criarTabelaJogos(data.jogosSugeridos.ordemSorteio, 'jogosSugeridosSorteio');
            criarTabelaJogos(data.jogosSugeridos.ordemCrescente, 'jogosSugeridosCrescente');
        }
		
        // Atualiza último resultado
        if (data.ultimoResultado) {
            const ultimoSorteio = document.getElementById('ultimoSorteio');
            const dataAtualizacao = document.getElementById('dataAtualizacao');
            
            ultimoSorteio.innerHTML = `
                Concurso ${data.ultimoResultado.concurso}<br>
                Números: ${data.ultimoResultado.dezenasOrdemSorteio.join(' - ')}
            `;
            
            dataAtualizacao.textContent = `Última atualização: ${new Date().toLocaleString()}`;
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

// Atualizar a cada 5 minutos
setInterval(atualizarDados, 5 * 60 * 1000);

// Chamar imediatamente quando a página carregar
document.addEventListener('DOMContentLoaded', atualizarDados);



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


// function criarTabelaFrequencia(dados) {
//     const container = document.getElementById('matrizFrequencia');
//     if (!container || !dados) return;

//     const table = document.createElement('table');
//     table.className = 'tabela-matriz';

//     // Cabeçalho
//     const thead = document.createElement('thead');
//     const headerRow = document.createElement('tr');
//     ['Número', '1ª', '2ª', '3ª', '4ª', '5ª', '6ª', 'Total'].forEach(texto => {
//         const th = document.createElement('th');
//         th.textContent = texto;
//         headerRow.appendChild(th);
//     });
//     thead.appendChild(headerRow);
//     table.appendChild(thead);

//     // Corpo da tabela
//     const tbody = document.createElement('tbody');
//     dados.forEach(linha => {
//         const row = document.createElement('tr');
        
//         // Número
//         const tdNum = document.createElement('td');
//         tdNum.textContent = formatNumber(linha.numero);
//         row.appendChild(tdNum);
        
//         // Frequências por coluna
//         linha.frequencias.forEach(freq => {
//             const td = document.createElement('td');
//             td.textContent = freq;
//             td.className = freq > 0 ? 'tem-ocorrencia' : '';
//             row.appendChild(td);
//         });
        
//         // Total
//         const tdTotal = document.createElement('td');
//         tdTotal.textContent = linha.total;
//         tdTotal.className = 'total';
//         row.appendChild(tdTotal);
        
//         tbody.appendChild(row);
//     });

//     table.appendChild(tbody);
//     container.innerHTML = '';
//     container.appendChild(table);
// }

function criarTabelaFrequencia(dados) {
    const container = document.getElementById('matrizFrequencia');
    if (!container || !dados) return;

    // Encontra o maior valor de cada coluna
    const maioresPorColuna = [0, 0, 0, 0, 0, 0];
    dados.forEach(linha => {
        linha.frequencias.forEach((freq, colIndex) => {
            if (freq > maioresPorColuna[colIndex]) {
                maioresPorColuna[colIndex] = freq;
            }
        });
    });

    const table = document.createElement('table');
    table.className = 'tabela-matriz';

    // Cabeçalho
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    ['Número', '1ª Col', '2ª Col', '3ª Col', '4ª Col', '5ª Col', '6ª Col', 'Total'].forEach(texto => {
        const th = document.createElement('th');
        th.textContent = texto;
        th.style.padding = '8px 15px';
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Corpo da tabela
    const tbody = document.createElement('tbody');
    dados.forEach(linha => {
        const row = document.createElement('tr');
        
        // Número com formatação
        const tdNum = document.createElement('td');
        tdNum.textContent = formatNumber(linha.numero);
        tdNum.style.fontWeight = 'bold';
        row.appendChild(tdNum);
        
        // Frequências por coluna
        linha.frequencias.forEach((freq, colIndex) => {
            const td = document.createElement('td');
            td.textContent = freq;
            
            // Aplica classes de destaque
            if (freq > 0) {
                td.className = 'tem-ocorrencia';
            }
            // Destaca o maior valor da coluna
            if (freq === maioresPorColuna[colIndex] && freq > 0) {
                td.className = 'maior-valor-coluna';
            }
            row.appendChild(td);
        });
        
        // Total
        const tdTotal = document.createElement('td');
        tdTotal.textContent = linha.total;
        tdTotal.className = 'total';
        row.appendChild(tdTotal);
        
        tbody.appendChild(row);
    });

    table.appendChild(tbody);
    container.innerHTML = '';
    container.appendChild(table);
}




// Atualização automática
setInterval(atualizarDados, 5 * 60 * 1000);