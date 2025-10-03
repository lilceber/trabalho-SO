
from math import sqrt

# -------------------------
# Round Robin (RR)
# -------------------------
def round_robin(processes, quantum, context_switch=1):
    # cria cópias (para não alterar entrada original)
    procs = [ { **p } for p in processes ]
    for p in procs:
        p["remaining"] = p["burst"]
        p["completion"] = None

    current_time = 0
    ready_queue = []
    timeline = []
    last_pid = None

    # loop até todos terminarem
    while any(p["remaining"] > 0 for p in procs):
        # adicionar chegadas até current_time
        for p in procs:
            if p["arrival"] <= current_time and p["remaining"] > 0 and p not in ready_queue:
                ready_queue.append(p)

        if not ready_queue:
            # pula para próxima chegada
            future = [p["arrival"] for p in procs if p["remaining"] > 0]
            current_time = min(future)
            continue

        proc = ready_queue.pop(0)

        # context switch se mudou de processo e não for o primeiro
        if last_pid is not None and last_pid != proc["pid"]:
            timeline.append(("CS", current_time, current_time + context_switch))
            current_time += context_switch

        run_time = min(quantum, proc["remaining"])
        timeline.append((proc["pid"], current_time, current_time + run_time))
        current_time += run_time
        proc["remaining"] -= run_time
        last_pid = proc["pid"]

        # adicionar novas chegadas que ocorreram DURANTE a execução
        for p in procs:
            if p["arrival"] <= current_time and p["remaining"] > 0 and p not in ready_queue and p is not proc:
                ready_queue.append(p)

        if proc["remaining"] == 0:
            proc["completion"] = current_time
        else:
            ready_queue.append(proc)

    # calcular turnaround e waiting
    for p in procs:
        p["turnaround"] = p["completion"] - p["arrival"]
        p["waiting"] = p["turnaround"] - p["burst"]

    return procs, timeline

# -------------------------
# FCFS
# -------------------------
def fcfs(processes, context_switch=1):
    procs = [ { **p } for p in processes ]
    for p in procs:
        p["remaining"] = p["burst"]
        p["completion"] = None

    procs.sort(key=lambda x: x["arrival"])
    current_time = 0
    timeline = []
    last_pid = None

    for p in procs:
        if current_time < p["arrival"]:
            current_time = p["arrival"]

        if last_pid is not None and last_pid != p["pid"]:
            timeline.append(("CS", current_time, current_time + context_switch))
            current_time += context_switch

        timeline.append((p["pid"], current_time, current_time + p["burst"]))
        current_time += p["burst"]
        p["remaining"] = 0
        p["completion"] = current_time
        last_pid = p["pid"]

    for p in procs:
        p["turnaround"] = p["completion"] - p["arrival"]
        p["waiting"] = p["turnaround"] - p["burst"]

    return procs, timeline

# -------------------------
# SJF não preemptivo
# -------------------------
def sjf_non_preemptive(processes, context_switch=1):
    procs = [ { **p } for p in processes ]
    for p in procs:
        p["remaining"] = p["burst"]
        p["completion"] = None

    current_time = 0
    timeline = []
    last_pid = None
    finished = []

    while len(finished) < len(procs):
        ready = [p for p in procs if p["arrival"] <= current_time and p not in finished]
        if not ready:
            future = [p["arrival"] for p in procs if p not in finished]
            current_time = min(future)
            continue

        # escolhe menor burst; desempata por arrival
        ready.sort(key=lambda x: (x["burst"], x["arrival"]))
        proc = ready[0]

        if last_pid is not None and last_pid != proc["pid"]:
            timeline.append(("CS", current_time, current_time + context_switch))
            current_time += context_switch

        timeline.append((proc["pid"], current_time, current_time + proc["burst"]))
        current_time += proc["burst"]
        proc["remaining"] = 0
        proc["completion"] = current_time
        finished.append(proc)
        last_pid = proc["pid"]

    for p in procs:
        p["turnaround"] = p["completion"] - p["arrival"]
        p["waiting"] = p["turnaround"] - p["burst"]

    return procs, timeline

# -------------------------
# métricas: média, desvio populacional e throughput
# -------------------------
def mean(values):
    if not values:
        return 0.0
    return sum(values) / len(values)

def std_population(values):
    if not values:
        return 0.0
    mu = mean(values)
    var = sum((x - mu)**2 for x in values) / len(values)   # divisão por N -> populacional
    return sqrt(var)

def throughput(processes, T):
    # conta quantos processos completaram até tempo T (completion <= T)
    return sum(1 for p in processes if p["completion"] is not None and p["completion"] <= T)

# -------------------------
# função utilitária para rodar e imprimir resumo
# -------------------------
def run_and_report(name, fn, *args, T=100, **kwargs):
    procs, timeline = fn(*args, **kwargs)
    waits = [p["waiting"] for p in procs]
    turns = [p["turnaround"] for p in procs]

    print(f"=== {name} ===")
    print("Timeline:", timeline)
    print("Per-process:")
    for p in procs:
        print(f"  {p['pid']}: arrival={p['arrival']} burst={p['burst']} completion={p['completion']} waiting={p['waiting']} turnaround={p['turnaround']}")

    mean_wait = mean(waits)
    std_wait = std_population(waits)
    mean_turn = mean(turns)
    std_turn = std_population(turns)
    thr = throughput(procs, T)

    print(f"\nMétricas (T={T}):")
    print(f"  mean waiting = {mean_wait:.3f}, std waiting = {std_wait:.3f}")
    print(f"  mean turnaround = {mean_turn:.3f}, std turnaround = {std_turn:.3f}")
    print(f"  throughput = {thr}\n")
    return procs, timeline

# -------------------------
# exemplo de uso
# -------------------------
if __name__ == "__main__":
    processos = [
        {"pid": "P1", "arrival": 0, "burst": 5},
        {"pid": "P2", "arrival": 1, "burst": 3},
        {"pid": "P3", "arrival": 2, "burst": 7},
        {"pid": "P1", "arrival": 4, "burst": 5},
        {"pid": "P2", "arrival": 6, "burst": 3}
    ]

    # RR: use quantum 2 e CS=1 (exemplo)
    run_and_report("Round Robin", round_robin, processos, quantum=8, context_switch=1, T=20)

    # FCFS
    run_and_report("FCFS", fcfs, processos, context_switch=1, T=20)

    # SJF não preemptivo
    run_and_report("SJF non-preemptive", sjf_non_preemptive, processos, context_switch=1, T=20)
