
import numpy as np
from gurobipy import Model, GRB, quicksum
from load_data import L, N, G, E, P, R, A, T, costo_g, plazo_g, gen1, gen2, emp_g, ubi_g, tec, cap, req, max, costo_n, plazo_n, trans1, trans2, emp_n, ubi_n

#TODO Revisar que todo esté bien indexado
#TODO Revisar datos para las fechas y costos
#TODO Buscar datos faltantes
#TODO Crear los arrays o diccionarios necesarios para los parámetros

#G Conjunto L listo
#G Conjunto G listo
#G Conjunto E listo


def modelo():

    model = Model("GeneracionElectrica")
    model.setParam('TimeLimit', 1800)

    x = model.addVars(L, T, vtype=GRB.BINARY, name="x")
    y = model.addVars(L, T, vtype=GRB.BINARY, name="y")
    w = model.addVars(N, T, vtype=GRB.BINARY, name="w")
    z = model.addVars(N, T, vtype=GRB.BINARY, name="z")

    #Restricciones

    #La capacidad de generaci´on el´ectrica total es suficiente para satisfacer la demanda energ´etica proyectada para el 2050
    model.addConstrs(quicksum(x[l, t] * gen1[l] for l in L for t in range(T) ) + quicksum(gen2[l_prima] for l_prima in A) >= req)

    #Todos lo proyectos deben terminarse a mas tardar en diciembre de 2049
    model.addConstrs(x[l, t] * t + plazo_g[l] <= 50 for l in L for t in range(T))

    #Una empresa solo puede desarrollar tantos proyectos paralelamente como le permite su capacidad.
    model.addConstrs(quicksum(y[l, t] * emp_g[l, e] for l in L) <= cap[e] for e in E for t in range(T))

    #No pueden realizarse 2 proyectos en la misma ubicaci´on. N´otese que esto evita que un proyecto se construya 2 veces
    model.addConstrs(quicksum(x[l, t] * ubi_g[l, p] for l in L for t in range(T)) <= 1 for p in P)

    #Comportamiento de yℓ,t
    model.addConstrs(x[l, t] <= y[l, t + t_prima] for l in L for t in range(T) for t_prima in range(plazo_g[l]) if t + t_prima < T) #revisar lo del if t + t_prima
    model.addConstrs(quicksum(y[l, t] for t in range(T)) == x[l, t] * plazo_g[l] for l in L for t in range(T))  #falot el para todo t en modelación?

    #No construir más proyectos que los que te permite la regi´on
    model.addConstrs(quicksum(x[l, t] * tec[l, g] * ubi_g[l, p] for l in L for t in range(T) for p in P) <= max[g, r] for g in G for r in R)

    #Función objetivo
    model.setObjective(quicksum(costo_g[l, t] * x[l, t] for l in L for t in range(T)) + quicksum(w[n, t] * costo_n[n, t] for n in N for t in range(T)), GRB.MINIMIZE)
    
    model.update()
    model.optimize()

    if model.status == GRB.OPTIMAL: return model

model = modelo()