import requests
import json
from datetime import datetime

# 🔐 Seu token de acesso ao Tiny ERP
TOKEN = '9c49579f4c8778127df8b120b76addb0b315247dcc6b5f4c1d1bdbc640b8511e'
HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}

BASE_URL = "https://api.tiny.com.br/api2"


# 🔍 1. Buscar produtos cadastrados
def buscar_produtos(pesquisa=None):
    url = f"{BASE_URL}/produtos.pesquisa.php"
    params = {
        "token": TOKEN,
        "formato": "json"
    }
    if pesquisa:
        params["pesquisa"] = pesquisa
    response = requests.get(url, params=params, verify=False)
    return response.json()


# 🔍 2. Obter detalhes de um produto específico pelo código
def obter_produto(codigo_produto):
    url = f"{BASE_URL}/produto.obter.php"
    params = {
        "token": TOKEN,
        "formato": "json",
        "codigo": codigo_produto
    }
    response = requests.get(url, params=params, verify=False)
    return response.json()


# 🚚 3. Listar transportadoras
def listar_transportadoras():
    url = f"{BASE_URL}/transportadoras.pesquisa.php"
    params = {
        "token": TOKEN,
        "formato": "json"
    }
    response = requests.get(url, params=params, verify=False)
    return response.json()


# 💳 4. Lista de formas de pagamento (manual/local)
def listar_formas_pagamento():
    # Essa informação normalmente vem de um cadastro fixo seu.
    # A API do Tiny NÃO retorna isso diretamente.
    return [
        "Boleto",
        "Cartão de Crédito",
        "Depósito Bancário",
        "PIX",
        "Dinheiro"
    ]


# 🧾 5. Criar um novo pedido
def criar_pedido(pedido_dict):
    url = f"{BASE_URL}/pedido.incluir.php"
    
    # Pedido deve estar como string JSON com aspas escapadas
    pedido_json = json.dumps(pedido_dict).replace('"', '\\"')
    
    data = {
        "token": TOKEN,
        "formato": "json",
        "pedido": pedido_json
    }
    
    response = requests.post(url, headers=HEADERS, data=data)
    return response.json()


def buscar_todos_produtos():
    url = f"{BASE_URL}/produtos.pesquisa.php"
    pagina = 1
    todos_produtos = []

    while True:
        params = {
            "token": TOKEN,
            "formato": "json",
            "pagina": pagina
        }
        response = requests.get(url, params=params)
        dados = response.json()

        produtos = dados.get("retorno", {}).get("produtos", [])
        if not produtos:
            break

        todos_produtos.extend(produtos)
        pagina += 1

        if len(produtos) < 50:
            break  # Última página

    return todos_produtos


# 📋 FUNÇÕES DOS PEDIDOS (API PRINCIPAL)
def buscar_todos_pedidos(data_inicial=None, data_final=None, situacao=None):
    """
    Busca todos os pedidos com paginação automática
    Conforme documentação oficial da API pedidos.pesquisa.php
    
    Args:
        data_inicial (str): Data inicial no formato 'dd/mm/yyyy' (opcional)
        data_final (str): Data final no formato 'dd/mm/yyyy' (opcional)
        situacao (str): Situação do pedido (opcional)
    
    Returns:
        list: Lista com todos os pedidos encontrados
    """
    url = f"{BASE_URL}/pedidos.pesquisa.php"
    pagina = 1
    todos_pedidos = []

    # Parâmetros base (pelo menos um filtro é obrigatório)
    params_base = {
        "token": TOKEN,
        "formato": "json"
    }
    
    # Adiciona filtros se fornecidos
    if data_inicial:
        params_base["dataInicial"] = data_inicial
    if data_final:
        params_base["dataFinal"] = data_final
    if situacao:
        params_base["situacao"] = situacao
    
    # Se nenhum filtro foi fornecido, usar data dos últimos 7 dias
    if not any([data_inicial, data_final, situacao]):
        from datetime import datetime, timedelta
        data_final_auto = datetime.now().strftime("%d/%m/%Y")
        data_inicial_auto = (datetime.now() - timedelta(days=7)).strftime("%d/%m/%Y")
        params_base["dataInicial"] = data_inicial_auto
        params_base["dataFinal"] = data_final_auto
        print(f"🗓️ Usando filtro automático: {data_inicial_auto} a {data_final_auto}")

    while True:
        params = params_base.copy()
        params["pagina"] = pagina
            
        try:
            response = requests.get(url, params=params, verify=False)
            dados = response.json()

            # Verifica se houve erro na resposta
            if dados.get("retorno", {}).get("status") == "Erro":
                print(f"❌ Erro na API: {dados.get('retorno', {}).get('erros', [])}")
                break

            # Extrai os pedidos da resposta
            pedidos = dados.get("retorno", {}).get("pedidos", [])
            
            if not pedidos:
                break  # Não há mais pedidos

            todos_pedidos.extend(pedidos)
            print(f"📄 Página {pagina}: {len(pedidos)} pedidos carregados")
            pagina += 1

            # Se retornou menos que o limite da página, é a última página
            if len(pedidos) < 100:  # Documentação oficial: 100 registros por página
                break
                
        except Exception as e:
            print(f"❌ Erro ao buscar página {pagina}: {str(e)}")
            break

    print(f"✅ Total de pedidos carregados: {len(todos_pedidos)}")
    return todos_pedidos


