# Define o caminho do repositório
$repoPath = "J:\Meu Drive\ProjetosPython\Loterias\Estrategias\MegaSena\Colunas"

# Mensagem de commit padrão
$commitMessage = "Commit forçado via PowerShell"

# Muda para o diretório do repositório
Set-Location -Path $repoPath

# Adiciona todas as mudanças ao staging
git add --all

# Faz o commit (forçando inclusão de todas as mudanças)
git commit -m "$commitMessage"

# Faz push forçado para o repositório remoto
git push origin main --force
