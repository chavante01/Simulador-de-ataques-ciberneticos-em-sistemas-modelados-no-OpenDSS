import opendssdirect as dss
import os
from os.path import abspath, dirname
import matplotlib.pyplot as plt
import numpy as np

def solve_settings():   
    dss_file = r"C:\soh_bateria_opendss\123Bus\IEEE123Master.dss"
    dss.Text.Command('Clear')
    pwd = dirname(abspath(__file__))
    dss.Text.Command(f"Compile [{dss_file}]")
    dss.Text.Command("set maxcontroliter = 200")
    dss.Text.Command("set maxiterations = 100")
    dss.Text.Command("set mode = daily")
    dss.Text.Command("set stepsize = 60s")
    print("Configurações de simulação aplicadas.")

def contador_ciclos_e_soh():
    contador_ciclos = 0
    carga_completa = False
    descarga_completa = False
    soh = 100.0  # SOH inicial
    taxa_degradacao_por_ciclo = 0.009
    iteracoes = []
    soh_lista = []

    dss.Circuit.SetActiveElement("Storage.Bateria")

    for i in range(8760):
        dss.Solution.Solve()
        soc = float(dss.Properties.Value("%stored"))

        iteracoes.append(i + 1)
        soh_lista.append(soh)

        #print(f"Iteração {i + 1}: SOC = {soc}%, SOH = {soh:.2f}%")

        if not carga_completa and soc >= 60:
            carga_completa = True
            #print("Carga completa detectada.")

        if carga_completa and not descarga_completa and soc <= 40:
            descarga_completa = True
            #print("Descarga completa detectada.")

        if carga_completa and descarga_completa:
            contador_ciclos += 1
            soh = 100 * np.exp(-taxa_degradacao_por_ciclo * contador_ciclos)  # Exponencial
            #print(f"Ciclo completo! Total: {contador_ciclos}, SOH = {soh:.2f}%")
            carga_completa = False
            descarga_completa = False

    print(f"Total de ciclos completos: {contador_ciclos}")
    print(f"SOH final da bateria: {soh:.2f}%")

    plt.figure(figsize=(10, 6))
    plt.plot(iteracoes, soh_lista, marker='o', linestyle='-', label="SOH (%)")
    plt.title("Degradação Exponencial do SOH ao Longo do Tempo")
    plt.xlabel("Iteração (Horas)")
    plt.ylabel("SOH (%)")
    plt.grid(True)
    plt.legend()
    plt.show()

solve_settings()
contador_ciclos_e_soh()