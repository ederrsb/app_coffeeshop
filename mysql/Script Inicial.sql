CREATE TABLE `acesso` (
  `id_acesso` varchar(60) NOT NULL,
  `descricao` varchar(100) NOT NULL,
  PRIMARY KEY (`id_acesso`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO db_coffeeshop.acesso (id_acesso,descricao) VALUES
	 ('assinatura','Dados das Assinaturas dos Cliente'),
	 ('assinatura_item','Dados das Assinaturas'),
	 ('carrinho','Carrinho de Compras'),
	 ('cliente','Dados dos Clientes'),
	 ('cliente_endereco','Dados de Endereço dos Clientes'),
	 ('conta_estoque','Dados das Conta de Estoque'),
	 ('finaliza_carrinho','Finalizar carrinho gerando a Venda para o Cliente'),
	 ('funcao','Funçao dos Funcionários'),
	 ('funcao_acesso','Acesso as Funcionalidades do Sistema por Função'),
	 ('funcionario','Dados dos Funcionários');
INSERT INTO db_coffeeshop.acesso (id_acesso,descricao) VALUES
	 ('item','Dados dos Itens'),
	 ('item_categoria','Dados das Categiorias dos Itens'),
	 ('item_conta_estoque','Dados das Contas de Estoque por Item'),
	 ('usuario','Dados dos Usuários'),
	 ('venda','Dados das Vendas'),
	 ('venda_entrega','Dados de Entrega das Vendas'),
	 ('venda_item','Dados dos Itens das Vendas'),
	 ('venda_pagamento','Dados dos Pagamento das Vendas');
	
CREATE TABLE `usuario` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `data_cadastro` date NOT NULL,
  `email` varchar(100) NOT NULL,
  `senha` varchar(100) NOT NULL,
  `status` char(1) NOT NULL COMMENT 'A - Ativo; I - Inativo',
  PRIMARY KEY (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;-- db_coffeeshop.funcao definition

CREATE TABLE `funcao` (
  `id_funcao` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `descricao` varchar(300) NOT NULL,
  PRIMARY KEY (`id_funcao`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `funcionario` (
  `id_funcionario` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `id_funcao` int NOT NULL,
  `data_admissao` date NOT NULL,
  `data_rescisao` date DEFAULT NULL,
  `id_usuario` int DEFAULT NULL,
  PRIMARY KEY (`id_funcionario`),
  KEY `funcionario_FK` (`id_funcao`),
  KEY `funcionario_FK_1` (`id_usuario`),
  CONSTRAINT `funcionario_FK` FOREIGN KEY (`id_funcao`) REFERENCES `funcao` (`id_funcao`),
  CONSTRAINT `funcionario_FK_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `cliente` (
  `id_cliente` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `cpf` varchar(14) NOT NULL,
  `rg` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `nascimento` date NOT NULL,
  `genero` char(1) NOT NULL,
  `celular` varchar(20) DEFAULT NULL,
  `id_usuario` int DEFAULT NULL,
  PRIMARY KEY (`id_cliente`),
  KEY `cliente_FK` (`id_usuario`),
  CONSTRAINT `cliente_FK` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `cliente_endereco` (
  `id_cliente` int NOT NULL,
  `seq` int NOT NULL,
  `rua` varchar(100) NOT NULL,
  `numero` varchar(10) NOT NULL,
  `bairro` varchar(60) NOT NULL,
  `cidade` varchar(100) NOT NULL,
  `cep` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `complemento` varchar(100) DEFAULT NULL,
  `tipo_endereco` varchar(20) NOT NULL,
  PRIMARY KEY (`id_cliente`,`seq`),
  CONSTRAINT `cliente_endereco_FK` FOREIGN KEY (`id_cliente`) REFERENCES `cliente` (`id_cliente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `item_categoria` (
  `id_item_categoria` int NOT NULL AUTO_INCREMENT,
  `descricao` varchar(100) NOT NULL,
  PRIMARY KEY (`id_item_categoria`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;-- db_coffeeshop.Item definition

CREATE TABLE `item` (
  `id_item` int NOT NULL AUTO_INCREMENT,
  `descricao` varchar(500) NOT NULL,
  `descricao_completa` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `unid_medida` varchar(10) NOT NULL,
  `id_item_categoria` int DEFAULT NULL,
  `valor_unitario` decimal(8,2) NOT NULL,
  `data_atualizacao` datetime DEFAULT NULL,
  `status` char(1) DEFAULT NULL COMMENT 'A - Ativo; I - Inativo',
  `imagem` longblob,
  PRIMARY KEY (`id_item`),
  KEY `Item_FK` (`id_item_categoria`),
  CONSTRAINT `Item_FK` FOREIGN KEY (`id_item_categoria`) REFERENCES `item_categoria` (`id_item_categoria`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `conta_estoque` (
  `id_conta_estoque` int NOT NULL AUTO_INCREMENT,
  `descricao` varchar(100) NOT NULL,
  PRIMARY KEY (`id_conta_estoque`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `item_conta_estoque` (
  `id_item` int NOT NULL,
  `id_conta_estoque` int NOT NULL,
  `saldo` decimal(8,2) NOT NULL,
  `qtde_minima` decimal(8,2) DEFAULT NULL,
  `qtde_maxima` decimal(8,2) DEFAULT NULL,
  `data_atualizacao` datetime NOT NULL,
  `conta_padrao` char(1) DEFAULT NULL COMMENT 'S - Sim; N - Não',
  PRIMARY KEY (`id_item`,`id_conta_estoque`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `assinatura` (
  `id_assinatura` int NOT NULL AUTO_INCREMENT,
  `descricao` varchar(500) NOT NULL,
  `periodicidade` varchar(20) NOT NULL,
  `status` char(1) NOT NULL COMMENT 'A - Ativa; I - Inativa',
  `id_cliente` int NOT NULL,
  PRIMARY KEY (`id_assinatura`),
  KEY `assinatura_FK` (`id_cliente`),
  CONSTRAINT `assinatura_FK` FOREIGN KEY (`id_cliente`) REFERENCES `cliente` (`id_cliente`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `assinatura_item` (
  `id_assinatura` int NOT NULL,
  `id_item` int NOT NULL,
  `quantidade` int NOT NULL,
  PRIMARY KEY (`id_assinatura`,`id_item`),
  KEY `assinatura_item_FK_1` (`id_item`),
  CONSTRAINT `assinatura_item_FK` FOREIGN KEY (`id_assinatura`) REFERENCES `assinatura` (`id_assinatura`),
  CONSTRAINT `assinatura_item_FK_1` FOREIGN KEY (`id_item`) REFERENCES `Item` (`id_item`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `venda` (
  `id_venda` int NOT NULL AUTO_INCREMENT,
  `id_cliente` int NOT NULL,
  `id_funcionario` int DEFAULT NULL,
  `data` datetime NOT NULL,
  `valor_total_venda` decimal(8,2) NOT NULL,
  PRIMARY KEY (`id_venda`),
  KEY `venda_FK` (`id_cliente`),
  KEY `venda_FK_1` (`id_funcionario`),
  CONSTRAINT `venda_FK` FOREIGN KEY (`id_cliente`) REFERENCES `cliente` (`id_cliente`),
  CONSTRAINT `venda_FK_1` FOREIGN KEY (`id_funcionario`) REFERENCES `funcionario` (`id_funcionario`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `venda_item` (
  `id_venda` int NOT NULL,
  `item` int NOT NULL,
  `id_item` int DEFAULT NULL,
  `id_assinatura` int DEFAULT NULL,
  `quantidade` int NOT NULL,
  `valor_unitario` decimal(8,2) NOT NULL,
  `valor_desconto` decimal(8,2) NOT NULL,
  `valor_total_item` decimal(8,2) NOT NULL,
  PRIMARY KEY (`id_venda`,`item`),
  KEY `venda_item_FK` (`id_item`),
  KEY `venda_item_FK_1` (`id_assinatura`),
  CONSTRAINT `venda_item_FK` FOREIGN KEY (`id_item`) REFERENCES `Item` (`id_item`),
  CONSTRAINT `venda_item_FK_1` FOREIGN KEY (`id_assinatura`) REFERENCES `assinatura` (`id_assinatura`),
  CONSTRAINT `venda_item_FK_2` FOREIGN KEY (`id_venda`) REFERENCES `venda` (`id_venda`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `venda_pagamento` (
  `id_venda` int NOT NULL,
  `forma_pagamento` varchar(60) NOT NULL,
  `qtde_parcelas` int NOT NULL,
  `status` varchar(2) NOT NULL,
  `data_confirmacao` datetime DEFAULT NULL,
  PRIMARY KEY (`id_venda`),
  CONSTRAINT `venda_pagamento_FK` FOREIGN KEY (`id_venda`) REFERENCES `venda` (`id_venda`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `venda_entrega` (
  `id_venda` int NOT NULL,
  `id_cliente` int NOT NULL,
  `seq` int NOT NULL,
  `previsao_entrega` date NOT NULL,
  `observacao` varchar(300) DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  PRIMARY KEY (`id_venda`),
  KEY `venda_entrega_FK_1` (`id_cliente`,`seq`),
  CONSTRAINT `venda_entrega_FK` FOREIGN KEY (`id_venda`) REFERENCES `venda` (`id_venda`),
  CONSTRAINT `venda_entrega_FK_1` FOREIGN KEY (`id_cliente`, `seq`) REFERENCES `cliente_endereco` (`id_cliente`, `seq`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;-- db_coffeeshop.carrinho definition

CREATE TABLE `carrinho` (
  `id_cliente` int NOT NULL,
  `id_item` int NOT NULL,
  `quantidade` decimal(8,2) NOT NULL,
  `data_atualizacao` datetime NOT NULL,
  `valor_unitario` decimal(8,2) NOT NULL,
  `valor_desconto` decimal(8,2) NOT NULL,
  `valor_total_item` decimal(8,2) NOT NULL,
  PRIMARY KEY (`id_cliente`,`id_item`),
  KEY `carrinho_FK_1` (`id_item`),
  CONSTRAINT `carrinho_FK` FOREIGN KEY (`id_cliente`) REFERENCES `cliente` (`id_cliente`),
  CONSTRAINT `carrinho_FK_1` FOREIGN KEY (`id_item`) REFERENCES `Item` (`id_item`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `funcao_acesso` (
  `id_funcao` int NOT NULL,
  `id_acesso` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `consultar` char(1) NOT NULL DEFAULT 'N',
  `inserir` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'N',
  `alterar` char(1) NOT NULL DEFAULT 'N',
  `excluir` char(1) NOT NULL DEFAULT 'N',
  PRIMARY KEY (`id_funcao`,`id_acesso`),
  KEY `funcao_acesso_FK_1` (`id_acesso`),
  CONSTRAINT `funcao_acesso_FK` FOREIGN KEY (`id_funcao`) REFERENCES `funcao` (`id_funcao`),
  CONSTRAINT `funcao_acesso_FK_1` FOREIGN KEY (`id_acesso`) REFERENCES `acesso` (`id_acesso`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

