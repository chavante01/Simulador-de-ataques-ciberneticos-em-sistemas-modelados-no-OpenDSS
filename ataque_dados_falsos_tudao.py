import os
from os.path import abspath, dirname
import csv
import py_dss_interface
import numpy as np
import matplotlib.pyplot as plt
import random
import math

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
kWh_lista = []
kW_lista = []
tensao_lista = []
correntes_lista = []
kVA_lista = []
soc_ataque_lista = []
kWh_ataque_lista = []
kW_ataque_lista = []
tensao_ataque_lista = []
corrente_ataque_lista = []
kVA_ataque_lista = []
soc_max_lista = []
soc_min_lista = []
passos = []
taxa_degradacao_por_ciclo = 0.009
soh = 100.0  
iteracoes = []
soh_lista = []
# kW_painel_lista = []
# kW_carga_lista = []
# kW_bateria_lista = []

# Variáveis globais
estado_anterior = 0  # Começa como 0 para detectar o primeiro 1
y_tau_y = None       # Valor do sensor antes do ataque
dados_salvos_antes_do_ataque = False

def false_data(): 
    global soc_ataque, kWh_bateria, kW_bateria, kVA_bateria, tensao_bateria, corrente_bateria # variáveis dos sensores

    # Conjunto de sensores da bateria 
    dss.circuit._set_active_element("Storage.Bateria")
    soc_ataque = float(dss.dssproperties._value_read("23"))
    kWh_bateria = float(dss.dssproperties._value_read("22"))
    kW_bateria = dss.cktelement._powers()
    kVA_bateria = math.sqrt((kW_bateria[0]**2) + (kW_bateria[1]**2))
    tensao_bateria = dss.cktelement._voltages()
    corrente_bateria = dss.cktelement._currents()

    yk = np.array([  # "matriz 6x1" sinal que deveria chegar ao controlador e detector de anomalias
            [soc_ataque],
            [kWh_bateria],
            [kW_bateria[0]],
            [tensao_bateria[0]],
            [corrente_bateria[0]],
            [kVA_bateria]
    ])

    Gamma_y = np.array([     #matriz binária que indica se o adversário possui ou não acesso aos sensores
        [1, 0, 0, 0, 0],
        [0, 1, 0, 0, 0],      
        [0, 0, 1, 0, 0],   #6x5
        [0, 0, 0, 1, 0],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0]
    ])

    # bky = np.array([   # é essa matriz que vai adicionar corrupção ao sinal, ela soma um valor aleatório entre o range declarado e soma ao sinal original
    #     [random.uniform(maximo_soc, minimo_soc)],   # declare valores adequados para cada tipo de medição!!!
    #     [random.uniform(maximo_kWh, minimo_kWh)],
    #     [random.uniform(maximo_kW, minimo_kW)],
    #     [random.uniform(maximo_tensao, minimo_tensao)],
    #     [random.uniform(maximo_corrente, minimo_corrente)],
    # ])

    bky = np.array([   # é essa matriz que vai adicionar corrupção ao sinal, ela soma um valor aleatório entre o range declarado e soma ao sinal original
    [random.uniform(100, 0)],   # declare valores adequados para cada tipo de medição!!!
    [random.uniform(2000, 0)],
    [random.uniform(200, -200)],
    [random.uniform(4600, 0)],
    [random.uniform(5000, -5000)],
    ])

    y_til_k = yk + (np.dot(Gamma_y, bky))
    resultado_ataque = y_til_k  

    soc_ataque_lista.append(float(resultado_ataque[0])) 
    kWh_ataque_lista.append(float(resultado_ataque[1]))
    kW_ataque_lista.append(float(resultado_ataque[2]))
    tensao_ataque_lista.append(float(resultado_ataque[3]))
    corrente_ataque_lista.append(float(resultado_ataque[4]))
    kVA_ataque_lista.append(float(resultado_ataque[5]))

    return resultado_ataque

def aplicar_degradacao_soc(soc_max_atual, soc_min_atual, taxa_degradacao, limite_superior=60, limite_inferior=40):
    novo_soc_max = max(soc_max_atual - taxa_degradacao, limite_superior)
    novo_soc_min = min(soc_min_atual + taxa_degradacao, limite_inferior)
    return novo_soc_max, novo_soc_min

