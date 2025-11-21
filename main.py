#%%
import numpy as np
from gurobipy import Model, GRB, quicksum
from load_data import L, N, G, E, P, R, T, costo_l, plazo_l, gen_l, emp_l, ubi_l, tec_l, cap_e, REQ, max, costo_n, plazo_n, trans_n, emp_n, ubi_n

#TODO Revisar que todo esté bien indexado
#TODO Revisar datos para las fechas y costos
#TODO Buscar datos faltantes


def modelo():

    model = Model("GeneracionElectrica")
    model.setParam('TimeLimit', 1800)


    x = model.addVars(L, T, vtype=GRB.BINARY, name="x")
    y = model.addVars(L, T, vtype=GRB.BINARY, name="y")
    w = model.addVars(N, T, vtype=GRB.BINARY, name="w")
    z = model.addVars(N, T, vtype=GRB.BINARY, name="z")

    model.update()

    #Restricciones

    #1. La capacidad de generaci´on el´ectrica total es suficiente para satisfacer la demanda energ´etica proyectada para el 2050
    model.addConstr(quicksum((x[l, t] * gen_l[l]) for l in L for t in T) >= req)

    #2. Todos lo proyectos deben terminarse a mas tardar en diciembre de 2049
    model.addConstrs(x[l, t] + plazo_l[l] <= 50 for l in L for t in T)
    model.addConstrs(w[n, t] + plazo_n[n] <= 50 for n in N for t in T)

    #3. Una empresa solo puede desarrollar tantos proyectos paralelamente como le permite su capacidad.
    model.addConstrs(quicksum(y[l, t] * emp_l[l, e] for l in L) + quicksum(z[n, t] * emp_n[n, e] for n in N) <= cap for e in E for t in T)

    #4. No pueden realizarse 2 proyectos en la misma ubicaci´on. N´otese que esto evita que un proyecto se construya 2 veces
    model.addConstrs(quicksum(x[l, t] * ubi_l[l, p] for l in L for t in T) <= 1 for p in P)
    model.addConstrs(quicksum(w[n, t] * ubi_n[n, p] for n in N for t in T) <= 1 for p in P)

    #5. Para hacer un proyecto de transmisión debe haber uno de generación asociado
    model.addConstrs(quicksum(x[l, t] * ubi_l[l, p] for l in L for t in T) <= quicksum(w[n, t] * ubi_n[n, p] for n in N for t in T) + quicksum(ubi_n[n_prima, p] for n_prima in N) for p in P)

    #6. Comportamiento de yℓ,t y de z
    model.addConstrs(x[l, t] <= y[l, t + t_prima] for l in L for t in T for t_prima in range(plazo_g[l]) if t + t_prima <= T[-1]) #revisar lo del if t + t_prima
    model.addConstrs(quicksum(y[l, t] for t in T) == quicksum(x[l, t] * plazo_g[l] for t in T) for l in L)

    model.addConstrs(w[n, t] <= z[n, t + t_prima] for n in N for t in range(T) for t_prima in range(plazo_n[n]) if t + t_prima < T) #revisar lo del if t + t_prima
    model.addConstrs(quicksum(z[n, t] for t in range(T)) == quicksum(w[n, t] * plazo_n[n] for t in range(T)) for n in N)  #falot el para todo t en modelación?

    #7. No construir más proyectos de cierta tecnología que los que te permite la regi´on
    model.addConstrs(quicksum(x[l, t] * tec[l, g] * ubi_g[l, p] for l in L for t in range(T) for p in P) <= max[r, g] for r in R for g in G)

    #8. No superar la capacidad de transmisión de cada línea
    model.addConstrs(quicksum(w[n, t] * trans1[n] * ubi_n[n, p] for t in range(T) for p in range(P)) >= quicksum(gen1[l] * ubi_g[l, p] for l in range(L) for p in range(P)) for n in N)

    #Función objetivo
    #¬ model.setObjective(quicksum(costo_g[l, t] * x[l, t] for l in L for t in T) + quicksum(w[n, t] * costo_g[n, t] for n in N for t in T), GRB.MINIMIZE)
    model.setObjective(quicksum(costo_g[l, t] * x[l, t] for l in L for t in range(T)) + quicksum(w[n, t] * costo_n[n, t] for n in N for t in range(T)), GRB.MINIMIZE)
    
    model.update()
    model.optimize()

    if model.status == GRB.OPTIMAL: return model

model = modelo()

#%%

model = modelo()

#%%
#with open("vars_que_valen_1.txt", "w") as file:
#    for a in model.getVars():
#        if int(a.x) != 0:
#            print(f"{a.VarName}", file=file)
