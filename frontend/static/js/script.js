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
    const botao = element;
    const rect = botao.getBoundingClientRect();

    // Animação no botão
    botao.classList.add('carregando');
    botao.textContent = 'Adicionando...';

    // Criar contador flutuante
    criarContadorFlutuante(rect);

    // Tocar som
    const audio = new Audio('{{ url_for("static", filename="sounds/caixa.mp3") }}');
    audio.play().catch(e => console.log("Audio play failed:", e));

    fetch(`/adicionar/${idProduto}`)
        .then(response => {
            if (response.ok) {
                // Animações de sucesso
                botao.classList.remove('carregando');
                botao.classList.add('adicionado');
                botao.textContent = 'Adicionado!';
                botao.style.backgroundColor = '#27ae60'; // Verde

                atualizarContadorCarrinho();
                mostrarNotificacao(
                    `${nomeProduto} adicionado ao carrinho! 🧁`,
                    'sucesso',
                    'Produto Adicionado!'
                );

                // Volta ao normal após 2 segundos
                setTimeout(() => {
                    botao.classList.remove('adicionado');
                    botao.textContent = '🛒 Comprar';
                    botao.style.backgroundColor = ''; // Volta à cor original
                }, 2000);
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            botao.classList.remove('carregando');
            botao.textContent = '🛒 Tentar Novamente';
            setTimeout(() => {
                botao.textContent = '🛒 Comprar';
            }, 2000);

            mostrarNotificacao(
                'Erro ao adicionar ao carrinho. Tente novamente.',
                'erro',
                'Oops!'
            );
        });
}

// Função para criar contador flutuante
function criarContadorFlutuante(rect) {
    const contador = document.createElement('div');
    contador.className = 'contador-flutuante';
    contador.textContent = '+1';
    contador.style.position = 'fixed';
    contador.style.top = `${rect.top + window.scrollY}px`;
    contador.style.left = `${rect.left + (rect.width / 2) - 15}px`;
    contador.style.zIndex = '9999';

    document.body.appendChild(contador);

    // Remove após animação
    setTimeout(() => {
        contador.remove();
    }, 1000);
}

// Atualize também o carregamento inicial
document.addEventListener('DOMContentLoaded', function () {
    atualizarContadorCarrinho();
});

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
document.addEventListener('DOMContentLoaded', function () {
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

// 🔍 FILTRAR CUPCAKES EM TEMPO REAL (igual ao admin)
function filtrarCupcakes() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const url = new URL(window.location.href);

    if (searchTerm.trim()) {
        url.searchParams.set('q', searchTerm);
    } else {
        url.searchParams.delete('q');
    }

    window.location.href = url.toString();
}

// 🔍 BUSCA EM TEMPO REAL (digitação)
document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchInput');

    if (searchInput) {
        let searchTimeout;

        searchInput.addEventListener('input', function () {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                filtrarCupcakes();
            }, 500); // Busca após 500ms de inatividade
        });
    }
});