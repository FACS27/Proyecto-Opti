# %%

from gurobipy import Model, GRB, quicksum
from load_data import L, N, G, E, P, R, T, costo_g, plazo_g, gen1, emp_g, ubi_g, tec, cap, req, max, costo_n, plazo_n, trans1, emp_n, ubi_n


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

#2. Todos lo proyectos deben terminarse a mas tardar en diciembre de 2049
model.addConstrs(x[l, t] * t + plazo_g[l] <= 50 for l in L for t in (T))
model.addConstrs(w[n, t] * t + plazo_n[n] <= 50 for n in N for t in (T))

#3. Una empresa solo puede desarrollar tantos proyectos paralelamente como le permite su capacidad.
model.addConstrs(quicksum(y[l, t] * emp_g[l, e] for l in L) + quicksum(z[n, t] * emp_n[n, e] for n in N) <= 1000 for e in E for t in T)

#4. No pueden realizarse 2 proyectos en la misma ubicaci´on. N´otese que esto evita que un proyecto se construya 2 veces
model.addConstrs(quicksum(x[l, t] * ubi_g[l, p] for l in L for t in T) <= 1 for p in P)
model.addConstrs(quicksum(w[n, t] * ubi_n[n, p] for n in N for t in T) <= 1 for p in P)

#5. Para hacer un proyecto de transmisión debe haber uno de generación asociado
model.addConstrs(quicksum(x[l, t] * ubi_g[l, p] for l in L for t in T) >= quicksum(w[n, t] * ubi_n[n, p] for n in N for t in T) for p in P)

#6. Comportamiento de yℓ,t y de z
model.addConstrs(x[l, t] <= y[l, t + t_prima] for l in L for t in T for t_prima in range(plazo_g[l]) if t + t_prima < len(T)) #revisar lo del if t + t_prima
model.addConstrs(quicksum(y[l, t] for t in T) == quicksum(x[l, t] * plazo_g[l] for t in T) for l in L)

model.addConstrs(w[n, t] <= z[n, t + t_prima] for n in N for t in T for t_prima in range(plazo_n[n]) if t + t_prima < len(T)) #revisar lo del if t + t_prima
model.addConstrs(quicksum(z[n, t] for t in T) == quicksum(w[n, t] * plazo_n[n] for t in T) for n in N) 

#7. No construir más proyectos de cierta tecnología que los que te permite la regi´on
model.addConstrs(quicksum(x[l, t] * tec[l, g] * ubi_g[l, p] for l in L for t in T for p in P) <= max[r, g] for r in R for g in G)

#8. No superar la capacidad de transmisión de cada línea
model.addConstrs(quicksum(w[n, t] * trans1[n] * ubi_n[n, p] for t in T for n in (N)) >= quicksum(x[l, t] * gen1[l] * ubi_g[l, p] for l in (L) for t in (T)) for p in P)

model.update()

#Función objetivo
model.setObjective(quicksum(costo_g[l] * x[l, t] for l in L for t in T) + quicksum(w[n, t] * costo_n[n] for n in N for t in T), GRB.MINIMIZE)

model.update()

print("Iniciando optimización...")

model.optimize()

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

elif model.Status == GRB.INFEASIBLE:
    print("\nEl modelo es INFACTIBLE.")
    print("Calculando IIS (Irreducible Inconsistent Subsystem) para encontrar el conflicto...")
    
    # Calcular IIS para que Gurobi te diga qué restricciones están en conflicto
    model.computeIIS()
    model.write("modelo_infactible.ilp")
    print("Se ha guardado un archivo 'modelo_infactible.ilp'.")
    print("Ábrelo para ver las restricciones que causan el conflicto.")

elif model.Status == GRB.UNBOUNDED:
    print("\nEl modelo es NO ACOTADO (Unbounded).")

elif model.Status == GRB.TIME_LIMIT:
    print("\nLímite de tiempo alcanzado.")
    if model.SolCount > 0:
        print(f"Se encontró una solución (no óptima). Costo: {model.ObjVal:,.2f} UF")
        # (Aquí podrías duplicar el código para imprimir la solución encontrada)
    else:
        print("No se encontró ninguna solución factible antes del límite de tiempo.")

else:
    print(f"\nOptimización terminada con estado: {model.Status}")
