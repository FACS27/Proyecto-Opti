from collections import namedtuple, defaultdict

ProyectoGen = namedtuple('ProyectoGen', ['Id', 'Region', 'Comuna', 'Titular', 'Nombre', 'Tecnologia', 'Inversion_MUF', 'Capacidad_MW', 'Posicion'])
proyectos_g = dict()

ProyectoTrans = namedtuple('ProyectoTrans', ['Id', 'Nombre', 'Titular', 'Region', 'Comuna', 'Inversion_MUF', 'Capacidad_MVA', 'Plazo_Semestres', 'Posicion'])
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

with open("data_modules/data/gen_data_real.csv", "r", encoding="utf-8") as file:
    lines = [line.strip().split(";") for line in file.readlines()]
    cont = 0
    for l in lines[1:]:
        new_proyecto = ProyectoGen(cont, *l)

        L.add(new_proyecto.Id)
        E.add(new_proyecto.Titular)
        R.add(new_proyecto.Region)
        P.add(int(new_proyecto.Posicion))

        proyectos_g[new_proyecto.Id] = new_proyecto
        cont += 1

#with open("data_modules_data/data/gen_data_real.csv", "r", encoding="utf-8") as file:
#    lines = [line.strip().split(";") for line in file.readlines()]
#    cont = 0
#    for l in lines:
#        new_proyecto = ProyectoTrans(cont, *l)

#        N.add(new_proyecto.Id)
#        E.add(new_proyecto.Titular)
#        R.add(new_proyecto.Region)
#        P.add(new_proyecto.Posicion)

#        proyectos_t[new_proyecto.Id] = new_proyecto
#        cont += 1

#TODO 
#! Tenemos que definir como manejamos los costos respecto al tiempo
#Costo en UF de realizar el proyecto l del dia t
costo_g = {l : float(proyectos_g[l].Inversion_MUF) for l in L}


#TODO 
#Tiempo en semestres que el proyecto ℓ estar´ıa terminado desde el mes en que se inició
plazo_g = {l : 1 for l in L}

#TODO 
#Capacidad de generaci´on el´ectrica del proyecto ℓ en MW
gen1 = {l : float(proyectos_g[l].Capacidad_MW) for l in L}

#1 Si el proyecto ℓ es propuesto por la empresa e
emp_g = {(l, e) : 1 if proyectos_g[l].Titular == e else 0 for l in L for e in E}

#TODO 
#1 Si el proyecto ℓ esta ubicado en la posici´on p
ubi_g = {(l, p) : 1 if proyectos_g[l].Posicion == p else 0 for p in P for l in L}

#1 Si el proyecto ℓ utiliza la tecnolog´ıa de generaci´on g
#! Debido a la cantidad de proyectos que tienen 2 tecnologias
#! Voy a asumir que un proyecto puede usar mas de una tecnologia
tec = {(l, g) : 1 if g in proyectos_g[l].Tecnologia else 0 for l in L for g in G}

#TODO 
# Cantidad de proyectos que puede desarrollar la empresa e en cada semestre.
cap = 1

#Capacidad de generaci´on el´ectrica requerida en MW para cumplir la demanda en el 2050
#TODO 
req = 32350

#TODO 
#Cantidad m´axima de proyectos que utilizan la tecnolog´ıa g en la regi´on r.
max = {(r, g) : float("inf") for r in R for g in G}
#30 solar, 5 hidro, 15 eólico

#Costo en UF de realizar el proyecto n en el semestre t
costo_n = {n: float(proyectos_t[n].Inversion_MUF) for n in N}

#Tiempo en semestres que el proyecto n estar´ıa terminado desde el semestre en que se inició
plazo_n = {n: int(proyectos_t[n].Plazo_Semestres) for n in N}

#Capacidad de transmisi´on del proyecto n en MW
trans1 = {n: int(proyectos_t[n].Capacidad_MVA) for n in N}

#1 Si el proyecto n es propuesto por la empresa e
emp_n = {(n, e): 1 if proyectos_t[n].Titular == e else 0 for n in N for e in E}

#1 Si el proyecto n esta ubicado en la posici´on p
ubi_n = {n: proyectos_t[n].Posicion for n in N}
