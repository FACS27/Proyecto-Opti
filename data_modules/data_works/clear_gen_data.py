from collections import namedtuple
from functools import reduce
from random import randint


#* Este codigo es una verguenza
#* pero funciona


#? Data from: https://comisionenergia-my.sharepoint.com/:x:/g/personal/infoestadistica_cne_cl/EdW-oYIWUoVPjEXDK8ulXbUBG1OexzpBL4eR5wZcF_Jt9g


#? formato datos completos
#? region_nombre;region_cod;comuna;titular_proyecto;nombre_proyecto;tipo_proyecto;categoria_electrica;tipo_tecnologia;combustible;inversion_mmus;fecha_ingreso;categoria_seia;letra_seia;ficha;mapa;latitud;longitud;longitud_linea_km;num_rca;fecha_rca;tension_kv;capacidad_mw;estado_seia;almacenamiento

def isfloat(string):
    #Esto deberia ser ilegal
    try:
        float(string)
        return True
    except ValueError:
        return False

def conyunction(x):
    return bool(reduce(lambda a, b: a and b, x))

Regiones = set()

PlazosTec = {

    "Solar":        (2, 5),
    "Hidro":        (2, 6),
    "Eólica":       (8, 16),
    "Geotérmica":   (6, 10),
    "Eólica-Solar": (8, 16),
    "Hidro-Solar":  (2, 6),

    }


def simplify_tech(tech):
    Solar = ("Solar Fotovoltaica", "Concentración Solar de Potencia", "csp-solar fotovoltaico", "solar fotovoltaico y solar csp")
    Hidro = ("Hidráulica de Embalse", "Hidráulica de Pasada", "bombeo hidráulico", "Mini Hidráulica de Pasada", "hidroeléctrica < 20 mw", "hidro  > 20 mw", "ch > 20 mw")
    Eolica = ("Eólica")
    Geotermica = ("Geotérmica")
    Eolico_Solar = ("eólico-solar fotovoltaico")
    Hidro_Solar = ("hidro-solar fotovoltaio")
    if tech in Solar: return "Solar"
    elif tech in Hidro: return "Hidro"
    elif tech in Eolica: return "Eólica"
    elif tech in Geotermica: return "Geotérmica"
    elif tech in Eolico_Solar: return "Eólica-Solar"
    elif tech in Hidro_Solar: return "Hidro-Solar"
    else: return False


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
        d = d.strip().replace("\"", "").replace("\\", "").split(";")
        try:
            if d[0] != "Interregional":
                Regiones.add(d[0])
                register = RegistroCompleto(*d)
                formated_full_data.add(register)
        except Exception as e: #Ni ahi con adaptar los datos que estan mal subidos
            print(f"Algo salio mal en la linea {cont}") 
    Regiones = tuple(Regiones)

formated_reduced_data = set()
RegistroReducido = namedtuple('Reducido', ['Region', 'Comuna', 'Titular', 'Nombre', 'Tecnologia', 'Inversion_MMUS', 'Capacidad_MW', 'Posicion', 'Plazo'])

#? Se queda solo con las energias limpias
data_ernc = set(filter(lambda x: x.categoria_electrica in ["ERNC", "ER", "Hidroeléctrica convencional", "Renovable convencional"], formated_full_data))

#? Se queda solo con los datos que interesan
semi_reduced_data = set(map(lambda x: (x.region_nombre, x.region_cod, x.comuna, x.titular_proyecto, x.nombre_proyecto, simplify_tech(x.tipo_tecnologia), x.inversion_mmus.replace(",", "."), x.capacidad_mw.replace(",", ".")), data_ernc))

#? Se queda solo con los datos que tienen todos los campos completos
more_reduced_data = set(filter(lambda x : conyunction(x), semi_reduced_data))

even_more_reduced_data = set()

for s in more_reduced_data:
    posicion = randint(1, 50) * int(s[1])
    plazo = randint(*(PlazosTec[s[5]]))
    register = RegistroReducido(s[0], *(s[2:]), posicion, plazo)
    #print(register)
    if isfloat(register.Capacidad_MW) and register.Capacidad_MW != "0.0" and float(register.Inversion_MMUS) > 0:
        formated_reduced_data.add(register)

print(len(formated_reduced_data))


with open("data_modules/data/gen_data_real_wh.csv", "w", encoding="utf-8") as file:
    print('Region', 'Comuna', 'Titular', 'Nombre', 'Tecnologia', 'Inversion_MMUS', 'Capacidad_MW', 'Posicion', 'Plazo', sep =";", file=file)
    for f in formated_reduced_data:
        print(*(f), sep=";", file=file)

with open("data_modules/data/gen_data_real.csv", "w", encoding="utf-8") as file:
    for f in formated_reduced_data:
        print(*(f), sep=";", file=file)
