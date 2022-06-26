from math import sqrt
from random import sample
from numpy import random
import numpy as np
from matplotlib import pyplot as plt


# Objeto que representa o indivíduo
class Individuo:
    aptidao = 0

    def __init__(self, lista_cidades):
        self.cromossomos = lista_cidades


# Objeto que representa a cidade
class Cidade:
    def __init__(self, numero_cidade, x, y):
        self.numero_cidade = numero_cidade
        self.x = x
        self.y = y


def renderizar_caminho(individuo_final):
    cromossomos = individuo_final.cromossomos

    matriz_trajeto_x = np.zeros([len(cromossomos) + 1, 1], dtype=np.float64)
    matriz_trajeto_y = np.zeros([len(cromossomos) + 1, 1], dtype=np.float64)

    for i in range(len(cromossomos)):
        matriz_trajeto_x[i] = cromossomos[i].x
        matriz_trajeto_y[i] = cromossomos[i].y

    matriz_trajeto_x[len(cromossomos)] = cromossomos[0].x
    matriz_trajeto_y[len(cromossomos)] = cromossomos[0].y

    plt.figure(3)
    plt.plot(matriz_trajeto_x, matriz_trajeto_y)
    # label do eixo x
    plt.xlabel('Distância X')
    # label do eixo y
    plt.ylabel('Distância Y')
    # label do título
    plt.title("Melhor caminho encontrado pelo Algoritmo Genético")

    plt.show(block=False)


def print_info(individuo_final):
    print(tamanho_populacao)
    print(chance_mutacao)
    print(quantidade_cidades)
    print(individuo_final.aptidao)
    numero_cidades = [i.numero_cidade for i in individuo_final.cromossomos]
    numero_cidades.append(individuo_final.cromossomos[0].numero_cidade)
    print(*numero_cidades, sep=" -> ")


def mutacao(lista_cidades):
    chance = random.random()
    if chance < chance_mutacao:
        # Troca duas posições aleatórias no caso de mutação
        posicoes = sample(range(len(lista_cidades)), 2)
        placeholder = lista_cidades[posicoes[0]]
        lista_cidades[posicoes[0]] = lista_cidades[posicoes[1]]
        lista_cidades[posicoes[1]] = placeholder

    return lista_cidades


def cycle_duplicado(pai_1, pai_2, posicao):
    posicao_duplicado = filter(lambda x: (x != posicao), [i for i, x in enumerate(pai_1) if x == pai_1[posicao]])
    outra_posicao = next(posicao_duplicado)

    cycle_pai(pai_1, pai_2, outra_posicao)

    return outra_posicao


def has_duplicado(lista):
    return any(lista.count(element) > 1 for element in lista)


def cycle_pai(pai_1, pai_2, posicao):
    placeholder = pai_1[posicao]
    pai_1[posicao] = pai_2[posicao]
    pai_2[posicao] = placeholder


def cycle(pai_1, pai_2):
    filhos = []

    posicao = random.randint(0, len(pai_1))
    # Faz o ciclo em uma posição aleatória
    cycle_pai(pai_1, pai_2, posicao)

    # Realiza o ciclo até não houver mais duplicados
    while has_duplicado(pai_1):
        posicao = cycle_duplicado(pai_1, pai_2, posicao)

    # Faz a mutação depois da criação dos novos
    pai_1 = mutacao(pai_1)
    pai_2 = mutacao(pai_2)

    # Filhos vão
    filhos.append(Individuo(pai_1[:]))
    filhos.append(Individuo(pai_2[:]))

    return filhos


# Seleciona usando probabilidades aleatórias criadas anteriormente
def selecionar_roleta(individuos, intervalos_probabilidade, individuos_selecionados):
    selecionar = False

    while not selecionar:
        selecionado = random.random()

        for i in range(len(intervalos_probabilidade)):
            if selecionado < intervalos_probabilidade[i]:
                # Verificação se número já está nos selecionados
                if individuos[i] not in individuos_selecionados:
                    return individuos[i]

                break


# Calcula os intervalos que vão gerar a probabilidade final
def calcular_intervalo_individuos(lista_probabilidade):
    lista_intervalo = []
    intervalo_anterior = 0

    for probabilidade in lista_probabilidade:
        probabilidade_atual = intervalo_anterior + probabilidade
        lista_intervalo.append(probabilidade_atual)
        intervalo_anterior = probabilidade_atual

    return lista_intervalo


def calcular_probabilidades_roleta(individuos, probabilidade_total_invertida):
    # Gera a lista baseada no cálculo anterior
    return [(1 / individuo.aptidao) / probabilidade_total_invertida for individuo in individuos]


