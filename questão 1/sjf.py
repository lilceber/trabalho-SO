def sjf(processes, context_switch=1):
    # Faz cópia para não alterar original
    procs = [p.copy() for p in processes]
    current_time = 0
    timeline = []
    last_pid = None

    # Inicializa atributos
    for p in procs:
        p["remaining"] = p["burst"]
        p["completion"] = None

    finished = []

    while len(finished) < len(procs):
        # pega todos os que já chegaram e não finalizaram
        ready = [p for p in procs if p["arrival"] <= current_time and p not in finished]

        if not ready:  
            # ninguém pronto → avança até o próximo arrival
            next_arrival = min(p["arrival"] for p in procs if p not in finished)
            current_time = next_arrival
            continue

        # escolhe o de menor burst (tie-breaker: menor arrival)
        ready.sort(key=lambda x: (x["burst"], x["arrival"]))
        proc = ready[0]

        # se trocou de processo → CS
        if last_pid is not None and last_pid != proc["pid"]:
            current_time += context_switch
            timeline.append("CS")

        # executa até terminar
        start = current_time
        end = current_time + proc["burst"]
        timeline.append(proc["pid"])
        current_time = end

        proc["remaining"] = 0
        proc["completion"] = current_time
        finished.append(proc)
        last_pid = proc["pid"]

    # calcula métricas
    for p in procs:
        p["turnaround"] = p["completion"] - p["arrival"]
        p["waiting"] = p["turnaround"] - p["burst"]

    return procs, timeline

processos = [
    {"pid": "P1", "arrival": 0, "burst": 5},
    {"pid": "P2", "arrival": 1, "burst": 3},
    {"pid": "P3", "arrival": 2, "burst": 7},
    {"pid": "P4", "arrival": 3, "burst": 2},
]

resultado, linha_tempo = sjf(processos)

print("Timeline:", linha_tempo)
for p in resultado:
    print(p)
