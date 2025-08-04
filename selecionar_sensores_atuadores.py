def selecionar_alvos():
    # Dicionário de sensores
    sensores = {
        0: "SOC da Bateria",
        1: "Energia da Bateria (kWh)",
        2: "Potência Ativa da Bateria (kW)",
        3: "Tensão da Bateria (V)",
        4: "Corrente da Bateria (A)"
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

    Gamma_y = np.zeros((6, 5))  # Matriz 6x5
    for idx in selecionados_sensores:
        if 0 <= idx <= 4:
            Gamma_y[idx, idx] = 1
        else:
            print(f" Índice de sensor inválido ignorado: {idx}")

    # ---- Atuadores ----
    print("\nAtuadores disponíveis para ataque:")
    for idx, nome in atuadores.items():
        print(f"[{idx}]: {nome}")
    entrada_atuadores = input("\nDigite os índices dos atuadores para ataque (ex: 0,2): ")
    selecionados_atuadores = list(map(int, entrada_atuadores.strip().split(",")))

    Gamma_u = np.zeros((4, 3))  # Matriz 4x3
    for idx in selecionados_atuadores:
        if 0 <= idx <= 2:
            Gamma_u[idx, idx] = 1
        elif idx == 3:
            Gamma_u[idx, 2] = 1  # Idling_kW compartilha a coluna com kW_ref
        else:
            print(f" Índice de atuador inválido ignorado: {idx}")

    return Gamma_y, Gamma_u