/// Função para mostrar notificação super elegante
function mostrarNotificacao(mensagem, tipo = 'sucesso', titulo = 'Sucesso!') {
    const notificacao = document.createElement('div');
    notificacao.className = `notificacao ${tipo}`;
    
    const icons = {
        sucesso: '🎉',
        erro: '❌',
        info: 'ℹ️'
    };
    
    notificacao.innerHTML = `
        <span class="notificacao-icon">${icons[tipo] || '🎉'}</span>
        <div class="notificacao-conteudo">
            <div class="notificacao-titulo">${titulo}</div>
            <div class="notificacao-mensagem">${mensagem}</div>
        </div>
        <button class="btn-fechar" onclick="this.parentElement.remove()">×</button>
    `;
    
    document.body.appendChild(notificacao);
    
    // Mostra a notificação com animação
    setTimeout(() => notificacao.classList.add('mostrar'), 100);
    
    // Remove automaticamente após 4 segundos
    setTimeout(() => {
        if (notificacao.parentElement) {
            notificacao.classList.remove('mostrar');
            setTimeout(() => notificacao.remove(), 400);
        }
    }, 4000);
}

function comprar(idProduto, nomeProduto, element) {
    // Animação de clique no botão
    const botao = element;
    botao.classList.add('carregando');
    botao.textContent = 'Adicionando...';
    
    fetch(`/adicionar/${idProduto}`)
        .then(response => {
            if (response.ok) {
                // Animação de sucesso
                botao.classList.remove('carregando');
                botao.classList.add('adicionado');
                botao.textContent = 'Adicionado!';
                
                atualizarContadorCarrinho();
                mostrarNotificacao(
                    `${nomeProduto} adicionado ao carrinho! 🧁`,
                    'sucesso',
                    'Produto Adicionado!'
                );
                
                // Volta ao normal após 2 segundos
                setTimeout(() => {
                    botao.classList.remove('adicionado');
                    botao.textContent = 'Comprar';
                }, 2000);
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            botao.classList.remove('carregando');
            botao.textContent = 'Tentar Novamente';
            setTimeout(() => {
                botao.textContent = 'Comprar';
            }, 2000);
            
            mostrarNotificacao(
                'Erro ao adicionar ao carrinho. Tente novamente.',
                'erro',
                'Oops!'
            );
        });
}

function atualizarContadorCarrinho() {
    fetch('/get-contador-carrinho')
        .then(response => response.json())
        .then(data => {
            const contadorCarrinho = document.getElementById('contador-carrinho');
            if (contadorCarrinho) {
                contadorCarrinho.textContent = data.quantidade;
            }
        });
}

function verCarrinho() {
    window.location.href = "/carrinho";
}

// Atualiza o contador quando a página carrega
document.addEventListener('DOMContentLoaded', function() {
    atualizarContadorCarrinho();
});

// Gerenciador de notificações - vertical compacto
function gerenciarNotificacoes() {
    const notificacoes = document.querySelectorAll('.notificacao');
    const bottomStart = 20;
    const spacing = 80; /* Espaço entre notificações */
    
    notificacoes.forEach((notificacao, index) => {
        notificacao.style.bottom = `${bottomStart + (index * spacing)}px`;
        notificacao.style.right = '20px';
    });
}

// Atualiza a posição das notificações a cada 100ms
setInterval(gerenciarNotificacoes, 100);