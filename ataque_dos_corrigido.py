import os
from os.path import abspath, dirname
import csv
import py_dss_interface
import numpy as np
import matplotlib.pyplot as plt
import random

# Instância do OpenDSS
dss = py_dss_interface.DSS()

# ========================= CONTROLE SOC COM DEGRADAÇÃO =========================
# Variáveis globais do ataque DoS

dados_salvos_antes_do_ataque = False
x = 0 # variável que atualiza os instantes de tempo
atacando = False
# Variáveis globais do controle
soc_max = 100
soc_min = 0
contador_soc_max = 60
contador_soc_min = 40
taxa_degradacao = 1.0
contador_ciclos = 0
carga_completa = False
descarga_completa = False

soc_lista = []
soc_lista_2 = []
soc_ataque_lista = []
soc_max_lista = []
soc_min_lista = []
passos = []
taxa_degradacao_por_ciclo = 0.009
soh = 100.0  
iteracoes = []
soh_lista = []
kW_painel_lista = []
kW_carga_lista = []
kW_bateria_lista = []

# Variáveis globais
estado_anterior = 0  # Começa como 0 para detectar o primeiro 1
y_tau_y = None       # Valor do sensor antes do ataque
dados_salvos_antes_do_ataque = False

def bernoulli(p: float) -> int:
    if not 0 <= p <= 1:
        raise ValueError("O valor de p deve estar entre 0 e 1.")
    return 1 if random.random() < p else 0

def ataque_DoS():
    global estado_anterior
    global dados_salvos_antes_do_ataque
    global y_tau_y
    global soc_ataque

    # puxar o valor do soc_2 pra ficar de acordo com o gráfico
    dss.circuit._set_active_element("Storage.Bateria")
    soc_ataque = float(dss.dssproperties._value_read("23"))

    yk = np.array([  #sinal que deveria chegar ao controlador e detector de anomalias
        [soc_ataque]
    ])
    #print(f"yk:{yk}")
    # Gera valor binário (0 ou 1) com Bernoulli
    resultado = bernoulli(0.77)
    Sky = np.array([      #matriz binária que indica se o ataque DoS está sendo performado ou não, varia com o tempo
        [resultado]  #depende do passo de simulação!!!
    ])
    #print(f"Resultado Bernoulli: {resultado}")

    # Detecta transição de 0 → 1
    if resultado == 1 and estado_anterior == 0:
        y_tau_y = np.array([[soc_ataque]])  # salva o valor do sensor
        dados_salvos_antes_do_ataque = True
        print(f"Transição detectada: salvando soc de ataque = {soc_ataque:.3f}")
    else:
        dados_salvos_antes_do_ataque = False

    estado_anterior = resultado  # atualiza para próxima chamada

    # Exibe estado atual
    #print(f"y_tau_y: {y_tau_y}")
    #print(f"dados_salvos_antes_do_ataque: {dados_salvos_antes_do_ataque}\n")

    #Sku = np.array([1])  #matriz binária que indica se o ataque DoS está sendo performado ou não, também varia com o tempo 

    Gamma_y = np.array([     #matriz binária que indica se o adversário possui ou não acesso aos sensores
        [1]
    ])

    Gamma_y_transposta = Gamma_y.T  #matriz gama y maiúsculo transposta

    #operações para negação de serviço dos sensores
    subtracaoy = yk - y_tau_y #diferença entre o sinal que deveria ser injetado no controlador e o último sinal medido antes do ataque   
    multiplicacao1 = np.dot(Sky, Gamma_y_transposta)  #multiplicação entre a matriz que indica se o ataque está ocorrendo em determinado tempo k e a matriz que mostra os sensores que o aversário domina
    multiplicacao2 = np.dot(multiplicacao1, subtracaoy)
    byk = multiplicacao2 * -1  #matriz resultante do ataque DoS
    multiplicacao3 = np.dot(Gamma_y , byk)
    y_til_k = yk + multiplicacao3  #Sinal dos sensores negado 
    soc_ataque = y_til_k
    print(f"resultado do ataque{soc_ataque}")
        
    return soc_ataque

def aplicar_degradacao_soc(soc_max_atual, soc_min_atual, taxa_degradacao, limite_superior=60, limite_inferior=40):
    novo_soc_max = max(soc_max_atual - taxa_degradacao, limite_superior)
    novo_soc_min = min(soc_min_atual + taxa_degradacao, limite_inferior)
    return novo_soc_max, novo_soc_min

