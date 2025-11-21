# %%

from gurobipy import Model, GRB, quicksum
from load_data import L, N, G, E, P, R, T, costo_g, plazo_g, gen1, emp_g, ubi_g, tec, cap, req, max_t, costo_n, plazo_n, emp_n, ubi_n, proyectos_g


model = Model("GeneracionElectrica")
model.setParam('TimeLimit', 1800)

x = model.addVars(L, T, vtype=GRB.BINARY, name="x")
y = model.addVars(L, T, vtype=GRB.BINARY, name="y")
w = model.addVars(N, T, vtype=GRB.BINARY, name="w")
z = model.addVars(N, T, vtype=GRB.BINARY, name="z")

model.update()

#Restricciones

#1. La capacidad de generaci´on el´ectrica total es suficiente para satisfacer la demanda energ´etica proyectada para el 2050
model.addConstr(quicksum((x[l, t] * gen1[l]) for l in L for t in (T)) >= req)

print("Restricción agregada 1")

#2. Todos lo proyectos deben terminarse a mas tardar en diciembre de 2049
model.addConstrs(x[l, t] * t + plazo_g[l] <= 50 for l in L for t in (T))
model.addConstrs(w[n, t] * t + plazo_n[n] <= 50 for n in N for t in (T))

print("Restricción agregada 2")

#3. Una empresa solo puede desarrollar tantos proyectos paralelamente como le permite su capacidad.
L_por_empresa = {e: [] for e in E}
N_por_empresa = {e: [] for e in E}

for l in L:
    for e in E:
        if emp_g.get((l, e), 0) == 1:
            L_por_empresa[e].append(l)
            break 

for n in N:
    for e in E:
        if emp_n.get((n, e), 0) == 1:
            N_por_empresa[e].append(n)
            break

model.addConstrs(
    (quicksum(y[l, t] for l in L_por_empresa[e]) + quicksum(z[n, t] for n in N_por_empresa[e])) <= cap for e in E for t in T)

print("Restricción agregada 3")

#4. No pueden realizarse 2 proyectos en la misma ubicaci´on. N´otese que esto evita que un proyecto se construya 2 veces
model.addConstrs(quicksum(x[l, t] * ubi_g[l, p] for l in L for t in T) <= 1 for p in P)
model.addConstrs(quicksum(w[n, t] * ubi_n[n, p] for n in N for t in T) <= 1 for p in P)

print("Restricción agregada 4")

#5. Para hacer un proyecto de transmisión debe haber uno de generación asociado
model.addConstrs(quicksum(x[l, t] * ubi_g[l, p] for l in L for t in T) <= quicksum(w[n, t] * ubi_n[n, p] for n in N for t in T) for p in P)

print("Restricción agregada 5")

#6. Comportamiento de yℓ,t y de z
model.addConstrs(y[l, t] == quicksum(x[l, tau] for tau in range(max(1, t - plazo_g[l] + 1), t + 1)) for l in L for t in T)
model.addConstrs(z[n, t] == quicksum(w[n, tau] for tau in range(max(1, t - plazo_n[n] + 1), t + 1)) for n in N for t in T)

print("Restricción agregada 6")

#7. No construir más proyectos de cierta tecnología que los que te permite la regi´on

proyectos_por_zona = {}
for l in L:
    region = proyectos_g[l].Region
    for g in G:
        if tec.get((l, g), 0) == 1:
            if (region, g) not in proyectos_por_zona:
                proyectos_por_zona[(region, g)] = []
            proyectos_por_zona[(region, g)].append(l)

model.addConstrs((quicksum(x[l, t] for l in proyectos_por_zona.get((r, g), []) for t in T) <= max_t[r, g]) for r in R for g in G)

print("Restricción agregada 7")

model.update()

#Función objetivo
model.setObjective(quicksum(costo_g[l] * x[l, t] for l in L for t in T) + quicksum(w[n, t] * costo_n[n] for n in N for t in T), GRB.MINIMIZE)

model.update()

print("Iniciando optimización...")

model.optimize()

print(model.status)

if model.Status == GRB.OPTIMAL:
    print("\n¡Solución óptima encontrada!")
    print(f"Valor objetivo (costo total): {model.ObjVal:,.2f} UF")

    proyectos_gen = []
    proyectos_trans = []

    for l in L:
        for t in T:
            var = model.getVarByName(f"x[{l},{t}]")
            if var is not None and var.X > 0.5:
                print(f"El proyecto de generacion {l} se inicia en el semestre {t}")
                proyectos_gen.append((l, t))

    for n in N:
        for t in T:
            var = model.getVarByName(f"w[{n},{t}]")
            if var is not None and var.X > 0.5:
                print(f"El proyecto de transmision {n} se inicia en el semestre {t}")
                proyectos_trans.append((n, t))

    print(f"Proyectos de Generación: {len(proyectos_gen)}")
    print(f"Proyectos de Transmisión: {len(proyectos_trans)}")

    empresas_gen = set()
    empresas_trans = set()
    for l, t in proyectos_gen:
        for e in E:
            if emp_g[l, e] == 1:
                empresas_gen.add(e)

    for n, t in proyectos_trans:
        for e in E:
            if emp_n[n, e] == 1:
                empresas_trans.add(e)

    empresas_totales = empresas_gen.union(empresas_trans)
    print(f"\n{'Empresas totales contratadas:'} {len(empresas_totales)}")
    print(f"Empresas de Generación: {len(empresas_gen)}")
    print(f"Empresas de Transmisión: {len(empresas_trans)}")

    print(f"\n{'Proyectos según la región:':}")
    regiones = {}
    for l, t in proyectos_gen:
        for r in R:
            for p in P:
                if ubi_g[l, p] == 1:
                    regiones[r] = regiones.get(r, 0) + 1
                    break

    for r in sorted(regiones.keys()):
        print(f"La región {r} tiene {regiones[r]} proyectos")

else:
    print("No se encontró una solución óptima.")