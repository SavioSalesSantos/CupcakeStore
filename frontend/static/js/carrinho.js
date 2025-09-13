function removerItem(idProduto) {
    if (confirm('Tem certeza que deseja remover este item do carrinho?')) {
        alert(`Produto ${idProduto} removido do carrinho!`);
        // Aqui vamos recarregar a página (mais tarde implementamos remoção real)
        window.location.reload();
    }
}

function finalizarCompra() {
    alert('🎉 Compra finalizada com sucesso! Obrigado pela preferência!');
    // Redireciona para a página inicial
    window.location.href = "/";
}