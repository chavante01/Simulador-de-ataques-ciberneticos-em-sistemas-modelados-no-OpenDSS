import os
import py_dss_interface
import numpy as np
import matplotlib.pyplot as plt

# Instância do OpenDSS
dss = py_dss_interface.DSS()

# ========================= CONTROLE SOC COM DEGRADAÇÃO =========================

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

def aplicar_degradacao_soc(soc_max_atual, soc_min_atual, taxa_degradacao, limite_superior=60, limite_inferior=40):
    novo_soc_max = max(soc_max_atual - taxa_degradacao, limite_superior)
    novo_soc_min = min(soc_min_atual + taxa_degradacao, limite_inferior)
    return novo_soc_max, novo_soc_min

def controle_soc_por_ciclo(stepNumber):
    global soc_max, soc_min, contador_ciclos, carga_completa, descarga_completa, soh
    global kW_painel_lista, kW_bateria_lista, kW_carga_lista 

    dss.circuit._set_active_element("Storage.Bateria")
    soc = float(dss.dssproperties._value_read("23"))
    kW_bateria = float(dss.dssproperties._value_read("5"))

    dss.circuit._set_active_element("Load.634a")
    kW_carga = dss.cktelement._powers()[0]
    #kW_carga = float(dss.dssproperties._value_read("4"))
    #kW_carga = dss.loads._kw()

    dss.circuit._set_active_element("PVSystem.PV")
    kW_painel = dss.cktelement._powers()[0] * (-1)
    #kW_painel = float(dss.dssproperties._value_read("5"))
    #kW_painel = dss.pvsystems._kw()
    #kW_painel = dss.pvsystems.kw_output()

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
        if kW_painel >= kW_carga:
            dss.text("Edit Storage.Bateria state=idling %Charge=0 %Discharge=0")        
        else:
            dss.text("Edit Storage.Bateria %Charge=0 dispmode=external %stored=" + str(soc_max))

    elif soc < soc_min:
        if kW_painel >= kW_carga:
            dss.text("Edit Storage.Bateria state=idling %Charge=0 %Discharge=0") 
        else:
            dss.text("Edit Storage.Bateria %Discharge=0 dispmode=external %stored=" + str(soc_min))

    else:
        if kW_painel >= kW_carga:
            dss.text("Edit Storage.Bateria state=idling %Charge=0 %Discharge=0") 
        else:
            dss.loadshapes._name()
            dss.text("Edit Storage.Bateria %Charge=100 %Discharge=100 dispmode=follow daily=storageCurve")
        
    dss.circuit._set_active_element("Storage.Bateria")
    soc_2 = float(dss.dssproperties._value_read("23"))
    soc_lista_2.append(soc_2)

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
    dss.text("set maxcontroliter=2000")
    dss.text("set maxiterations=1000")
    dss.text("set mode=daily")
    dss.text("set stepsize=500h")
    dss.text("Disable StorageController.*")
    print("Configurações aplicadas.")
    return dss_file



dss_file = solve_settings()
original_steps = 100  # 168 passos = 7 dias
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

print(f"\nSimulação finalizada. Total de ciclos completos: {contador_ciclos}")

# ============================= PLOT ==============================

horas = np.linspace(0, 100, original_steps)
# Gráfico 1: SOC e limites
plt.figure(figsize=(12, 5))
plt.plot(horas, soc_lista_2, label="SOC (%)", linewidth=1)
plt.plot(horas, soc_max_lista, linestyle="--", label="SOC Máx")
plt.plot(horas, soc_min_lista, linestyle="--", label="SOC Mín")
plt.title("SOC com Controle e Degradação por Ciclos")
plt.xlabel("Hora")
plt.ylabel("SOC (%)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# Gráfico 2: SOH
plt.figure(figsize=(12, 5))
plt.plot(horas, soh_lista, linestyle="-.", color="purple", label="SOH (%)")
plt.title("SOH (State of Health) da Bateria")
plt.xlabel("Hora")
plt.ylabel("SOH (%)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()