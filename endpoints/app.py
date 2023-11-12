from flask import Flask
from venda import venda_bp
from conta_estoque import conta_estoque_bp
from assinatura import assinatura_bp
from item_conta_estoque import item_conta_estoque_bp
from item_categoria import item_categoria_bp
from funcao import funcao_bp
from cliente import cliente_bp
from cliente_endereco import cliente_endereco_bp
from item import item_bp
from logger import logger  # Importe o logger do logger.py

app = Flask(__name__)
app.register_blueprint(venda_bp, url_prefix='')
app.register_blueprint(assinatura_bp, url_prefix='')
app.register_blueprint(item_bp, url_prefix='')
app.register_blueprint(conta_estoque_bp, conta_estoque='')
app.register_blueprint(item_conta_estoque_bp, item_conta_estoque='')
app.register_blueprint(item_categoria_bp, item_categoria='')
app.register_blueprint(funcao_bp, funcao='')
app.register_blueprint(cliente_bp, cliente='')
app.register_blueprint(cliente_endereco_bp, cliente_endereco='')

if __name__ == '__main__':
    app.run(port=5550, host='endpoints', debug=True)
