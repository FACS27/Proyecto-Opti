from collections import namedtuple
from functools import reduce


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


def simplify_tech(tech):
    Solar = ("Solar Fotovoltaica", "Concentración Solar de Potencia", "csp-solar fotovoltaico", "solar fotovoltaico y solar csp")
    Hidro = ("Hidráulica de Embalse", "Hidráulica de Pasada", "bombeo hidráulico", "Mini Hidráulica de Pasada", "hidroeléctrica < 20 mw", "hidro  > 20 mw", "ch > 20 mw")
    Eolica = ("Eólica")
    Geotermica = ("Geotérmica")
    Eolico_Solar = ("eólico-solar fotovoltaico")
    Hidro_Solar = ("hidro-solar fotovoltaio")
    if tech in Solar: return "Solar Fotovoltaica"
    elif tech in Hidro: return "Hidráulica"
    elif tech in Eolica: return "Eólica"
    elif tech in Geotermica: return "Geotérmica"
    elif tech in Eolico_Solar: return "Eólico-Solar"
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
        d = d.strip().split(";")
        try:
            if d[0] != "Interregional":
                register = RegistroCompleto(*d)
                formated_full_data.add(register)
        except Exception as e: #Ni ahi con adaptar los datos que estan mal subidos
            print(f"Algo salio mal en la linea {cont}") 


formated_reduced_data = set()
RegistroReducido = namedtuple('Reducido', ['Region', 'Comuna', 'Titular', 'Nombre', 'Tecnologia', 'Inversion_MMUS', 'Capacidad_MW', "Latitud", "Longitud"])

#? Se queda solo con las energias limpias
data_ernc = set(filter(lambda x: x.categoria_electrica in ["ERNC", "ER", "Hidroeléctrica convencional", "Renovable convencional"], formated_full_data))

#? Se queda solo con los datos que interesan
semi_reduced_data = set(map(lambda x: (x.region_nombre, x.comuna, x.titular_proyecto, x.nombre_proyecto, simplify_tech(x.tipo_tecnologia), x.inversion_mmus.replace(",", "."), x.capacidad_mw.replace(",", "."), x.latitud.replace(",", "."), x.longitud.replace(",", ".")), data_ernc))

#? Se queda solo con los datos que tienen todos los campos completos
more_reduced_data = set(filter(lambda x : conyunction(x), semi_reduced_data))

even_more_reduced_data = set()

for s in more_reduced_data:
    register = RegistroReducido(*s)
    if isfloat(register.Capacidad_MW):
        formated_reduced_data.add(register)

print(len(formated_reduced_data))


with open("data_modules/data/gen_data_reales_w_h.csv", "w", encoding="utf-8") as file:
    print('Region', 'Comuna', 'Titular', 'Nombre', 'Tecnologia', 'Inversion_MMUS', 'Capacidad_MW', "Latitud", "Longitud", sep =";", file=file)
    for f in formated_reduced_data:
        print(f.Region, f.Comuna, f.Titular, f.Nombre, f.Tecnologia, f.Inversion_MMUS, f.Capacidad_MW, f.Latitud, f.Longitud, sep=";", file=file)

with open("data_modules/data/gen_data_reales.csv", "w", encoding="utf-8") as file:
    for f in formated_reduced_data:
        print(f.Region, f.Comuna, f.Titular, f.Nombre, f.Tecnologia, f.Inversion_MMUS, f.Capacidad_MW, f.Latitud, f.Longitud, sep=";", file=file)

