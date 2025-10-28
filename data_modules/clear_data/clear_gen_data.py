from collections import namedtuple
from functools import reduce


#* Este codigo es una verguenza
#* pero funciona


#? Data from: https://comisionenergia-my.sharepoint.com/:x:/g/personal/infoestadistica_cne_cl/EdW-oYIWUoVPjEXDK8ulXbUBG1OexzpBL4eR5wZcF_Jt9g


#? formato datos completos
#? region_nombre;region_cod;comuna;titular_proyecto;nombre_proyecto;tipo_proyecto;categoria_electrica;tipo_tecnologia;combustible;inversion_mmus;fecha_ingreso;categoria_seia;letra_seia;ficha;mapa;latitud;longitud;longitud_linea_km;num_rca;fecha_rca;tension_kv;capacidad_mw;estado_seia;almacenamiento


def conyunction(x):
    return bool(reduce(lambda a, b: a and b, x))


with open("data_modules/bloated_data/bloated_gen_" \
"data.csv", "r", encoding="utf-8") as file:
    format = file.readline().strip().split(";")
    format[-1] = format[-1].replace(",", "")
    print("Formato de los datos completos:")
    for f in format:
        print(f)
    print()
    RegistroCompleto = namedtuple('Completo', format)
    data = file.readlines()
    formated_full_data = set()
    cont = 1
    for d in data:
        cont += 1
        d = d.strip().split(";")
        try:
            if d[0] != "Interregional":
                register = RegistroCompleto(*d)
                formated_full_data.add(register)
        except Exception as e: #Ni ahi con adaptar los datos que estan mal subidos
            print(f"Algo salio mal en la linea {cont}") 


#tecnologias = set()
#categorias = set()
#tipos_proyecto = set()
#for f in formated_full_data:
#    print()
#    if f.tipo_proyecto not in tipos_proyecto:
#        tipos_proyecto.add(f.tipo_proyecto)
#    if f.tipo_tecnologia not in tecnologias:
#        tecnologias.add(f.tipo_tecnologia)
#    if f.categoria_electrica not in categorias:
#        categorias.add(f.categoria_electrica)

#print("Tecnologias encontradas:")
#for t in tecnologias:
#    print(t)
#print()
#print("Categorias encontradas:")
#for c in categorias:
#    print(c)    
#print()
#print("Tipos de proyecto encontrados:")
#for tp in tipos_proyecto:
#    print(tp)

#transmision = set(filter(lambda x: x.tipo_proyecto == "Transmisión", formated_full_data))


formated_reduced_data = set()
RegistroReducido = namedtuple('Reducido', ['Region', 'Comuna', 'Titular', 'Nombre', 'Tecnologia', 'Inversion_MMUS', 'Capacidad_MW', "Latitud", "Longitud"])

#? Se queda solo con las energias limpias
data_ernc = set(filter(lambda x: x.categoria_electrica in ["ERNC", "ER", "Hidroeléctrica convencional", "Renovable convencional"], formated_full_data))

#? Se queda solo con los datos que interesan
semi_reduced_data = set(map(lambda x: (x.region_nombre, x.comuna, x.titular_proyecto, x.nombre_proyecto, x.tipo_tecnologia, x.inversion_mmus, x.capacidad_mw, x.latitud, x.longitud), formated_full_data))

#? Se queda solo con los datos que tienen todos los campos completos
more_reduced_data = set(filter(lambda x : conyunction(x), semi_reduced_data))
 

for s in more_reduced_data:
    register = RegistroReducido(*s)
    formated_reduced_data.add(register)

print(len(formated_reduced_data))


with open("data_modules/data/gen_data_reales.csv", "w", encoding="utf-8") as file:
    for f in formated_reduced_data:
        print(f.Region, f.Comuna, f.Titular, f.Nombre, f.Tecnologia, f.Inversion_MMUS, f.Capacidad_MW, f.Latitud, f.Longitud, sep=";", file=file)

