import os
from os.path import abspath, dirname
import csv
import py_dss_interface
import numpy as np
import matplotlib.pyplot as plt
import random
import math

def selecionar_alvos():
    # Dicionário de sensores
    sensores = {
        0: "SOC da Bateria",
        1: "Energia da Bateria (kWh)",
        2: "Potência Ativa da Bateria (kW)",
        3: "Tensão da Bateria (V)",
        4: "Corrente da Bateria (A)",
        5: "Potência Aparente da Bateria (kVA)"
    }

    # Dicionário de atuadores
    atuadores = {
        0: "SOC Máximo da Bateria",
        1: "SOC Mínimo da Bateria",
        2: "kW_ref da Bateria",
        3: "Idling_kW da Bateria"
    }

    # ---- Sensores ----
    print("\nSensores disponíveis para ataque:")

    for idx, nome in sensores.items():
        print(f"[{idx}]: {nome}")
    entrada_sensores = input("\nDigite os índices dos sensores para ataque (ex: 0,2,4): ")
    selecionados_sensores = list(map(int, entrada_sensores.strip().split(",")))

    Gamma_y = np.zeros((6, 6))  # Matriz 6x5
    for idx in selecionados_sensores:
        if 0 <= idx <= 5:
            Gamma_y[idx, idx] = 1
        else:
            print(f" Índice de sensor inválido ignorado: {idx}")

    # ---- Atuadores ----
    print("\nAtuadores disponíveis para ataque:")
    for idx, nome in atuadores.items():
        print(f"[{idx}]: {nome}")
    entrada_atuadores = input("\nDigite os índices dos atuadores para ataque (ex: 0,2): ")
    selecionados_atuadores = list(map(int, entrada_atuadores.strip().split(",")))

    Gamma_u = np.zeros((4, 4))  
    for idx in selecionados_atuadores:
        if 0 <= idx <= 3:
            Gamma_u[idx, idx] = 1
        else:
            print(f" Índice de atuador inválido ignorado: {idx}")

    return Gamma_y, Gamma_u

print("\n=== SIMULADOR DE ATAQUES CIBERFÍSICOS NA BATERIA ===")
print("Escolha o(s) ataque(s) a simular:")
print("[1] DoS (Negação de Serviço)")
print("[2] Replay (Repetição de Dados)")
print("[3] False Data Injection (Injeção de Dados Falsos)")
print("[4] Injeção de Dados Falsos Customizável")
print("[5] Todos os ataques")
print("[0] Sem ataques\n")

modo = input("Digite a opção desejada: ")

Gamma_y, Gamma_u = selecionar_alvos()

enable_dos = False
enable_replay = False
enable_false_data = False
enable_false_data_customizable = False
prob_bernoulli = 0
k0 = 0
kr = 0
kf = 0
bky = np.zeros((6, 1))
bku = np.zeros((4, 1))

if modo == "1":
    enable_dos = True
    print(" Ataque de Negação de Serviço ativado.")
elif modo == "2":
    enable_replay = True
    print(" Ataque de Replay ativado.")
elif modo == "3":
    enable_false_data = True
    print(" Ataque de Injeção de Dados Falsos ativado.")
elif modo == "4":
    enable_false_data_customizable = True
    print(" Ataque de Injeção de Dados Falsos Customizável ativado.")
elif modo == "5":
    enable_dos = True
    enable_replay = True
    enable_false_data = True
    enable_false_data_customizable = True
    print(" Todos os ataques ativados.")
elif modo == "0":
    print(" Nenhum ataque será simulado.")  
else:
    print(" Opção inválida. Nenhum ataque ativado por padrão.")

if modo == "1" or modo == "5":
    print("\nInsira o valor da Probabilidade de Bernoulli")
    prob_bernoulli = float(input("Digite o valor desejado: "))
elif modo == "2" or modo == "5":
    print("\nInsira os valores dos Locais de Ocorrência do Ataque de Replay: ")
    k0 = float(input("Digite o valor desejado de k0: "))
    kr = float(input("Digite o valor desejado de kr: "))
    kf = float(input("Digite o valor desejado de kf: "))
elif modo == "3" or modo == "5":
    print("\nInsira os valores dos Locais de Ocorrência do Ataque de Injeção de Dados Falsos: ")
    print("\n--- bku (atuadores) ---")

    if np.any(Gamma_u[0, :]):
        print("\nCorrupção para SOC Máximo da Bateria:")
        a = float(input("  -> Limite inferior: "))
        b = float(input("  -> Limite superior: "))
        bku[0, 0] = random.uniform(a, b)

    if np.any(Gamma_u[1, :]):
        print("\nCorrupção para SOC Mínimo da Bateria:")
        a = float(input("  -> Limite inferior: "))
        b = float(input("  -> Limite superior: "))
        bku[1, 0] = random.uniform(a, b)

    if np.any(Gamma_u[2, :]):
        print("\nCorrupção para kW_ref da Bateria:")
        a = float(input("  -> Limite inferior: "))
        b = float(input("  -> Limite superior: "))
        bku[2, 0] = random.uniform(a, b)

    if np.any(Gamma_u[3, :]):
        print("\nCorrupção para Idling_kW da Bateria:")
        a = float(input("  -> Limite inferior: "))
        b = float(input("  -> Limite superior: "))
        bku[3, 0] = random.uniform(a, b)

    print("\n--- bky (sensores) ---")

    if np.any(Gamma_y[0, :]):
        print("\nCorrupção para SOC da Bateria:")
        a = float(input("  -> Limite inferior: "))
        b = float(input("  -> Limite superior: "))
        bky[0, 0] = random.uniform(a, b)

    if np.any(Gamma_y[1, :]):
        print("\nCorrupção para Energia da Bateria (kWh):")
        a = float(input("  -> Limite inferior: "))
        b = float(input("  -> Limite superior: "))
        bky[1, 0] = random.uniform(a, b)

    if np.any(Gamma_y[2, :]):
        print("\nCorrupção para Potência Ativa da Bateria (kW):")
        a = float(input("  -> Limite inferior: "))
        b = float(input("  -> Limite superior: "))
        bky[2, 0] = random.uniform(a, b)

    if np.any(Gamma_y[3, :]):
        print("\nCorrupção para Tensão da Bateria (V):")
        a = float(input("  -> Limite inferior: "))
        b = float(input("  -> Limite superior: "))
        bky[3, 0] = random.uniform(a, b)

    if np.any(Gamma_y[4, :]):
        print("\nCorrupção para Corrente da Bateria (A):")
        a = float(input("  -> Limite inferior: "))
        b = float(input("  -> Limite superior: "))
        bky[4, 0] = random.uniform(a, b)

    if np.any(Gamma_y[5, :]):
        print("\nCorrupção para Potência Aparente da Bateria (kVA):")
        a = float(input("  -> Limite inferior: "))
        b = float(input("  -> Limite superior: "))
        bky[5, 0] = random.uniform(a, b)