def controle_soc_por_ciclo(stepNumber):
    global soc_max, soc_min, contador_ciclos, carga_completa, descarga_completa, soh, x
    global kW_painel_lista, kW_bateria_lista, kW_carga_lista 

    dss.circuit._set_active_element("Storage.Bateria")
    soc = float(dss.dssproperties._value_read("23"))
    
    kW_bateria = float(dss.dssproperties._value_read("5"))

    dss.circuit._set_active_element("Load.634a")
    kW_carga = dss.cktelement._powers()[0]

    dss.circuit._set_active_element("PVSystem.PV")
    kW_painel = dss.cktelement._powers()[0] * (-1)

    # Salva para gráficos
    soc_lista.append(soc)
    soc_max_lista.append(soc_max)
    soc_min_lista.append(soc_min)
    passos.append(stepNumber)
    soh_lista.append(soh)  
    kW_carga_lista.append(kW_carga)
    kW_painel_lista.append(kW_painel)
    kW_bateria_lista.append(kW_bateria)

    # Aplicação do controle
    if soc > soc_max:
        dss.text("Edit Storage.Bateria %Charge=0 dispmode=external %stored=" + str(soc_max))

    elif soc < soc_min:
        dss.text("Edit Storage.Bateria %Discharge=0 %IdlingkW=0 dispmode=external %stored=" + str(soc_min))

    else:
        dss.text("Edit Storage.Bateria %Charge=100 %Discharge=100 dispmode=follow daily=storageCurve")
        
    dss.circuit._set_active_element("Storage.Bateria")
    soc_2 = float(dss.dssproperties._value_read("23"))
    soc_lista_2.append(soc_2)

    # Aplicação do ataque do Lucão
    x = step  # os valores dos passos da simulação de acordo com o Lucão    
    ataque_DoS()

    soc_ataque_lista.append(float(soc_ataque)) # armazenar os dados do soc_ataque para ver se eles estão fixando onde quero

    # Contagem de ciclos
    if not carga_completa and soc >= contador_soc_max:
        carga_completa = True

    if carga_completa and not descarga_completa and soc <= contador_soc_min:
        descarga_completa = True

    if carga_completa and descarga_completa:
        contador_ciclos += 1
        print(f"[{stepNumber}] Ciclo completo #{contador_ciclos}")
        soh = 100 * np.exp(-taxa_degradacao_por_ciclo * contador_ciclos)
        print(f"O valor do SOH atual é: {soh}")
        soc_max, soc_min = aplicar_degradacao_soc(soc_max, soc_min, taxa_degradacao)
        print(f"↳ Novos limites: SOC máx = {soc_max:.1f}%, SOC min = {soc_min:.1f}%")
        carga_completa = False
        descarga_completa = False

def solve_settings():
    dss_file = r"C:\soh_bateria_opendss\123Bus\IEEE123Master.dss"
    dss.text("Clear")
    dss.text(f"Compile [{dss_file}]")

    # Salva o diretório atual e acrescenta uma pasta para resultados
    OpenDSS_folder_path = os.path.dirname(dss_file)
    results_path = os.path.join(OpenDSS_folder_path, "Teste")
    os.makedirs(results_path, exist_ok=True)

    dss.text("set maxcontroliter=2000")
    dss.text("set maxiterations=1000")
    dss.text("set mode=daily")
    dss.text("set controlmode = time")
    dss.text("set stepsize=1h")
    dss.text("Disable StorageController.*")
    print("Configurações aplicadas.")
    return dss_file, results_path

# ========================= SIMULAÇÃO =========================

dss_file, results_path = solve_settings()
original_steps = 168
dss.solution._number_write(original_steps)

for step in range(original_steps):

    control_iter = 1
    dss.solution._init_snap()

    while not dss.solution._control_actions_done_read():
        dss.solution._solve_no_control()

        if control_iter == 1:
            controle_soc_por_ciclo(step)
            dss.solution._solve_no_control()
            
        dss.solution._sample_control_devices()

        if dss.ctrlqueue._queue_size() == 0:
            break

        dss.solution._do_control_actions()

        control_iter += 1
        if control_iter >= dss.solution._max_control_iterations_read():
            print("Número máximo de iterações de controle excedido.")
            break

    dss.solution._finish_time_step()

print(f"\n Simulação finalizada. Total de ciclos completos: {contador_ciclos}")

# ============================= SALVANDO EM CSV ==============================

# saida_csv = os.path.join(results_path, "resultados_simulacao.csv")

# with open(saida_csv, mode='w', newline='') as arquivo_csv:
#     writer = csv.writer(arquivo_csv)
#     writer.writerow(["Step", "SOC", "SOC_2", "SOC_max", "SOC_min", "SOH", "kW_painel", "kW_carga", "kW_bateria"])
    
#     for i in range(len(passos)):
#         writer.writerow([
#             passos[i],
#             soc_lista[i],
#             soc_lista_2[i],
#             soc_max_lista[i],
#             soc_min_lista[i],
#             soh_lista[i],
#             kW_painel_lista[i],
#             kW_carga_lista[i],
#             kW_bateria_lista[i]
#         ])

# print(f" Resultados salvos em: {saida_csv}")

# ============================= PLOT ==============================

horas = np.linspace(0, original_steps, original_steps)

# Gráfico 1: SOC e limites
plt.figure(figsize=(12, 5))
plt.plot(horas, soc_lista_2, label="SOC (%)", linewidth=1)
plt.plot(horas, soc_max_lista, linestyle="--", label="SOC Máx")
plt.plot(horas, soc_min_lista, linestyle="--", label="SOC Mín")
plt.title("SOC com Controle e Degradação por Ciclos")
plt.xlabel("Tempo (horas)")
plt.ylabel("SOC (%)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Gráfico 2: SOH
plt.figure(figsize=(12, 5))
plt.plot(horas, soh_lista, linestyle="-.", color="purple", label="SOH (%)")
plt.title("SOH (State of Health) da Bateria")
plt.xlabel("Tempo (horas)")
plt.ylabel("SOH (%)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# # Gráfico 3: SOC Normal sem Limites
# plt.figure(figsize=(12, 5))
# plt.plot(horas, soc_lista, label="SOC (%)", linewidth=1)
# plt.title("SOC Normal da Bateria")
# plt.xlabel("Tempo (horas)")
# plt.ylabel("SOC Normal (%)")
# plt.grid(True)
# plt.legend()
# plt.tight_layout()
# plt.show()

# Gráfico 3: SOC Ataque com Limites
plt.figure(figsize=(12, 5))
plt.plot(horas, soc_ataque_lista, label="SOC (%)", linewidth=1)
plt.title("SOC com Ataques na Bateria")
plt.xlabel("Tempo (horas)")
plt.ylabel("SOC Ataque (%)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()