def calcular_probabilidade_total_invertida(individuos):
    total = 0
    for individuo in individuos:
        total += 1 / individuo.aptidao
    return total


def calcular_intervalo_roleta(individuos):
    # Calcula o total do somatório da inversão de todas as funções de aptidão
    probabilidade_total_invertida = calcular_probabilidade_total_invertida(individuos)
    # Calcula a probabilidade de cada aptidão aparecer
    lista_probabilidades = calcular_probabilidades_roleta(individuos, probabilidade_total_invertida)
    # Divide a probabilidade em intervalos de 0 a 1 para poder ser usado o random depois
    intervalos_probabilidade = calcular_intervalo_individuos(lista_probabilidades)

    return intervalos_probabilidade


def criar_filhos(todos_pais):
    # Faz toda parte do cálculo para definição de probabilidade da roleta
    intervalos = calcular_intervalo_roleta(todos_pais)

    filhos = []
    # Dividido por 2 pois cada par de pais gera um par de filhos
    for i in range(len(todos_pais) // 2):
        pai_1 = selecionar_roleta(todos_pais, intervalos, []).cromossomos[:]
        # Adiciona o pai_1 na lista da população para não escolher, para evitar indivíduos iguais
        pai_2 = selecionar_roleta(todos_pais, intervalos, [pai_1]).cromossomos[:]

        novos_filhos = cycle(pai_1, pai_2)
        filhos.extend(novos_filhos)

    return filhos


def calcular_caminho(individuo):
    distancia_total = 0
    cidades_visita = individuo.cromossomos[:]
    # Como tem que voltar para a cidade inicial, o programa faz um append do primeiro item no final da lista
    # para calculo
    cidades_visita.append(cidades_visita[0])

    cidade_anterior = cidades_visita[0].numero_cidade
    for i in range(len(cidades_visita)):
        cidade_atual = cidades_visita[i].numero_cidade
        # Pega a distância do caminho com base na tabela de distancias criada anteriormente
        distancia_total += distancias[cidade_anterior][cidade_atual]
        cidade_anterior = cidade_atual

    # Quando calcula a função de aptidão, atribui o valor ao individuo para não ser necessário calcular novamente
    individuo.aptidao = distancia_total

    return distancia_total


def processar_geracao(individuos: list):
    # Ordena os indivíduos da lista com base na função de aptidão
    individuos.sort(key=calcular_caminho)

    # Mata a pior metade dos individuos da geração
    pais = individuos[:len(individuos) // 2]
    # cria o resto da geração
    filhos = criar_filhos(pais)

    # Adiciona os pais e filhos na nova geração
    novos_individuos = []
    novos_individuos.extend(pais)
    novos_individuos.extend(filhos)

    return novos_individuos


def gerar_populacao_inicial():
    # população inicial que vai conter a lista de cidades não repetida em ordem aleatória
    return [Individuo(sample(cidades, quantidade_cidades)) for _ in range(tamanho_populacao)]


def calcular_distancia_cidades(cidade_1, cidade_2):
    dif_x = cidade_1.x - cidade_2.x
    dif_y = cidade_1.y - cidade_2.y

    return sqrt((dif_x ** 2) + (dif_y ** 2))


def gerar_tabela_distancias():
    tabela_distancia = []

    # Calcula a distância de um ponto para todos os outros e guarda o valor em uma tabela
    for i in range(len(cidades)):
        distancias_i = []
        for f in range(len(cidades)):
            distancias_i.append(calcular_distancia_cidades(cidades[i], cidades[f]))
        tabela_distancia.append(distancias_i)

    return tabela_distancia


def gerar_cidades():
    lista_cidades = []
    for i in range(quantidade_cidades):
        x = random.random()
        y = random.random()
        lista_cidades.append(Cidade(i, x, y))
    return lista_cidades


# Parâmetros de inicialização
quantidade_cidades = 20
# Por causa do jeito que divisão de inteiros em python funciona, o tamanho da população só pode ser números pares
tamanho_populacao = 20
quantidade_interacoes = 10000
chance_mutacao = 0.05

# Geração da posição de todas as cidades
cidades = gerar_cidades()
# Cálculo das distâncias pra otimizar utilizações futuras
distancias = gerar_tabela_distancias()
# Geração da população inicial aleatória
populacao_inicial = gerar_populacao_inicial()

populacao_gerada = populacao_inicial[:]
for _ in range(quantidade_interacoes):
    # Faz o processamento de toda ocorrência das gerações
    populacao_gerada = processar_geracao(populacao_gerada)

populacao_gerada.sort(key=calcular_caminho)

melhor_individuo = populacao_gerada[0]

# Print e plot das informações no final
print_info(melhor_individuo)
renderizar_caminho(melhor_individuo)