def buscar_pedidos_com_filtros(numero=None, cliente=None, cpf_cnpj=None, 
                              data_inicial=None, data_final=None, 
                              situacao=None, numero_ecommerce=None,
                              id_vendedor=None, nome_vendedor=None,
                              marcador=None, pagina=1):
    """
    Busca pedidos com filtros específicos (uma página)
    Conforme documentação oficial da API pedidos.pesquisa.php
    
    Args:
        numero (str): Número do pedido no Tiny
        cliente (str): Nome ou código do cliente
        cpf_cnpj (str): CPF ou CNPJ do cliente
        data_inicial (str): Data inicial no formato 'dd/mm/yyyy'
        data_final (str): Data final no formato 'dd/mm/yyyy'
        situacao (str): Situação do pedido
        numero_ecommerce (str): Número do pedido no ecommerce
        id_vendedor (str): ID do vendedor
        nome_vendedor (str): Nome do vendedor
        marcador (str): Descrição do marcador
        pagina (int): Número da página
    
    Returns:
        dict: Resposta completa da API
    """
    url = f"{BASE_URL}/pedidos.pesquisa.php"
    params = {
        "token": TOKEN,
        "formato": "json",
        "pagina": pagina
    }
    
    # Adiciona filtros fornecidos
    if numero:
        params["numero"] = numero
    if cliente:
        params["cliente"] = cliente
    if cpf_cnpj:
        params["cpf_cnpj"] = cpf_cnpj
    if data_inicial:
        params["dataInicial"] = data_inicial
    if data_final:
        params["dataFinal"] = data_final
    if situacao:
        params["situacao"] = situacao
    if numero_ecommerce:
        params["numeroEcommerce"] = numero_ecommerce
    if id_vendedor:
        params["idVendedor"] = id_vendedor
    if nome_vendedor and not id_vendedor:  # nome_vendedor é ignorado se idVendedor for informado
        params["nomeVendedor"] = nome_vendedor
    if marcador:
        params["marcador"] = marcador
    
    response = requests.get(url, params=params, verify=False)
    
    result = response.json()
    
    return result


