let carrinho = [];

function comprar(idProduto) {
    // Adiciona o produto ao carrinho
    carrinho.push(idProduto);
    atualizarCarrinho();
    alert(`Produto ${idProduto} adicionado ao carrinho! 🧁`);
}

function atualizarCarrinho() {
    const contadorCarrinho = document.getElementById('contador-carrinho');
    if (contadorCarrinho) {
        contadorCarrinho.textContent = carrinho.length;
    }
}

function verCarrinho() {
    // Redireciona para a página do carrinho
    window.location.href = "/carrinho";
}

// Inicializa o carrinho quando a página carrega
document.addEventListener('DOMContentLoaded', function() {
    atualizarCarrinho();
});