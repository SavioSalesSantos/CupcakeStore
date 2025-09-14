function removerItem(idProduto) {
    if (confirm('Tem certeza que deseja remover este item do carrinho?')) {
        alert(`Produto ${idProduto} removido do carrinho!`);
        // Aqui vamos recarregar a página (mais tarde implementamos remoção real)
        window.location.reload();
    }
}

function finalizarCompra() {
    // Redireciona para a página de confirmação de compra
    window.location.href = "/finalizar-compra";
}