def salvar_pedidos_txt(pedidos):
    """
    Salva pedidos em formato enxuto para RAG
    Conforme estrutura da API pedidos.pesquisa.php
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"tiny_pedidos_rag_{timestamp}.txt"
    
    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
            arquivo.write("PEDIDOS:\n")
            
            for pedido in pedidos:
                p = pedido.get('pedido', pedido)
                
                # Dados básicos do pedido (conforme documentação oficial)
                numero = p.get('numero', 'N/A')
                numero_ecommerce = p.get('numero_ecommerce', 'N/A')
                data_pedido = p.get('data_pedido', 'N/A')
                nome_cliente = p.get('nome', 'N/A')
                valor = p.get('valor', '0.00')
                situacao = p.get('situacao', 'N/A')
                vendedor = p.get('nome_vendedor', 'N/A')
                codigo_rastreamento = p.get('codigo_rastreamento', 'N/A')
                
                arquivo.write(f"Num:{numero}|NumEcomm:{numero_ecommerce}|Data:{data_pedido}|Cliente:{nome_cliente}|Valor:R${valor}|Status:{situacao}|Vendedor:{vendedor}|Rastreio:{codigo_rastreamento}\n")
            
        print(f"✅ Arquivo de pedidos salvo: {nome_arquivo}")
        return nome_arquivo
        
    except Exception as e:
        print(f"❌ Erro ao salvar pedidos: {str(e)}")
        return None


# 💾 Função para salvar dados em arquivo TXT (ENXUTO PARA RAG)
def salvar_dados_txt(produtos, formas_pagamento):
    """
    Salva produtos e formas de pagamento em formato enxuto para RAG
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"tiny_erp_rag_{timestamp}.txt"
    
    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
            # Produtos em formato compacto
            arquivo.write("PRODUTOS:\n")
            for produto in produtos:
                p = produto.get('produto', produto)
                nome = p.get('nome', 'N/A')
                preco = p.get('preco', '0.00')
                unidade = p.get('unidade', 'N/A')
                arquivo.write(f"Nm:{nome}|R${preco}|Unit:{unidade}\n")
            
            # Formas de pagamento
            arquivo.write("\nPAGAMENTO:\n")
            arquivo.write("|".join(formas_pagamento) + "\n")
            
        print(f"✅ Arquivo RAG salvo: {nome_arquivo}")
        return nome_arquivo
        
    except Exception as e:
        print(f"❌ Erro ao salvar: {str(e)}")
        return None