def plotar_resultados_ataques(horas):
    """
    Plota automaticamente gráficos apenas para os sensores e atuadores realmente atacados,
    de acordo com Gamma_y e Gamma_u.
    """
    step_size = 1  # passos de 1 hora

    # === FLAGS DE SENSOR E ATUADOR ===
    sensor_soc = np.any(Gamma_y[:, 0])
    sensor_kwh = np.any(Gamma_y[:, 1])
    sensor_kw = np.any(Gamma_y[:, 2])
    sensor_v = np.any(Gamma_y[:, 3])
    sensor_i = np.any(Gamma_y[:, 4])
    sensor_kva = np.any(Gamma_y[:, 5])


    atuador_soc_max = np.any(Gamma_u[0, :])
    atuador_soc_min = np.any(Gamma_u[1, :])
    atuador_kw_ref = np.any(Gamma_u[2, :])
    atuador_idling_kw = np.any(Gamma_u[3, :])

    # SOC
    if enable_dos and sensor_soc:
        plt.figure()
        plt.plot(horas, soc_dos_lista_sensores, label="SOC Sensor DoS")
        plot_attack_regions(time_attack_dos, step_size)
        plt.title("SOC - Ataque DoS"); plt.xlabel("Tempo (h)"); plt.ylabel("SOC (%)"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_false_data and sensor_soc:
        plt.figure()
        plt.plot(horas, soc_false_injection_lista_sensores, label="SOC Sensor False Data")
        plot_attack_regions(time_attack_false_data, step_size)
        plt.title("SOC - Ataque False Data"); plt.xlabel("Tempo (h)"); plt.ylabel("SOC (%)"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_replay and sensor_soc:
        plt.figure()
        plt.plot(horas, soc_replay_lista_sensores, label="SOC Sensor Replay")
        plot_attack_regions(time_attack_replay, step_size)
        plt.title("SOC - Ataque Replay"); plt.xlabel("Tempo (h)"); plt.ylabel("SOC (%)"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_false_data_customizable and sensor_soc:
        plt.figure()
        plt.plot(horas, soc_replay_lista_sensores, label="SOC Sensor False Data Customizable")
        plot_attack_regions(time_attack_false_data_customizable, step_size)
        plt.title("SOC - Ataque False Data Customizable"); plt.xlabel("Tempo (h)"); plt.ylabel("SOC (%)"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    # Energia
    if enable_dos and sensor_kwh:
        plt.figure()
        plt.plot(horas, kWh_dos_lista_sensores, label="kWh Sensor DoS")
        plot_attack_regions(time_attack_dos, step_size)
        plt.title("Energia (kWh) - Ataque DoS"); plt.xlabel("Tempo (h)"); plt.ylabel("kWh"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_false_data and sensor_kwh:
        plt.figure()
        plt.plot(horas, kWh_false_injection_lista_sensores, label="kWh Sensor False Data")
        plot_attack_regions(time_attack_false_data, step_size)
        plt.title("Energia (kWh) - Ataque False Data"); plt.xlabel("Tempo (h)"); plt.ylabel("kWh"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_replay and sensor_kwh:
        plt.figure()
        plt.plot(horas, kWh_replay_lista_sensores, label="kWh Sensor Replay")
        plot_attack_regions(time_attack_replay, step_size)
        plt.title("Energia (kWh) - Ataque Replay"); plt.xlabel("Tempo (h)"); plt.ylabel("kWh"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_false_data_customizable and sensor_kwh:
        plt.figure()
        plt.plot(horas, kWh_false_injection_customizavel_lista_sensores, label="kWh Sensor False Data Customizable")
        plot_attack_regions(time_attack_false_data_customizable, step_size)
        plt.title("Energia (kWh) - False Data Customizable"); plt.xlabel("Tempo (h)"); plt.ylabel("kWh"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    # Potência ativa (kW)
    if enable_dos and sensor_kw:
        plt.figure()
        plt.plot(horas, kW_dos_lista_sensores, label="kW Sensor DoS")
        plot_attack_regions(time_attack_dos, step_size)
        plt.title("Potência Ativa (kW) - Ataque DoS"); plt.xlabel("Tempo (h)"); plt.ylabel("kW"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_false_data and sensor_kw:
        plt.figure()
        plt.plot(horas, kW_false_injection_lista_sensores, label="kW Sensor False Data")
        plot_attack_regions(time_attack_false_data, step_size)
        plt.title("Potência Ativa (kW) - Ataque False Data"); plt.xlabel("Tempo (h)"); plt.ylabel("kW"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_replay and sensor_kw:
        plt.figure()
        plt.plot(horas, kW_replay_lista_sensores, label="kW Sensor Replay")
        plot_attack_regions(time_attack_replay, step_size)
        plt.title("Potência Ativa (kW) - Ataque Replay"); plt.xlabel("Tempo (h)"); plt.ylabel("kW"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_false_data_customizable and sensor_kw:
        plt.figure()
        plt.plot(horas, kW_false_injection_customizavel_lista_sensores, label="kW Sensor False Data Customizable")
        plot_attack_regions(time_attack_false_data_customizable, step_size)
        plt.title("Potência Ativa (kW) - Ataque False Data Customizable"); plt.xlabel("Tempo (h)"); plt.ylabel("kW"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()
    
    # Tensão
    if enable_dos and sensor_v:
        plt.figure()
        plt.plot(horas, tensao_dos_lista_sensores, label="Tensão Sensor DoS")
        plot_attack_regions(time_attack_dos, step_size)
        plt.title("Tensão - Ataque DoS"); plt.xlabel("Tempo (h)"); plt.ylabel("V"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_false_data and sensor_v:
        plt.figure()
        plt.plot(horas, tensao_false_injection_lista_sensores, label="Tensão Sensor False Data")
        plot_attack_regions(time_attack_false_data, step_size)
        plt.title("Tensão - Ataque False Data"); plt.xlabel("Tempo (h)"); plt.ylabel("V"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_replay and sensor_v:
        plt.figure()
        plt.plot(horas, tensao_replay_lista_sensores, label="Tensão Sensor Replay")
        plot_attack_regions(time_attack_replay, step_size)
        plt.title("Tensão - Ataque Replay"); plt.xlabel("Tempo (h)"); plt.ylabel("V"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_false_data_customizable and sensor_v:
        plt.figure()
        plt.plot(horas, tensao_replay_lista_sensores, label="Tensão Sensor False Data Customizable")
        plot_attack_regions(time_attack_false_data_customizable, step_size)
        plt.title("Tensão - Ataque False Data Customizable"); plt.xlabel("Tempo (h)"); plt.ylabel("V"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    # Corrente
    if enable_dos and sensor_i:
        plt.figure()
        plt.plot(horas, corrente_dos_lista_sensores, label="Corrente Sensor DoS")
        plot_attack_regions(time_attack_dos, step_size)
        plt.title("Corrente - Ataque DoS"); plt.xlabel("Tempo (h)"); plt.ylabel("A"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_false_data and sensor_i:
        plt.figure()
        plt.plot(horas, corrente_false_injection_lista_sensores, label="Corrente Sensor False Data")
        plot_attack_regions(time_attack_false_data, step_size)
        plt.title("Corrente - Ataque False Data"); plt.xlabel("Tempo (h)"); plt.ylabel("A"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_replay and sensor_i:
        plt.figure()
        plt.plot(horas, corrente_replay_lista_sensores, label="Corrente Sensor Replay")
        plot_attack_regions(time_attack_replay, step_size)
        plt.title("Corrente - Ataque Replay"); plt.xlabel("Tempo (h)"); plt.ylabel("A"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_false_data_customizable and sensor_i:
        plt.figure()
        plt.plot(horas, corrente_false_injection_customizavel_lista_sensores, label="Corrente Sensor False Data Customizable")
        plot_attack_regions(time_attack_false_data_customizable, step_size)
        plt.title("Corrente - Ataque False Data Customizable"); plt.xlabel("Tempo (h)"); plt.ylabel("A"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()    

    # kVA
    if enable_dos and sensor_kva:
        plt.figure()
        plt.plot(horas, kVA_dos_lista_sensores, label="kVA Sensor DoS")
        plot_attack_regions(time_attack_dos, step_size)
        plt.title("Potência Aparente (kVA) - Ataque DoS"); plt.xlabel("Tempo (h)"); plt.ylabel("kVA"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_false_data and sensor_kva:
        plt.figure()
        plt.plot(horas, kVA_false_injection_lista_sensores, label="kVA Sensor False Data")
        plot_attack_regions(time_attack_false_data, step_size)
        plt.title("Potência Aparente (kVA) - Ataque False Data"); plt.xlabel("Tempo (h)"); plt.ylabel("kVA"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_replay and sensor_kva:
        plt.figure()
        plt.plot(horas, kVA_replay_lista_sensores, label="kVA Sensor Replay")
        plot_attack_regions(time_attack_replay, step_size)
        plt.title("Potência Aparente (kVA) - Ataque Replay"); plt.xlabel("Tempo (h)"); plt.ylabel("kVA"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_false_data_customizable and sensor_kva:
        plt.figure()
        plt.plot(horas, kVA_false_injection_customizavel_lista_sensores, label="kVA Sensor False Data Customizable")
        plot_attack_regions(time_attack_false_data_customizable, step_size)
        plt.title("Potência Aparente (kVA) - Ataque False Data Customizable"); plt.xlabel("Tempo (h)"); plt.ylabel("kVA"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    # Soc_Máx

    if enable_dos and atuador_soc_max:
        plt.figure()
        plt.plot(horas, soc_max_dos_atuadores, label="SOC Máx Atuador DoS")
        plot_attack_regions(time_attack_dos, step_size)
        plt.title("SOC Máximo - Ataque DoS"); plt.xlabel("Tempo (h)"); plt.ylabel("SOC_MÁX (%)"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_false_data and atuador_soc_max:
        plt.figure()
        plt.plot(horas, soc_max_false_injection_lista_atuadores, label="SOC Máx Atuador False Data")
        plot_attack_regions(time_attack_false_data, step_size)
        plt.title("SOC Máximo - Ataque False Data"); plt.xlabel("Tempo (h)"); plt.ylabel("SOC_MÁX (%)"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_replay and atuador_soc_max:
        plt.figure()
        plt.plot(horas, soc_max_replay_atuadores, label="SOC Máx Atuador Replay")
        plot_attack_regions(time_attack_replay, step_size)
        plt.title("SOC Máximo - Ataque Replay"); plt.xlabel("Tempo (h)"); plt.ylabel("SOC_MÁX (%)"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_false_data_customizable and atuador_soc_max:
        plt.figure()
        plt.plot(horas, soc_max_replay_atuadores, label="SOC Máx Atuador False Data Customizable")
        plot_attack_regions(time_attack_false_data_customizable, step_size)
        plt.title("SOC Máximo - Ataque False Data Customizable"); plt.xlabel("Tempo (h)"); plt.ylabel("SOC_MÁX (%)"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    # Soc_Mín

    if enable_dos and atuador_soc_min:
        plt.figure()
        plt.plot(horas, soc_min_dos_atuadores, label="SOC Mín Atuador DoS")
        plot_attack_regions(time_attack_dos, step_size)
        plt.title("SOC Mínimo - Ataque DoS"); plt.xlabel("Tempo (h)"); plt.ylabel("SOC_MÍN (%)"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_false_data and atuador_soc_min:
        plt.figure()
        plt.plot(horas, soc_min_false_injection_lista_atuadores, label="SOC Mín Atuador False Data")
        plot_attack_regions(time_attack_false_data, step_size)
        plt.title("SOC Mínimo - Ataque False Data"); plt.xlabel("Tempo (h)"); plt.ylabel("SOC_MÍN (%)"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_replay and atuador_soc_min:
        plt.figure()
        plt.plot(horas, soc_min_replay_atuadores, label="SOC Mín Atuador Replay")
        plot_attack_regions(time_attack_replay, step_size)
        plt.title("SOC Mínimo - Ataque Replay"); plt.xlabel("Tempo (h)"); plt.ylabel("SOC_MÍN (%)"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_false_data_customizable and atuador_soc_min:
        plt.figure()
        plt.plot(horas, soc_min_false_injection_customizavel_lista_atuadores, label="SOC Mín Atuador False Data Customizable")
        plot_attack_regions(time_attack_false_data_customizable, step_size)
        plt.title("SOC Mínimo - Ataque False Data Customizable"); plt.xlabel("Tempo (h)"); plt.ylabel("SOC_MÍN (%)"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    # kW_ref

    if enable_dos and atuador_kw_ref:
        plt.figure()
        plt.plot(horas, kW_ref_dos_atuadores, label="kW_ref Atuador DoS")
        plot_attack_regions(time_attack_dos, step_size)
        plt.title("kW_ref - Ataque DoS"); plt.xlabel("Tempo (h)"); plt.ylabel("kW_ref"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_false_data and atuador_kw_ref:
        plt.figure()
        plt.plot(horas, kW_ref_false_injection_lista_atuadores, label="kW_ref Atuador False Data")
        plot_attack_regions(time_attack_false_data, step_size)
        plt.title("kW_ref - Ataque False Data"); plt.xlabel("Tempo (h)"); plt.ylabel("kW_ref"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_replay and atuador_kw_ref:
        plt.figure()
        plt.plot(horas, kW_ref_replay_atuadores, label="kW_ref Atuador Replay")
        plot_attack_regions(time_attack_replay, step_size)
        plt.title("kW_ref - Ataque Replay"); plt.xlabel("Tempo (h)"); plt.ylabel("kW_ref"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_false_data_customizable and atuador_kw_ref:
        plt.figure()
        plt.plot(horas, kW_ref_false_injection_lista_customizavel_atuadores, label="kW_ref Atuador False Data Customizable")
        plot_attack_regions(time_attack_false_data_customizable, step_size)
        plt.title("kW_ref - Ataque False Data Customizable"); plt.xlabel("Tempo (h)"); plt.ylabel("kW_ref"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    # Idling_kW

    if enable_dos and atuador_idling_kw:
        plt.figure()
        plt.plot(horas, idling_kW_dos_atuadores, label="Idling_kW Atuador DoS")
        plot_attack_regions(time_attack_dos, step_size)
        plt.title("Idling_kW - Ataque DoS"); plt.xlabel("Tempo (h)"); plt.ylabel("Idling_kW"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_false_data and atuador_idling_kw:
        plt.figure()
        plt.plot(horas, idling_kW_false_injection_lista_atuadores, label="Idling_kW Atuador False Data")
        plot_attack_regions(time_attack_false_data, step_size)
        plt.title("Idling_kW - Ataque False Data"); plt.xlabel("Tempo (h)"); plt.ylabel("Idling_kW"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_replay and atuador_idling_kw:
        plt.figure()
        plt.plot(horas, idling_kW_replay_atuadores, label="Idling_kW Atuador Replay")
        plot_attack_regions(time_attack_replay, step_size)
        plt.title("Idling_kW - Ataque Replay"); plt.xlabel("Tempo (h)"); plt.ylabel("Idling_kW"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()

    if enable_false_data_customizable and atuador_idling_kw:
        plt.figure()
        plt.plot(horas, idling_kW_false_injection_customizavel_lista_atuadores, label="Idling_kW Atuador False Data Customizable")
        plot_attack_regions(time_attack_false_data_customizable, step_size)
        plt.title("Idling_kW - Ataque False Data Customizable"); plt.xlabel("Tempo (h)"); plt.ylabel("Idling_kW"); plt.legend(); plt.grid(); plt.tight_layout(); plt.show()


# Instância do OpenDSS
dss = py_dss_interface.DSS()

# ========================= CONTROLE SOC COM DEGRADAÇÃO =========================
# Variáveis globais do ataque replay
i_y = 0
i_u = 0
lk_lista_y = []
lk_lista_u = []
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

# Listas para os valores de Ataque de Negação de Serviço
kW_ref_dos_atuadores = []
soc_dos_lista_sensores = []
idling_kW_dos_atuadores = []
kWh_dos_lista_sensores = []
kW_dos_lista_sensores = []
tensao_dos_lista_sensores = []
corrente_dos_lista_sensores = []
kVA_dos_lista_sensores = []
soc_max_dos_atuadores = []
soc_min_dos_atuadores = []

# Listas para os valores de Ataque de Replay
kW_ref_replay_atuadores = []
soc_replay_lista_sensores = []
idling_kW_replay_atuadores = []
kWh_replay_lista_sensores = []
kW_replay_lista_sensores = []
tensao_replay_lista_sensores = []
corrente_replay_lista_sensores = []
kVA_replay_lista_sensores = []
soc_max_replay_atuadores = []
soc_min_replay_atuadores = []

# Listas para os valores de Ataque de Injeção de Dados Falsos
soc_false_injection_lista_sensores = []
kWh_false_injection_lista_sensores = []
kW_false_injection_lista_sensores = []
tensao_false_injection_lista_sensores = []
corrente_false_injection_lista_sensores = []
kVA_false_injection_lista_sensores = []
soc_max_false_injection_lista_atuadores = []
soc_min_false_injection_lista_atuadores = []
kW_ref_false_injection_lista_atuadores = []
idling_kW_false_injection_lista_atuadores = []

# Listas para os valores de Ataque de Injeção de Dados Falsos
soc_false_injection_customizavel_lista_sensores = []
kWh_false_injection_customizavel_lista_sensores = []
kW_false_injection_customizavel_lista_sensores = []
tensao_false_injection_customizavel_lista_sensores = []
corrente_false_injection_customizavel_lista_sensores = []
kVA_false_injection_customizavel_lista_sensores = []
soc_max_false_injection_customizavel_lista_atuadores = []
soc_min_false_injection_customizavel_lista_atuadores = []
kW_ref_false_injection_lista_customizavel_atuadores = []
idling_kW_false_injection_customizavel_lista_atuadores = []

# Listas a mais
soc_max_lista = []
soc_min_lista = []
passos = []
taxa_degradacao_por_ciclo = 0.009
soh = 100.0  
iteracoes = []
soh_lista = []
intervalos_dos = []
time_attack_dos = []
intervalos_replay = []
time_attack_replay = []
intervalos_false_data = []
time_attack_false_data = []
intervalos_false_data_customizable = []
time_attack_false_data_customizable = []

def aplicar_controle_bateria(soc, soc_max, soc_min):
    """
    Ajusta os parâmetros de operação da bateria no OpenDSS com base nos limites de SOC.
    Atualiza o modo de carga/descarga e retorna o novo valor de SOC lido do sistema.
    """
    if soc > soc_max:
        dss.text(f"Edit Storage.Bateria %Charge=0 dispmode=external %stored={soc_max}")
    elif soc < soc_min:
        dss.text(f"Edit Storage.Bateria %Discharge=0 %IdlingkW=0 dispmode=external %stored={soc_min}")
    else:
        dss.text("Edit Storage.Bateria %Charge=100 %Discharge=100 dispmode=follow daily=storageCurve")

    dss.circuit._set_active_element("Storage.Bateria")
    soc_2 = float(dss.dssproperties._value_read("23"))
    soc_lista_2.append(soc_2)
    return soc_2

def atualizar_contagem_ciclos(soc, soc_max, soc_min, contador_ciclos, carga_completa, descarga_completa, soh,
                              contador_soc_max, contador_soc_min, taxa_degradacao, taxa_degradacao_por_ciclo):
    """
    Atualiza o estado de contagem de ciclos com base no SOC atual. Se um ciclo completo for detectado,
    incrementa o contador de ciclos, aplica degradação nos limites de SOC e atualiza o SOH.
    
    Retorna os novos valores: contador_ciclos, carga_completa, descarga_completa, soc_max, soc_min, soh
    """
    if not carga_completa and soc >= contador_soc_max:
        carga_completa = True

    if carga_completa and not descarga_completa and soc <= contador_soc_min:
        descarga_completa = True

    if carga_completa and descarga_completa:
        contador_ciclos += 1
        soh = 100 * np.exp(-taxa_degradacao_por_ciclo * contador_ciclos)
        soc_max, soc_min = aplicar_degradacao_soc(soc_max, soc_min, taxa_degradacao)
        carga_completa = False
        descarga_completa = False

    return contador_ciclos, carga_completa, descarga_completa, soc_max, soc_min, soh

# Variáveis globais
estado_anterior = 0  # Começa como 0 para detectar o primeiro 1
y_tau_y = 0       # Valor do sensor antes do ataque
u_tau_u = 0       # Valor do atuador antes do ataque
dados_salvos_antes_do_ataque = False

def false_data(): 
    global soc_ataque, kWh_bateria, kW_bateria, kVA_bateria, tensao_bateria, corrente_bateria # variáveis dos sensores
    global soc_min, soc_max, kW_ref, Idling_kW
    # Conjunto de sensores da bateria 
    dss.circuit._set_active_element("Storage.Bateria")
    soc_ataque = float(dss.dssproperties._value_read("23"))
    kWh_bateria = float(dss.dssproperties._value_read("22"))
    kW_bateria = dss.cktelement._powers()
    kVA_bateria = math.sqrt((kW_bateria[0]**2) + (kW_bateria[1]**2))
    tensao_bateria = dss.cktelement._voltages()
    corrente_bateria = dss.cktelement._currents()
    #conjunto de atuadores
    kW_ref = float(dss.dssproperties._value_read("5"))
    Idling_kW = float(dss.dssproperties._value_read("30"))
    uk = np.array([
        [soc_max],
        [soc_min],
        [kW_ref], 
        [Idling_kW]  
    ])

    yk = np.array([  # "matriz 6x1" sinal que deveria chegar ao controlador e detector de anomalias
            [soc_ataque],
            [kWh_bateria],
            [kW_bateria[0]],
            [tensao_bateria[0]],
            [corrente_bateria[0]],
            [kVA_bateria]
    ])

    u_til_k = uk + (np.dot(Gamma_u, bku))
    resultado_ataque_false_data_1 = u_til_k

    y_til_k = yk + (np.dot(Gamma_y, bky))
    resultado_ataque_false_data_2 = y_til_k

    # O Chat mandou colocar essas linhas
    intervalos_false_data.append(x)
    time_attack_false_data.append(1)  # Sempre ativo se chamado  

    #Agora os resultados do ataque são divididos em false_data_1 e false_data_2
    soc_max_false_injection_lista_atuadores.append(float(resultado_ataque_false_data_1[0].item())) 
    soc_false_injection_lista_sensores.append(float(resultado_ataque_false_data_2[0].item()))
    soc_min_false_injection_lista_atuadores.append(float(resultado_ataque_false_data_1[1].item()))
    kWh_false_injection_lista_sensores.append(float(resultado_ataque_false_data_2[1].item()))
    kW_ref_false_injection_lista_atuadores.append(float(resultado_ataque_false_data_1[2].item()))
    kW_false_injection_lista_sensores.append(float(resultado_ataque_false_data_2[2].item()))
    idling_kW_false_injection_lista_atuadores.append(float(resultado_ataque_false_data_1[3].item()))
    tensao_false_injection_lista_sensores.append(float(resultado_ataque_false_data_2[3].item()))
    corrente_false_injection_lista_sensores.append(float(resultado_ataque_false_data_2[4].item()))
    kVA_false_injection_lista_sensores.append(float(resultado_ataque_false_data_2[5].item()))

    return resultado_ataque_false_data_1, resultado_ataque_false_data_2

def ataque_DoS():
    global estado_anterior, dados_salvos_antes_do_ataque, y_tau_y, u_tau_u #variáveis do ataque DoS
    global soc_ataque, kWh_bateria, kW_bateria, kVA_bateria, tensao_bateria, corrente_bateria #variáveis dos sensores
    global soc_min, soc_max, kW_ref, Idling_kW
    # puxar o valor do soc_2 pra ficar de acordo com o gráfico
    # Conjunto de sensores da bateria 
    dss.circuit._set_active_element("Storage.Bateria")
    soc_ataque = float(dss.dssproperties._value_read("23"))
    kWh_bateria = float(dss.dssproperties._value_read("22"))
    kW_bateria = dss.cktelement._powers()
    kVA_bateria = math.sqrt((kW_bateria[0]**2) + (kW_bateria[1]**2))
    tensao_bateria = dss.cktelement._voltages()
    corrente_bateria = dss.cktelement._currents()

    # Conjunto de atuadores
    kW_ref = float(dss.dssproperties._value_read("5"))           
    Idling_kW = float(dss.dssproperties._value_read("30"))

    uk = np.array([
        [soc_max],
        [soc_min],
        [kW_ref], 
        [Idling_kW] 
    ])
    yk = np.array([  #sinal que deveria chegar ao controlador e detector de anomalias
        [soc_ataque],
        [kWh_bateria],
        [kW_bateria[0]],
        [tensao_bateria[0]],
        [corrente_bateria[0]],
        [kVA_bateria]
    ])
    #print(f"yk:{yk}")
    # Gera valor binário (0 ou 1) com Bernoulli
    #resultado = bernoulli(0.85)
    resultado = 1 if random.random() < prob_bernoulli else 0
    # Chat mandou colocar abaixo
    if resultado == 1:
        intervalos_dos.append(x)
        time_attack_dos.append(1)
    else:
        time_attack_dos.append(0)

    Sku = np.eye(4) * resultado

    # Sku = np.array([      #matriz binária que indica se o ataque DoS está sendo performado ou não, varia com o tempo
    #     [resultado, 0, 0],  #depende do passo de simulação!!!
    #     [0, resultado, 0],
    #     [0, 0, resultado],   #3x3
        
    # ])

    Sky = np.eye(6) * resultado

    # Sky = np.array([      #matriz binária que indica se o ataque DoS está sendo performado ou não, varia com o tempo
    #     [resultado, 0, 0, 0, 0],  #depende do passo de simulação!!!
    #     [0, resultado, 0, 0, 0],
    #     [0, 0, resultado, 0, 0],   #5x5
    #     [0, 0, 0, resultado, 0],
    #     [0, 0, 0, 0, resultado]
        
    # ])
    #print(f"Resultado Bernoulli: {resultado}")

    # Detecta transição de 0 → 1
    if resultado == 1 and estado_anterior == 0: # salva o valor do sensor e do atuador 
        y_tau_y = np.array([
            [soc_ataque],
            [kWh_bateria],
            [kW_bateria[0]],
            [tensao_bateria[0]],
            [corrente_bateria[0]],
            [kVA_bateria]
        ])  

        u_tau_u = np.array([
            [soc_max],
            [soc_min],
            [kW_ref],  #Chamar kw_ref corretamente
            [Idling_kW]
        ])
        dados_salvos_antes_do_ataque = True
        #print(f"Transição detectada: salvando soc = {soc:.3f}")
    else:
        dados_salvos_antes_do_ataque = False
        
    estado_anterior = resultado  # atualiza para próxima chamada

    # Exibe estado atual
    #print(f"y_tau_y: {y_tau_y}")
    #print(f"dados_salvos_antes_do_ataque: {dados_salvos_antes_do_ataque}\n")

    Gamma_y_transposta = Gamma_y.T  #matriz gama y maiúsculo transposta
    #multiplicação1 =  5x5 * 5x6 = 5x6 ####  multiplicacao2 = 5x6 * 6x1 = 5x1 ### multiplicacao3 = 6x5 * 5x1 = 6x1 
    #operações para negação de serviço dos sensores
    subtracaoy = yk - y_tau_y #diferença entre o sinal que deveria ser injetado no controlador e o último sinal medido antes do ataque   
    multiplicacao1y = np.dot(Sky, Gamma_y_transposta)  #multiplicação entre a matriz que indica se o ataque está ocorrendo em determinado tempo k e a matriz que mostra os sensores que o aversário domina
    multiplicacao2y= np.dot(multiplicacao1y, subtracaoy)
    byk = multiplicacao2y * -1  #matriz resultante do ataque DoS
    multiplicacao3y = np.dot(Gamma_y , byk)
    y_til_k = yk + multiplicacao3y  #Sinal dos sensores negado 
    resultado_do_ataque_dos_1 = y_til_k
    #print(f"resultado do ataque: {resultado_do_ataque[0][0]}")

    Gamma_u_transposta = Gamma_u.T  #matriz gama y maiúsculo transposta
    #operações para negação de serviço dos sensores
    subtracaou = uk - u_tau_u #diferença entre o sinal que deveria ser injetado no controlador e o último sinal medido antes do ataque   
    multiplicacao1u = np.dot(Sku, Gamma_u_transposta)  #multiplicação entre a matriz que indica se o ataque está ocorrendo em determinado tempo k e a matriz que mostra os sensores que o aversário domina
    multiplicacao2u = np.dot(multiplicacao1u, subtracaou)
    buk = multiplicacao2u * -1  #matriz resultante do ataque DoS
    multiplicacao3u = np.dot(Gamma_u , buk)
    u_til_k = uk + multiplicacao3u  #Sinal dos sensores negado 
    resultado_do_ataque_dos_2 = u_til_k
    #print(f"resultado do ataque: {resultado_do_ataque[0][0]}")
    
    # Imprimir resultado_do_ataque_1 e resultado_do_ataque_2

    soc_max_dos_atuadores.append(float(resultado_do_ataque_dos_2[0].item())) 
    soc_dos_lista_sensores.append(float(resultado_do_ataque_dos_1[0].item())) 
    soc_min_dos_atuadores.append(float(resultado_do_ataque_dos_2[1].item()))
    kWh_dos_lista_sensores.append(float(resultado_do_ataque_dos_1[1].item()))
    kW_ref_dos_atuadores.append(float(resultado_do_ataque_dos_2[2].item()))
    kW_dos_lista_sensores.append(float(resultado_do_ataque_dos_1[2].item()))
    idling_kW_dos_atuadores.append(float(resultado_do_ataque_dos_2[3].item()))
    tensao_dos_lista_sensores.append(float(resultado_do_ataque_dos_1[3].item()))
    corrente_dos_lista_sensores.append(float(resultado_do_ataque_dos_1[4].item()))
    kVA_dos_lista_sensores.append(float(resultado_do_ataque_dos_1[5].item()))

    return resultado_do_ataque_dos_1, resultado_do_ataque_dos_2
     
def replay_attack():
    """
    k0 é o começo da gravação de dados.
    grava de k0 <=t <=kr.
    e repete de kr<t <=kf.
    """    
    global lk_lista_y, lk_lista_u, x, i_y, i_u, k0, kr, kf
    global soc_ataque, kWh_bateria, kW_bateria, kVA_bateria, tensao_bateria, corrente_bateria, Gamma_y #variáveis dos sensores
    global soc_min, soc_max, kW_ref, Idling_kW, Gamma_u 
    # Conjunto de sensores da bateria 
    dss.circuit._set_active_element("Storage.Bateria")
    soc_ataque = float(dss.dssproperties._value_read("23"))
    kWh_bateria = float(dss.dssproperties._value_read("22"))
    kW_bateria = dss.cktelement._powers()
    kVA_bateria = math.sqrt((kW_bateria[0]**2) + (kW_bateria[1]**2))
    tensao_bateria = dss.cktelement._voltages()
    corrente_bateria = dss.cktelement._currents()

    #Conjunto de atuadores do controlador da bateria 
    kW_ref = float(dss.dssproperties._value_read("5"))
    Idling_kW = float(dss.dssproperties._value_read("30"))
 
    Upsilon_y = Gamma_y.T        
    Upsilon_u = Gamma_u.T

    # Fase 1: coleta de dados
    if k0 <= x <= kr:

        uk = np.array([
            [soc_max],
            [soc_min],
            [kW_ref], #adicionar esse método de chamada!!!!
            [Idling_kW] 
        ])
        yk = np.array([  # "matriz 6x1" sinal que deveria chegar ao controlador e detector de anomalias
            [soc_ataque],
            [kWh_bateria],
            [kW_bateria[0]],
            [tensao_bateria[0]],
            [corrente_bateria[0]],
            [kVA_bateria]
        ])
        lku = np.dot(Upsilon_u, uk) # dados do atuador salvos antes do ataque
        lky = np.dot(Upsilon_y, yk) # dados do sensor salvos antes do ataque
        #print(lky)
        lk_lista_y.append(lky)
        lk_lista_u.append(lku)
        #print(lk_lista)

    # Fase 2: Repetição dos dados coletados
    elif kr < x <= kf:
        n_elementos_y = len(lk_lista_y) #neste exemplo é 6
        n_elementos_u = len(lk_lista_u)
        if kr < x <= kf:
            intervalos_replay.append(x)
            time_attack_replay.append(1)
        else:
            time_attack_replay.append(0)
        #print(n_elementos)
        if i_y < (n_elementos_y): # i < 5
            replay_y = lk_lista_y[i_y]
            soc_ataque = replay_y[0][0]
            kWh_bateria = replay_y[1][0]
            kW_bateria[0] = replay_y[2][0]
            tensao_bateria[0] = replay_y[3][0]
            corrente_bateria[0] = replay_y[4][0]
            kVA_bateria = replay_y[5][0]
            #print(resultado_replay)
            i_y += 1
        if i_y == (n_elementos_y):
            i_y = 0

        if i_u < (n_elementos_u): # i < 5
            replay_u = lk_lista_u[i_u]
            soc_max = replay_u[0][0]
            soc_min = replay_u[1][0]
            kW_ref = replay_u[2][0]
            Idling_kW = replay_u[3][0] # Rever essa parte do Idling_kW
            #print(resultado_replay)
            i_u += 1
        if i_u == (n_elementos_u):
            i_u = 0
    soc_replay_lista_sensores.append(float(soc_ataque))
    kWh_replay_lista_sensores.append(float(kWh_bateria))
    kW_replay_lista_sensores.append(float(kW_bateria[0]))
    tensao_replay_lista_sensores.append(float(tensao_bateria[0]))
    corrente_replay_lista_sensores.append(float(corrente_bateria[0]))
    kVA_replay_lista_sensores.append(float(kVA_bateria))
    kW_ref_replay_atuadores.append(float(kW_ref))
    idling_kW_replay_atuadores.append(float(Idling_kW))
    soc_max_replay_atuadores.append(float(soc_max))
    soc_min_replay_atuadores.append(float(soc_min))

    #adicionar os valores de kwref, soc max e mínimo no gráfico, também deve ser adicionado no return
    return soc_ataque, kWh_bateria, kW_bateria[0], tensao_bateria[0], corrente_bateria[0], kVA_bateria, kW_ref, Idling_kW, soc_max, soc_min

def injecao_dados_falsos_customizavel():
    global soc_ataque, kWh_bateria, kW_bateria, kVA_bateria, tensao_bateria, corrente_bateria # variáveis dos sensores
    global soc_min, soc_max, kW_ref, Idling_kW
    # Conjunto de sensores da bateria 
    dss.circuit._set_active_element("Storage.Bateria")
    soc_ataque = float(dss.dssproperties._value_read("23"))
    kWh_bateria = float(dss.dssproperties._value_read("22"))
    kW_bateria = dss.cktelement._powers()
    kVA_bateria = math.sqrt((kW_bateria[0]**2) + (kW_bateria[1]**2))
    tensao_bateria = dss.cktelement._voltages()
    corrente_bateria = dss.cktelement._currents()
    #conjunto de atuadores
    kW_ref = float(dss.dssproperties._value_read("5"))
    Idling_kW = float(dss.dssproperties._value_read("30"))

    #======== Coloque a função aqui ==========================================================================================
    #Example:
    def gerar_senoide(amplitude=100.0, frequencia=0.1, fase=0.0, x=0):
        return amplitude * np.sin(2 * np.pi * frequencia * x + fase)

    #===========================================================================================================================
    resultado = gerar_senoide(amplitude=10.0, frequencia=0.05, fase=0.0, x=x)
    if 20 <= x <= 60: #intervalo de ataque
        yk = np.array([  # "matriz 6x1" sinal que deveria chegar ao controlador e detector de anomalias
            [soc_ataque],
            [kWh_bateria],
            [kW_bateria[0]],
            [tensao_bateria[0]],
            [corrente_bateria[0]],
            [kVA_bateria]
        ])

        uk = np.array([
        [soc_max],
        [soc_min],
        [kW_ref], 
        [Idling_kW]  
        ])
        
        bky = np.array([
          [resultado],  # o sinal que você irá utilizar para corromper o sinal deve ser colocado dentro das células da matriz bky
          [resultado],
          [resultado],
          [resultado],
          [resultado],
          [resultado]
        ])
        bku = np.array([
          [resultado],  # o sinal que você irá utilizar para corromper o sinal deve ser colocado dentro das células da matriz bky
          [resultado],
          [resultado],
          [resultado]
        ])
        u_til_k = uk + (np.dot(Gamma_u, bku))
        resultado_ataque_false_data_customizavel_1 = u_til_k

        y_til_k = yk + (np.dot(Gamma_y, bky))
        resultado_ataque_false_data_customizavel_2 = y_til_k

    # else:
    #     # Sem ataque → valores reais
    #     y_til_k = yk
    #     u_til_k = uk

        soc_false_injection_customizavel_lista_sensores.append(float(resultado_ataque_false_data_customizavel_2[0].item()))
        kWh_false_injection_customizavel_lista_sensores.append(float(resultado_ataque_false_data_customizavel_2[1].item()))
        corrente_false_injection_customizavel_lista_sensores.append(float(resultado_ataque_false_data_customizavel_2[4].item()))
        kVA_false_injection_customizavel_lista_sensores.append(float(resultado_ataque_false_data_customizavel_2[5].item()))
        soc_max_false_injection_customizavel_lista_atuadores.append(float(resultado_ataque_false_data_customizavel_1[0].item())) 
        soc_min_false_injection_customizavel_lista_atuadores.append(float(resultado_ataque_false_data_customizavel_1[1].item()))
        kW_ref_false_injection_lista_customizavel_atuadores.append(float(resultado_ataque_false_data_customizavel_1[2].item()))
        idling_kW_false_injection_customizavel_lista_atuadores.append(float(resultado_ataque_false_data_customizavel_1[3].item()))

        return resultado_ataque_false_data_customizavel_1, resultado_ataque_false_data_customizavel_2

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

    # Degradação do Soc_Máx e Soc_Mín
    soc_2 = aplicar_controle_bateria(soc, soc_max, soc_min)
    soc_lista_2.append(soc_2)

    # Aplicação do ataque do Lucão
    x = step  # os valores dos passos da simulação de acordo com o Lucão   

    if enable_dos:
        ataque_DoS() 

    if enable_replay:
        replay_attack()

    if enable_false_data:
        false_data()

    if enable_false_data_customizable:
        injecao_dados_falsos_customizavel()    

    # Contagem de ciclos
    contador_ciclos, carga_completa, descarga_completa, soc_max, soc_min, soh = atualizar_contagem_ciclos(
        soc, soc_max, soc_min, contador_ciclos, carga_completa, descarga_completa, soh,
        contador_soc_max, contador_soc_min, taxa_degradacao, taxa_degradacao_por_ciclo
    )

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

# ============================= PLOT ==============================

horas = np.linspace(0, original_steps, original_steps)

# ==================== FUNÇÃO PARA REGIÕES DE ATAQUE ====================

def plot_attack_regions(time_vector, step_size, label="Ataque"):
    in_attack = False
    for i in range(len(time_vector)):
        if time_vector[i] == 1 and not in_attack:
            start = i
            in_attack = True
        elif time_vector[i] == 0 and in_attack:
            end = i
            plt.axvspan(start * step_size, end * step_size, color='red', alpha=0.2, label=label if start == 0 else "")
            in_attack = False
    if in_attack:
        plt.axvspan(start * step_size, len(time_vector) * step_size, color='red', alpha=0.2, label=label if start == 0 else "")

plotar_resultados_ataques(horas)

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




