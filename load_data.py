from collections import namedtuple, defaultdict

Proyecto = namedtuple('Proyecto', ['Id', 'Region', 'Comuna', 'Titular', 'Nombre', 'Tecnologia', 'Inversion_MMUS', 'Capacidad_MW', "Latitud", "Longitud"])
proyectos = dict()


#! Regiones = dict()


#Horizonte de planificaci´on T en semestres
T = tuple( t for t in range(50) )

#Conjunto de proyectos de generaci´on postulados a licitaciones. ℓ ∈ L
L = set()

#Tecnologías de generación de energía eléctrica ERNC
G = {"Solar", "Hidro", "Eólica", "Geotérmica"}

#Empresas o personas naturales que presentaron al menos un proyecto
E = set()

#Posiciones en las que se puede construir una planta de generación eléctrica y/o una linea de transmisión
P = set()

#Regiones de Chile que son a su vez subconjuntos de posiciones. r ∈ R ∧ r ⊆ P
R = set()


with open("data_modules/data/gen_data_reales.csv", "r", encoding="utf-8") as file:
    lines = file.readlines().strip().split(";")
    cont = 0
    for l in lines:
        new_proyecto = Proyecto(cont, *l)

        L.add(new_proyecto.Id)
        G.add(new_proyecto.Tecnologia)
        E.add(new_proyecto.Titular)

        #! REVISAR LAS POSICIONES, REGIONES Y COMUNAS
        #! P 
        #! R

        proyectos[new_proyecto.Id] = new_proyecto
        cont += 1



#! Tenemos que definir como manejamos los costos respecto al tiempo
#Costo en UF de realizar el proyecto l del dia t
costo = dict()



#Tiempo en semestres que el proyecto ℓ estar´ıa terminado desde el mes en que se inició
plazo = dict()

#Capacidad de generaci´on el´ectrica del proyecto ℓ en MW
gen1 = {l : proyectos[l].Capacidad_MW for l in L}

#Capacidad de generaci´on el´ectrica de los proyectos ℓ′ preexistentes en MW
gen2 = dict()

#1 Si el proyecto ℓ es propuesto por la empresa e
emp = {(l, e) : 1 if proyectos[l].Titular == e else 0 for l in L for e in E}

#1 Si el proyecto ℓ esta ubicado en la posici´on p
ubi = dict()

#1 Si el proyecto ℓ utiliza la tecnolog´ıa de generaci´on g
#! Debido a la cantidad de proyectos que tienen 2 tecnologias
#! Voy a asumir que un proyecto puede usar mas de una tecnologia
tec = {(l, g) : 1 if g in proyectos[l].Tecnologia else 0 for l in L for g in G}

# Cantidad de proyectos que puede desarrollar la empresa e en cada semestre.
cap = dict()

#Capacidad de generaci´on el´ectrica requerida en MW para cumplir la demanda en el 2050
req = 0

#Cantidad m´axima de proyectos que utilizan la tecnolog´ıa g en la regi´on r.
max = int("inf")