# 💾 Função combinada para salvar produtos E pedidos
def salvar_dados_completos_txt(produtos, pedidos, formas_pagamento):
    """
    Salva produtos, pedidos e formas de pagamento em um arquivo completo para RAG
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"tiny_erp_completo_rag_{timestamp}.txt"
    
    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
            # Produtos em formato compacto
            arquivo.write("PRODUTOS:\n")
            for produto in produtos:
                p = produto.get('produto', produto)
                nome = p.get('nome', 'N/A')
                preco = p.get('preco', '0.00')
                unidade = p.get('unidade', 'N/A')
                arquivo.write(f"Nm:{nome}|R${preco}|Unit:{unidade}\n")
            
            # Pedidos
            arquivo.write("\nPEDIDOS:\n")
            for pedido in pedidos:
                p = pedido.get('pedido', pedido)
                numero = p.get('numero', 'N/A')
                data_pedido = p.get('data_pedido', 'N/A')
                nome_cliente = p.get('nome', 'N/A')
                valor = p.get('valor', '0.00')
                situacao = p.get('situacao', 'N/A')
                arquivo.write(f"Num:{numero}|Data:{data_pedido}|Cliente:{nome_cliente}|Valor:R${valor}|Status:{situacao}\n")
            
            # Formas de pagamento
            arquivo.write("\nPAGAMENTO:\n")
            arquivo.write("|".join(formas_pagamento) + "\n")
            
        print(f"✅ Arquivo completo RAG salvo: {nome_arquivo}")
        return nome_arquivo
        
    except Exception as e:
        print(f"❌ Erro ao salvar dados completos: {str(e)}")
        return None


# Exemplo de uso no main para pedidos
def exemplo_uso_pedidos():
    print("🔍 Buscando TODOS os pedidos (últimos 7 dias)...")
    pedidos = buscar_todos_pedidos()
    
    if pedidos:
        print(f"✅ {len(pedidos)} pedidos encontrados!")
        
        print("\n💾 Salvando pedidos em arquivo TXT...")
        arquivo_salvo = salvar_pedidos_txt(pedidos)
        
        if arquivo_salvo:
            print(f"🎉 Arquivo de pedidos criado: '{arquivo_salvo}'")
    else:
        print("❌ Nenhum pedido encontrado ou erro na busca")
    
    # Exemplo de busca com filtros específicos
    print("\n🔍 Exemplo: Buscando pedidos com situação 'Aprovado'...")
    resultado_filtrado = buscar_pedidos_com_filtros(situacao="Aprovado", pagina=1)
    
    if resultado_filtrado.get('retorno', {}).get('status') == 'OK':
        pedidos_filtrados = resultado_filtrado.get('retorno', {}).get('pedidos', [])
        numero_paginas = resultado_filtrado.get('retorno', {}).get('numero_paginas', 0)
        print(f"✅ Página 1 de {numero_paginas}: {len(pedidos_filtrados)} pedidos aprovados")
    else:
        print("❌ Erro ao buscar pedidos filtrados")
    
    # Exemplo de busca por cliente
    print("\n🔍 Exemplo: Buscando pedidos por nome de cliente...")
    resultado_cliente = buscar_pedidos_com_filtros(cliente="João", pagina=1)
    
    if resultado_cliente.get('retorno', {}).get('status') == 'OK':
        pedidos_cliente = resultado_cliente.get('retorno', {}).get('pedidos', [])
        print(f"✅ {len(pedidos_cliente)} pedidos encontrados para clientes com 'João'")
    else:
        print("❌ Erro ao buscar pedidos por cliente")


# 🧪 Exemplo de uso COMPLETO
if __name__ == "__main__":
    print("🔍 Buscando TODOS os produtos...")
    produtos = buscar_todos_produtos()
    print(f"✅ {len(produtos)} produtos encontrados!")

    print("\n💳 Carregando formas de pagamento...")
    formas_pagamento = listar_formas_pagamento()
    print(f"✅ {len(formas_pagamento)} formas de pagamento carregadas!")

    print("\n💾 Salvando dados em arquivo TXT enxuto...")
    arquivo_salvo = salvar_dados_txt(produtos, formas_pagamento)
    
    if arquivo_salvo:
        print(f"\n🎉 Arquivo RAG criado: '{arquivo_salvo}'")
        print("Formato enxuto otimizado para LLM!")
    else:
        print("\n❌ Falha ao salvar o arquivo.")

    # Nova funcionalidade de pedidos
    print("\n" + "="*50)
    print("📋 PROCESSANDO PEDIDOS")
    print("="*50)
    
    pedidos = buscar_todos_pedidos()
    
    if pedidos:
        print("\n💾 Criando arquivo completo com produtos E pedidos...")
        arquivo_completo = salvar_dados_completos_txt(produtos, pedidos, formas_pagamento)
        
        if arquivo_completo:
            print(f"🎉 Arquivo COMPLETO criado: '{arquivo_completo}'")
            print("Contém: Produtos + Pedidos + Formas de Pagamento!")
        
        # Demonstração de filtros
        print("\n🔍 Testando filtros...")
        exemplo_uso_pedidos()

    # Exemplo comentado de criação de pedido
    # print("\n🧾 Enviando um pedido de exemplo:")
    # pedido_exemplo = {
    #     "pedido": {
    #         "data_pedido": "2025-06-01",
    #         "cliente": {
    #             "nome": "João da Silva",
    #             "cpf_cnpj": "12345678900",
    #             "endereco": "Rua Exemplo",
    #             "numero": "123",
    #             "bairro": "Centro",
    #             "cep": "12345000",
    #             "cidade": "São Paulo",
    #             "uf": "SP",
    #             "email": "joao@example.com"
    #         },
    #         "itens": [
    #             {
    #                 "item": {
    #                     "codigo": "PROD001",
    #                     "descricao": "Produto Exemplo",
    #                     "un": "pc",
    #                     "qtde": 1,
    #                     "vlr_unit": 100.00
    #                 }
    #             }
    #         ],
    #         "forma_pagamento": "PIX",
    #         "transporte": {
    #             "transportadora": "Correios",
    #             "frete_por_conta": "0",
    #             "peso_bruto": "1.000",
    #             "volumes": "1",
    #             "servico_correios": "PAC"
    #         }
    #     }
    # }
    # resposta_pedido = criar_pedido(pedido_exemplo)
    # print(json.dumps(resposta_pedido, indent=2, ensure_ascii=False))