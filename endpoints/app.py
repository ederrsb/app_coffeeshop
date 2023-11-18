from flask import Flask
from venda import venda_bp
from venda_pagamento import venda_pagamento_bp
from venda_entrega import venda_entrega_bp
from conta_estoque import conta_estoque_bp
from assinatura import assinatura_bp
from item_conta_estoque import item_conta_estoque_bp
from item_categoria import item_categoria_bp
from funcao import funcao_bp
from cliente import cliente_bp
from cliente_endereco import cliente_endereco_bp
from item import item_bp
from funcionario import funcionario_bp
from usuario import usuario_bp
from funcao_acesso import funcao_acesso_bp
from carrinho import carrinho_bp
from login import login_bp

app = Flask(__name__)
app.register_blueprint(venda_bp, url_prefix='')
app.register_blueprint(venda_pagamento_bp, venda_pagamento='')
app.register_blueprint(venda_entrega_bp, venda_entrega='')
app.register_blueprint(assinatura_bp, url_prefix='')
app.register_blueprint(item_bp, url_prefix='')
app.register_blueprint(conta_estoque_bp, conta_estoque='')
app.register_blueprint(item_conta_estoque_bp, item_conta_estoque='')
app.register_blueprint(item_categoria_bp, item_categoria='')
app.register_blueprint(funcao_bp, funcao='')
app.register_blueprint(cliente_bp, cliente='')
app.register_blueprint(cliente_endereco_bp, cliente_endereco='')
app.register_blueprint(funcionario_bp, funcionario='')
app.register_blueprint(usuario_bp, usuario='')
app.register_blueprint(funcao_acesso_bp, funcao_acesso='')
app.register_blueprint(carrinho_bp, carrinho='')
app.register_blueprint(login_bp, login='')

if __name__ == '__main__':
    app.run(port=5550, host='endpoints', debug=True)
