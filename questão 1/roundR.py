def round_robin(processes, quantum, context_switch=1):
    # Inicialização
    current_time = 0
    ready_queue = []
    timeline = []  # lista de execução (pid ou 'CS')
    last_pid = None

    # Prepara dicionários para cada processo
    for p in processes:
        p["remaining"] = p["burst"]
        p["completion"] = None

    # Enquanto ainda houver processos a terminar
    while any(p["remaining"] > 0 for p in processes):
        # Adicionar processos que chegaram até agora
        for p in processes:
            if p["arrival"] <= current_time and p["remaining"] > 0 and p not in ready_queue:
                ready_queue.append(p)

        if not ready_queue:  
            # Se ninguém está pronto, pula para o próximo arrival
            next_arrival = min(p["arrival"] for p in processes if p["remaining"] > 0)
            current_time = next_arrival
            continue

        # Pega próximo da fila
        proc = ready_queue.pop(0)

        # Se trocou de processo, adiciona CS
        if last_pid is not None and last_pid != proc["pid"]:
            current_time += context_switch
            timeline.append("CS")

        # Executa
        run_time = min(quantum, proc["remaining"])
        timeline.append(proc["pid"])
        current_time += run_time
        proc["remaining"] -= run_time
        last_pid = proc["pid"]

        # Adiciona processos que chegaram durante a execução do quantum
        for p in processes:
            if (
                p["arrival"] > current_time - run_time
                and p["arrival"] <= current_time
                and p["remaining"] > 0
                and p not in ready_queue
                and p != proc
            ):
                ready_queue.append(p)

        # Se terminou, registra tempo de conclusão
        if proc["remaining"] == 0:
            proc["completion"] = current_time
        else:
            # Recoloca no fim da fila
            ready_queue.append(proc)

    # Calcula métricas
    for p in processes:
        turnaround = p["completion"] - p["arrival"]
        waiting = turnaround - p["burst"]
        p["turnaround"] = turnaround
        p["waiting"] = waiting

    return processes, timeline

processos = [
    {"pid": "P1", "arrival": 0, "burst": 5},
    {"pid": "P2", "arrival": 1, "burst": 3},
    {"pid": "P3", "arrival": 2, "burst": 7},
]

resultado, linha_tempo = round_robin(processos, quantum=2)

print("Timeline:", linha_tempo)
for p in resultado:
    print(p)
