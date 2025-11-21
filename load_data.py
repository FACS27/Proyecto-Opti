from collections import namedtuple
from random import randint

ProyectoGen = namedtuple('ProyectoGen', ['Id', 'Region', 'Comuna', 'Titular', 'Nombre', 'Tecnologia', 'Inversion_MUF', 'Capacidad_MW', 'Posicion', 'Plazo'])
proyectos_g = dict()

ProyectoTrans = namedtuple('ProyectoTrans', ['Id', 'Region', 'Comuna', 'Titular', 'Nombre', 'Inversion_MUF', 'Posicion', 'Plazo'])
proyectos_t = dict()


#Horizonte de planificaci´on T en semestres
T = tuple( t for t in range(50) )

#Conjunto de proyectos de generaci´on postulados a licitaciones. ℓ ∈ L
L = set()

#Conjunto de proyectos de transmisión postulados a licitaciones
N = set()

#Tecnologías de generación de energía eléctrica ERNC
G = {"Solar", "Hidro", "Eólica"}

#Empresas o personas naturales que presentaron al menos un proyecto
E = set()

#Posiciones en las que se puede construir una planta de generación eléctrica y/o una linea de transmisión
P = set()

#Regiones de Chile que son a su vez subconjuntos de posiciones. r ∈ R ∧ r ⊆ P
R = set()


with open("data_modules/data/gen_data_real_wh.csv", "r", encoding="utf-8") as file:
    lines = [line.strip().split(";") for line in file.readlines()]
    cont = 0
    for l in lines[1:]:
        new_proyecto = ProyectoGen(cont, *l)

        L.add(new_proyecto.Id)
        E.add(new_proyecto.Titular)
        R.add(new_proyecto.Region)
        P.add(new_proyecto.Posicion)

        proyectos_g[new_proyecto.Id] = new_proyecto
        cont += 1

with open("data_modules/data/trans_data_real_wh.csv", "r", encoding="utf-8") as file:
    lines = [line.strip().split(";") for line in file.readlines()]
    cont = 0
    for l in lines[1:]:
        new_proyecto = ProyectoTrans(cont, *l)

        N.add(new_proyecto.Id)
        E.add(new_proyecto.Titular)
        R.add(new_proyecto.Region)
        P.add(new_proyecto.Posicion)

        proyectos_t[new_proyecto.Id] = new_proyecto
        cont += 1


#* PARAMETROS GENERACION
#* ==============================================


#Costo en UF de realizar el proyecto l del dia t
costo_l = {l : float(proyectos_g[l].Inversion_MUF) for l in L}

#Capacidad de generaci´on el´ectrica del proyecto ℓ en MW
gen_l = {l : float(proyectos_g[l].Capacidad_MW) for l in L}

#1 Si el proyecto ℓ es propuesto por la empresa e
emp_l = {(l, e) : 1 if proyectos_g[l].Titular == e else 0 for l in L for e in E}

#1 Si el proyecto ℓ esta ubicado en la posici´on p
ubi_l = {(l, p) : 1 if proyectos_g[l].Posicion == p else 0 for l in L for p in P}

#1 Si el proyecto ℓ utiliza la tecnolog´ıa de generaci´on g (puede ocupar más de una)
tec_l = {(l, g) : 1 if g in proyectos_g[l].Tecnologia else 0 for l in L for g in G}

#Tiempo en semestres que el proyecto ℓ estar´ıa terminado desde el mes en que se inició
plazo_l =  {l: int(proyectos_g[l].Plazo) for l in L}


    #L_por_empresa = {e: [] for e in E}
    #N_por_empresa = {e: [] for e in E}

    #for e in E:
    #    for l in L:
    #        if emp_l.get((l, e), 0) == 1:
    #            L_por_empresa[e].append(l)
    #            break 
    #    for n in N:
    #        if emp_n.get((n, e), 0) == 1:
    #            N_por_empresa[e].append(n)
    #            break 

#* PARAMETROS TRANSMISION
#* ==============================================

#Costo en UF de realizar el proyecto n en el semestre t
costo_n = {n: float(proyectos_t[n].Inversion_MUF) for n in N}

#Tiempo en semestres que el proyecto n estar´ıa terminado desde el semestre en que se inició
plazo_n = {n: int(proyectos_t[n].Plazo) for n in N}

#1 Si el proyecto n es propuesto por la empresa e
emp_n = {(n, e): 1 if proyectos_t[n].Titular == e else 0 for n in N for e in E}

#1 Si el proyecto n esta ubicado en la posici´on p
ubi_n = {(n, p): 1 if proyectos_t[n].Posicion == p else 0 for n in N for p in P}

#* PARAMETROS GENERALES
#* ==============================================

# Cantidad de proyectos que puede desarrollar la empresa e en cada semestre.
cap_e = {e : randint(1, 5) for e in E}

#Capacidad de generaci´on el´ectrica requerida en MW para cumplir la demanda en el 2050
REQ = 32350

#Cantidad m´axima de proyectos que utilizan la tecnolog´ıa g en la regi´on r.
max_r = {(r, g) : float("inf") for r in R for g in G}
#? Esto lo mantendré tal cual

#i = 0
#j = 0
#k = 0
#max_t = {}
#for r in R:
#    for g in G:
#        if g == "Solar":
#            max_t[r, g] = 30 - i
#        elif g == "Hidro":
#            max_t[r, g] = 5 + j
#        else:
#            max_t[r, g] = 15 + k
#    i+=2
#    j+=1
#    k+=1


L_r = {r : set(x.Id for x in filter(lambda x : x.Region == r, proyectos_g.values())) for r in R}

L_e = {e : set(x.Id for x in filter(lambda x : x.Titular == e, proyectos_g.values())) for e in E}
N_e = {e : set(x.Id for x in filter(lambda x : x.Titular == e, proyectos_t.values())) for e in E}


for l in L_r:
    print(l)