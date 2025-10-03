def fcfs(processes, context_switch=1):
    # Faz cópia para não alterar lista original
    procs = [p.copy() for p in processes]
    current_time = 0
    timeline = []
    last_pid = None

    # Inicializa atributos
    for p in procs:
        p["remaining"] = p["burst"]
        p["completion"] = None

    # Ordena por arrival
    procs.sort(key=lambda x: x["arrival"])

    for p in procs:
        # Se a CPU está ociosa e o processo ainda não chegou, pula tempo
        if current_time < p["arrival"]:
            current_time = p["arrival"]

        # Se for trocar de processo, adiciona CS
        if last_pid is not None and last_pid != p["pid"]:
            current_time += context_switch
            timeline.append("CS")

        # Executa o processo até terminar
        start = current_time
        end = current_time + p["burst"]
        timeline.append(p["pid"])
        current_time = end

        # Marca conclusão
        p["remaining"] = 0
        p["completion"] = current_time
        last_pid = p["pid"]

    # Calcula turnaround e waiting
    for p in procs:
        p["turnaround"] = p["completion"] - p["arrival"]
        p["waiting"] = p["turnaround"] - p["burst"]

    return procs, timeline

processos = [
    {"pid": "P1", "arrival": 0, "burst": 5},
    {"pid": "P2", "arrival": 1, "burst": 3},
    {"pid": "P3", "arrival": 2, "burst": 7},
]

resultado, linha_tempo = fcfs(processos)

print("Timeline:", linha_tempo)
for p in resultado:
    print(p)