def controle_soc_por_ciclo(stepNumber):
    global soc_max, soc_min, contador_ciclos, carga_completa, descarga_completa, soh, x, kWh_bateria, kW_bateria, kVA_bateria, tensao_bateria, corrente_bateria
    # global kW_painel_lista, kW_bateria_lista, kW_carga_lista  

    dss.circuit._set_active_element("Storage.Bateria")
    soc = float(dss.dssproperties._value_read("23"))
    kWh = float(dss.dssproperties._value_read("22"))
    kW = dss.cktelement._powers()
    kVA = math.sqrt((kW[0]**2) + (kW[1]**2))
    tensao = dss.cktelement._voltages()
    corrente = dss.cktelement._currents()
    
    # kW_bateria = float(dss.dssproperties._value_read("5"))

    # dss.circuit._set_active_element("Load.634a")
    # kW_carga = dss.cktelement._powers()[0]

    # dss.circuit._set_active_element("PVSystem.PV")
    # kW_painel = dss.cktelement._powers()[0] * (-1)

    # Salva para os gráficos
    soc_lista.append(soc)
    soc_max_lista.append(soc_max)
    soc_min_lista.append(soc_min)
    passos.append(stepNumber)
    soh_lista.append(soh)  
    kWh_lista.append(kWh)
    kW_lista.append(kW)
    tensao_lista.append(tensao[0])
    correntes_lista.append(corrente[0])
    kVA_lista.append(kVA) 
    # kW_carga_lista.append(kW_carga)
    # kW_painel_lista.append(kW_painel)
    # kW_bateria_lista.append(kW_bateria)

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
    false_data()

    #soc_ataque_lista.append(float(soc_ataque)) # armazenar os dados do soc_ataque para ver se eles estão fixando onde quero

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

# Gráfico 2: SOC Ataque com Limites
plt.figure(figsize=(12, 5))
plt.plot(horas, soc_ataque_lista, label="SOC (%)", linewidth=1)
plt.title("SOC com Ataques na Bateria")
plt.xlabel("Tempo (horas)")
plt.ylabel("SOC Ataque (%)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Gráfico 3: SOH
plt.figure(figsize=(12, 5))
plt.plot(horas, soh_lista, linestyle="-.", color="purple", label="SOH (%)")
plt.title("SOH (State of Health) da Bateria")
plt.xlabel("Tempo (horas)")
plt.ylabel("SOH (%)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Gráfico 4: SOC Normal sem Limites
plt.figure(figsize=(12, 5))
plt.plot(horas, soc_lista, label="SOC (%)", linewidth=1)
plt.title("SOC Normal da Bateria")
plt.xlabel("Tempo (horas)")
plt.ylabel("SOC Normal (%)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Gráfico 5: Energia sem Ataque 
plt.figure(figsize=(12, 5))
plt.plot(horas, kWh_lista, label="kWh ", linewidth=1)
plt.title("Energia sem Ataques na Bateria")
plt.xlabel("Tempo (horas)")
plt.ylabel("kWh ")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Gráfico 6: Energia com Ataque 
plt.figure(figsize=(12, 5))
plt.plot(horas, kWh_ataque_lista, label="kWh ", linewidth=1)
plt.title("Energia com Ataques na Bateria")
plt.xlabel("Tempo (horas)")
plt.ylabel("kWh Ataque ")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Gráfico 7: Potência Ativa sem Ataque 
plt.figure(figsize=(12, 5))
plt.plot(horas, kW_lista, label="kW ", linewidth=1)
plt.title("Potência Ativa sem Ataques na Bateria")
plt.xlabel("Tempo (horas)")
plt.ylabel("kW ")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Gráfico 8: Potência Ativa com Ataque 
plt.figure(figsize=(12, 5))
plt.plot(horas, kW_ataque_lista, label="kW ", linewidth=1)
plt.title("Potência Ativa com Ataques na Bateria")
plt.xlabel("Tempo (horas)")
plt.ylabel("kW Ataque ")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Gráfico 9: Tensão Fase R sem Ataque 
plt.figure(figsize=(12, 5))
plt.plot(horas, tensao_lista, label="V ", linewidth=1)
plt.title("Tensão sem Ataques na Bateria")
plt.xlabel("Tempo (horas)")
plt.ylabel("V ")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Gráfico 10: Tensão Fase R com Ataque 
plt.figure(figsize=(12, 5))
plt.plot(horas, tensao_ataque_lista, label="V ", linewidth=1)
plt.title("Tensão com Ataques na Bateria")
plt.xlabel("Tempo (horas)")
plt.ylabel("V Ataque ")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Gráfico 11: Corrente Fase R sem Ataque 
plt.figure(figsize=(12, 5))
plt.plot(horas, correntes_lista, label="I ", linewidth=1)
plt.title("Corrente sem Ataques na Bateria")
plt.xlabel("Tempo (horas)")
plt.ylabel("I ")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Gráfico 12: Corrente Fase R com Ataque 
plt.figure(figsize=(12, 5))
plt.plot(horas, corrente_ataque_lista, label="I ", linewidth=1)
plt.title("Corrente com Ataques na Bateria")
plt.xlabel("Tempo (horas)")
plt.ylabel("I Ataque ")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Gráfico 13: Potência Aparente sem Ataque 
plt.figure(figsize=(12, 5))
plt.plot(horas, kVA_lista, label="kVA", linewidth=1)
plt.title("Potência Aparente sem Ataques na Bateria")
plt.xlabel("Tempo (horas)")
plt.ylabel("kVA ")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Gráfico 14: Potência Aparente com Ataque 
plt.figure(figsize=(12, 5))
plt.plot(horas, kVA_ataque_lista, label="kVA", linewidth=1)
plt.title("Potência Aparente com Ataques na Bateria")
plt.xlabel("Tempo (horas)")
plt.ylabel("kVA Ataque ")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()