import numpy as np
import itertools as it
import copy
import time
###Leitura do arquivo
## Função para ler o arquivo
def leitura_arquivo(path):
    file = open(path,'r')

    linha = file.readline()
    ##Declrando variavel global
    global numeroVisitasPorAgente, dimensao, matrizCustos

    dimensao = int(linha.split()[1])

    linha = file.readline()

    numeroVisitasPorAgente = int(linha.split()[1])

    linha = file.readline()
    ###Criacao da matriz de custos
    matrizCustos = np.zeros((dimensao,dimensao),dtype=int)
    ### Transfere os valores do arquivo pra matrizcusto
    for linhaCusto in range(dimensao):
        linha = file.readline()
        matrizCustos[linhaCusto][:] = linha.split()
    file.close()


def vizinhomaisprox(matriz):
    enderecoAtual = 0
    s = []
    s.append([])
    enderecos = []
    
    # Preenchendo uma lista com todos os vértices
    for i in range(1,dimensao):
        enderecos.append(i)
    
    contador_agentes=0
    dim = dimensao - 1

    # Enquanto ainda houverem endereços a serem visitados vai executar
    while (enderecos != []):
        dim = dim - 1
        
        i=0
        melhorCustoProxEndereco = matriz[0][0]

        # Procura o caminho mais curto
        for endereco in enderecos:
            custoProxEndereco = matriz[enderecoAtual][endereco] 
            if custoProxEndereco < melhorCustoProxEndereco:
                melhorCustoProxEndereco = custoProxEndereco
                indice_endereco = i
            i+=1

        # Começa a rota de um novo agente
        if (len(s[contador_agentes]) == numeroVisitasPorAgente):
            enderecoAtual = 0
            s.append([])
            contador_agentes+=1
        s[contador_agentes].append(enderecos[indice_endereco])
        enderecoAtual = enderecos[indice_endereco]
        del enderecos[indice_endereco] # remove o endereço da lista de endereços
    
    # Tratamento para adicionar o ínicio e fim da rota    
    for agente in s:
        agente.insert(0,0)
        agente.append(0)
    return s

#Calculo custo de cada rota individual
def calculaCustoRota(matriz,solucao_ini,indice_rota):
    custoRota = 0
    rota = solucao_ini[indice_rota]
    tamanhoRota = len(rota)
    for i in range(tamanhoRota):
        j = i + 1
        vertice = rota[i]
        proximo_vertice = rota[j]
        custoArco = matriz[vertice][proximo_vertice]
        custoRota += custoArco
        if proximo_vertice == 0:
            break
    return custoRota
#Calculo do custo de uma solucao
def calculaCustoSolucao(matriz,solucao_ini):
    custoSolucao = 0
    for i in range(len(solucao_ini)):
        custoSolucao += calculaCustoRota(matriz,solucao_ini,i)
    return custoSolucao

# Função que faz o movimento do 2-opt
def vnd_2optSwap(rota, i, j):
    nova_rota = copy.deepcopy(rota)
    aux = []

    # Adiciona todos os itens a serem invertidos em uma lista auxiliar
    for k in range(len(rota)):
        if k >= i and k <= j:
            aux.append(rota[k])

    # Vai desempilhando os itens e adicionando em uma lista
    for k in range(len(rota)):
        if k >= i and k <= j:
            nova_rota[k] = aux.pop()

    return nova_rota

def VND_2_opt(matriz, solucao_ini):
    custos_iniciais=[]
    melhorRota=[]
    melhorCusto=[]

    rota = copy.deepcopy(solucao_ini)

    # calculando os custos iniciais das rotas de cada agente
    for cont in range(len(solucao_ini)):
        custos_iniciais.append(calculaCustoRota(matriz, solucao_ini, cont))

    melhorCusto = copy.deepcopy(custos_iniciais)

    # Executa para a rota de cada agente
    for numRota in range(len(solucao_ini)):
        melhorRota.append(rota[numRota])
        
        # Roda enquanto houverem mudanças
        flagBreak = 1
        while flagBreak:

            flagBreak = 0
            
            # Itera o lado esquerdo do "corte" do 2-opt
            for i in range(1, numeroVisitasPorAgente-1):

                if i >= (len(rota[numRota])-1):
                        break

                # Itera o lado direito do "corte" do 2-opt
                for j in range(i+3, numeroVisitasPorAgente -1): 
                    
                    if j >= (len(rota[numRota])-1):
                        break
                    
                    # calculo dos custos das arestas
                    custoArestasAdicionadas = matriz[rota[numRota][i-1]][rota[numRota][j]] + matriz[rota[numRota][i]][rota[numRota][j+1]] 

                    custoArestasRemovidas = matriz[rota[numRota][i-1]][rota[numRota][i]] + matriz[rota[numRota][j]][rota[numRota][j+1]]

                    novo_custo = custos_iniciais[numRota] - custoArestasRemovidas + custoArestasAdicionadas

                    if (novo_custo < melhorCusto[numRota]):

                        nova_rota = vnd_2optSwap(rota[numRota], i, j)

                        melhorRota[numRota] = copy.deepcopy(nova_rota)
                        melhorCusto[numRota] = copy.deepcopy(novo_custo)
                        flagBreak = 1
                        break
                if flagBreak:
                    break

    return melhorRota

