let tipoAtual = "dezenasOrdemSorteio";
let isLoading = false;

function formatNumber(num) {
    return num.toString().padStart(2, '0');
}

function atualizarTipoOrdemTexto() {
    const textoOrdem = tipoAtual === "dezenasOrdemSorteio" ? "Ordem do Sorteio" : "Ordem Crescente";
    document.getElementById("tipoOrdemAtual").textContent = textoOrdem;
}

function atualizarBotao(isLoading) {
    const botao = document.getElementById("toggleTipo");
    botao.disabled = isLoading;
    botao.textContent = isLoading ? "Alterando Ordem..." : "Alternar Ordem";
}

async function atualizarDados() {
    if (isLoading) return;
    
    isLoading = true;
    atualizarBotao(true);
    
    document.querySelectorAll('.numeros').forEach(el => {
        el.innerHTML = '<div class="loading">Carregando...</div>';
    });

    try {
        const response = await fetch(`/api/dados/${tipoAtual}`);
        if (!response.ok) throw new Error('Erro na resposta da API');
        const data = await response.json();
        
        // Atualizar o total de concursos
        if (data.totalConcursos) {
            document.getElementById("totalConcursos").value = data.totalConcursos;
        }
        
        // Atualizar dados das colunas
        Object.entries(data.frequencias).forEach(([coluna, numeros]) => {
            const elemento = document.getElementById(coluna);
            if (elemento) {
                elemento.innerHTML = numeros
                    .map(item => `
                        <div class="numero-item">
                            <span>Número ${formatNumber(item.numero)}</span>
                            <span>${item.frequencia}x</span>
                        </div>
                    `)
                    .join("");
            }
        });
    } catch (error) {
        console.error('Erro ao carregar dados:', error);
    } finally {
        isLoading = false;
        atualizarBotao(false);
    }
}

// Carregar dados quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    atualizarTipoOrdemTexto();
    atualizarDados();
});

// Adicionar evento de clique no botão
document.getElementById("toggleTipo").addEventListener("click", () => {
    tipoAtual = tipoAtual === "dezenasOrdemSorteio" ? "dezenas" : "dezenasOrdemSorteio";
    atualizarTipoOrdemTexto();
    atualizarDados();
});