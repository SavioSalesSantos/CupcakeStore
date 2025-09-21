🧁 Cupcake Store
Um protótipo de e-commerce para uma loja de cupcakes, desenvolvido como trabalho acadêmico para a disciplina de Projeto Integrador Transdisciplinar II do curso de Engenharia de Software da UNICID - Cruzeiro Sul Virtual

⚠️ Atenção: Este é um projeto acadêmico que funciona como uma loja online de cupcakes para uma pequena empresa. Ele utiliza conceitos aprendidos durante o curso, mas não atende aos requisitos para ser utilizado em produção.

✨ Funcionalidades Principais
Catálogo de Produtos: Visualização de cupcakes com imagens, descrições e preços

Sistema de Carrinho: Adição, remoção e gestão de itens no carrinho de compras

Autenticação de Usuários: Registro, login e gestão de perfis

Painel Administrativo: CRUD completo de produtos, usuários e pedidos

Sistema de Pedidos: Histórico de compras e status de pedidos

Design Responsivo: Interface adaptada para mobile, tablet e desktop

🛠️ Tecnologias Utilizadas
Back-end
Python 3.8+: Linguagem de programação principal

Flask: Framework web lightweight

SQLite: Banco de dados relacional

SQLAlchemy: ORM para gestão do banco de dados

Werkzeug: Utilidades para segurança (hash de senhas)

Front-end
HTML5: Estrutura das páginas

CSS3: Estilização com design responsivo

JavaScript: Interatividade e funcionalidades dinâmicas

Font Awesome: Ícones

Google Fonts (Poppins): Tipografia

📁 Estrutura do Projeto
text
cupcakestore/
├── backend/
│   ├── app.py                 # Aplicação principal Flask
│   ├── controller.py          # Controladores adicionais
│   └── __init__.py
├── database/
│   ├── database.py            # Configuração e modelos do banco
│   ├── cupcakes.db            # Banco de dados SQLite (gerado)
│   └── __init__.py
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css      # Estilos principais
│   │   ├── js/
│   │   │   ├── script.js      # JavaScript geral
│   │   │   └── carrinho.js    # Funcionalidades do carrinho
│   │   ├── sounds/            # Efeitos sonoros
│   │   └── uploads/           # Imagens enviadas
│   └── templates/
│       ├── admin/             # Painel administrativo
│       │   ├── dashboard.html
│       │   ├── produtos.html
│       │   ├── pedidos.html
│       │   ├── usuarios.html
│       │   ├── editar_produto.html
│       │   └── editar_usuario.html
│       ├── index.html         # Página inicial
│       ├── login.html         # Autenticação
│       ├── register.html      # Registro
│       ├── carrinho.html      # Carrinho de compras
│       ├── compra_finalizada.html
│       ├── meu_usuario.html   # Perfil do usuário
│       └── meus_pedidos.html  # Histórico de pedidos
├── tests/                     # Testes
├── docs/                      # Documentação
├── requirements.txt           # Dependências Python
└── README.md                  # Este arquivo
📸 Capturas de Tela
Página Principal
https://via.placeholder.com/800x400/ff6b8b/ffffff?text=P%25C3%25A1gina+Principal+Cupcake+Store

Painel Administrativo
https://via.placeholder.com/800x400/9b59b6/ffffff?text=Painel+Administrativo

Carrinho de Compras
https://via.placeholder.com/800x400/27ae60/ffffff?text=Carrinho+de+Compras

🚀 Como Executar o Projeto Localmente
Pré-requisitos
Python 3.8+

pip (gerenciador de pacotes do Python)

SQLite (já incluído no Python)

Passo a Passo
Clone o repositório:

bash
git clone https://github.com/SavioSalesSantos/cupcakestore.git
cd cupcakestore
Crie um ambiente virtual (recomendado):

bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
Instale as dependências:

bash
pip install -r requirements.txt
Inicialize o banco de dados:

bash
python -c "
from database.database import init_db
init_db()
print('✅ Banco de dados inicializado com sucesso!')
"
Execute a aplicação:

bash
python backend/app.py
Acesse a aplicação:
Abra seu navegador e visite: http://localhost:5000

👤 Credenciais de Demonstração
Conta Administrativa
Email: admin@cupcakestore.com

Senha: admin123

Conta de Usuário Comum
Email: teste@email.com

Senha: teste123

👥 Autoria
Este projeto foi desenvolvido como parte do Projeto Integrador Transdisciplinar em Engenharia de Software II da UNICID - Cruzeiro Sul Virtual.

Desenvolvedor: Savio Sales Santos
Email: savio.s11@gmail.com
GitHub: https://github.com/SavioSalesSantos

📄 Licença
Este projeto é acadêmico e desenvolvido para fins educacionais. Não possui licença específica, mas sinta-se à vontade para referenciar o código como inspiração para seus próprios projetos.

🤝 Contribuições
Sinta-se à vontade para contribuir com o código!

Para contribuir:

Faça um fork do projeto

Crie uma branch para sua feature (git checkout -b feature/AmazingFeature)

Commit suas mudanças (git commit -m 'Add some AmazingFeature')

Push para a branch (git push origin feature/AmazingFeature)

Abra um Pull Request

🆘 Suporte
Para dúvidas ou problemas com a aplicação:

Consulte a documentação no diretório docs/

Verifique as issues abertas no GitHub

Entre em contato pelo email: savio.s11@gmail.com

Nota: Este projeto está em constante desenvolvimento e melhorias. Novas funcionalidades podem ser adicionadas periodicamente.