#Movimento de Swap local
def VND_swap(matriz,solucao_ini):
    solucaoFinal = [] #Array com a solucao final
    indexRota = 0
    for rota in solucao_ini:
        rotaOriginal = copy.deepcopy(rota) #Copia da rota
        melhorRota = copy.deepcopy(rotaOriginal)
        rotaAtual = copy.deepcopy(rotaOriginal)
        tamanhoRota = len(rota)
        custoRotaOriginal = calculaCustoRota(matriz,solucao_ini,indexRota)
        custoMelhorRota = custoRotaOriginal
        for x in range(1,tamanhoRota-1):
            j = x + 1
            for y in range(j,tamanhoRota-1):
                rotaAtual = copy.deepcopy(rotaOriginal) #Reset da rota atual

                auxiliar = rotaAtual[x]
                rotaAtual[x] = rotaAtual[y] #Swap
                rotaAtual[y] = auxiliar
                # calculo do custo das arestas adicionadas e removidas 
                custoArestasAdicionadas = matriz[rotaAtual[x]][rotaAtual[x-1]] + matriz[rotaAtual[x]][rotaAtual[x+1]] + matriz[rotaAtual[y]][rotaAtual[y-1]] + matriz[rotaAtual[y]][rotaAtual[y+1]]

                custoArestasRemovidas = matriz[rotaOriginal[x]][rotaOriginal[x-1]] + matriz[rotaOriginal[x]][rotaOriginal[x+1]] + matriz[rotaOriginal[y]][rotaOriginal[y-1]] + matriz[rotaOriginal[y]][rotaOriginal[y+1]]
                
                custoRotaAtual = custoRotaOriginal - custoArestasRemovidas + custoArestasAdicionadas

                if(custoRotaAtual < custoMelhorRota):
                    melhorRota = copy.deepcopy(rotaAtual)
                    custoMelhorRota = custoRotaAtual
        solucaoFinal.append(melhorRota) #Adiciona a rota na lista da solucao
        indexRota += 1 #Vai para a proxima rota
    return solucaoFinal

#Swap inter rotas
def VND_swap_inter(matriz,solucao_ini):
    solucaoOriginal = copy.deepcopy(solucao_ini)
    custoSolucaoOriginal = calculaCustoSolucao(matriz,solucao_ini)
    customelhorSolucao = custoSolucaoOriginal
    melhorSolucao = copy.deepcopy(solucaoOriginal)
    tamanhoSolucao = len(solucaoOriginal)
    listaIndicesRotas = list(range(tamanhoSolucao)) #Lista com indices, de 0 a tamanho-1
    for combinacao in it.combinations(listaIndicesRotas,2): #Combinacao dois a dois de cada rota da solucao
        solucaoTemporaria = copy.deepcopy(solucaoOriginal)
        indiceRotaUm, indiceRotaDois = combinacao
        rotaUm = solucaoTemporaria[indiceRotaUm]
        rotaDois = solucaoTemporaria[indiceRotaDois]
        tamanhoRotaUm = len(rotaUm)
        tamanhoRotaDois = len(rotaDois)
        for i in range(tamanhoRotaUm-1): #Troca um a um de elementos entre as duas rotas escolhidas anteriormente
            if rotaUm[i] != 0:
                for j in range(tamanhoRotaDois-1):
                    solucaoTemporaria = copy.deepcopy(solucaoOriginal)
                    rotaUm = solucaoTemporaria[indiceRotaUm]
                    rotaDois = solucaoTemporaria[indiceRotaDois]
                    if rotaDois[j] != 0:
                        rotaUm[i], rotaDois[j] = rotaDois[j], rotaUm[i] #Swap
                        custoSolucaoTemporaria = calculaCustoSolucao(matriz,solucaoTemporaria)
                        if custoSolucaoTemporaria < customelhorSolucao:
                            melhorSolucao = solucaoTemporaria
        
    return melhorSolucao

###Criando função VND
def VND_teste(matriz,solucao_ini):
    melhorSolucao = copy.deepcopy(solucao_ini)
    solucaoAtual = copy.deepcopy(melhorSolucao)
    custoMelhorSolucao = calculaCustoSolucao(matriz,melhorSolucao)
    k = 1
    while k <= 3:
        if k == 1:
            solucaoAtual = VND_swap(matriz,solucaoAtual)
        elif k == 2:
            solucaoAtual = VND_swap_inter(matriz,solucaoAtual)
        elif k == 3:
            solucaoAtual = VND_2_opt(matriz,solucaoAtual)
        custoSolucaoAtual = calculaCustoSolucao(matriz, solucaoAtual)
        if custoSolucaoAtual < custoMelhorSolucao:
            melhorSolucao = solucaoAtual
            custoMelhorSolucao = custoSolucaoAtual
            k = 1
        else:
            k += 1
    return melhorSolucao


caminhoArquivo = 'n52p11.txt'
leitura_arquivo(caminhoArquivo)

ini_construcao = time.time()

solucao_inicial = vizinhomaisprox(matrizCustos)

fim_construcao = time.time()

print("tempo Heuristica de construcao: ", fim_construcao-ini_construcao)

print("solucao inicial:", solucao_inicial)

custoSolucaoInicial = calculaCustoSolucao(matrizCustos, solucao_inicial)

print("Custo solucao inicial: ", custoSolucaoInicial)

print("")

ini = time.time()

melhorSolucaoGlobal = VND_teste(matrizCustos,solucao_inicial)

fim = time.time()

print("tempo: ", fim-ini)

print("Print melhor solucao global: ", melhorSolucaoGlobal)

custoMelhorSolucaoGlobal = calculaCustoSolucao(matrizCustos,melhorSolucaoGlobal)

print("Print custo melhor solucao global: ", custoMelhorSolucaoGlobal)