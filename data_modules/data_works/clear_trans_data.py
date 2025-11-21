from collections import namedtuple
from functools import reduce
from random import randint


# Los datos son los mismos, pero estan filtrados para los proyectos de transmision, 
# hay un buen motivo para usar estos datos y no los otros

#* Este codigo es una verguenza
#* pero funciona


#? Data from: https://comisionenergia-my.sharepoint.com/:x:/g/personal/infoestadistica_cne_cl/EZV_eSBIzhBJmxgRzxYWYHUBJccNoR3x4gstLBSpfCjULA


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


Regiones = {}

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
                Regiones[d[1]] = d[0]
                register = RegistroCompleto(*d)
                formated_full_data.add(register)
        except Exception as e: #Ni ahi con adaptar los datos que estan mal subidos
            print(f"Algo salio mal en la linea {cont}") 



formated_reduced_data = set()
RegistroReducidoTrans = namedtuple('ReducidoTrans', ['Region', 'Comuna', 'Titular', 'Nombre', 'Inversion_MMUS', 'Posicion', 'Plazo'])

#? Se queda solo con las lineas de transmision
data_ernc = set(filter(lambda x: x.tipo_proyecto in ["Línea de transmisión eléctrica", "Subestación eléctrica"], formated_full_data))

##? Se queda solo con los datos que interesan
semi_reduced_data = set(map(lambda x: (x.region_nombre, x.region_cod, x.comuna, x.titular_proyecto, x.nombre_proyecto, x.inversion_mmus.replace(",", ".")), data_ernc))

##? Se queda solo con los datos que tienen todos los campos completos
more_reduced_data = set(filter(lambda x : conyunction(x), semi_reduced_data))


#Nuevas posiciones
for s in more_reduced_data:
    posicion = randint(1, 50) * int(s[1])
    plazo = randint(1, 10)
    register = RegistroReducidoTrans(s[0], *(s[2:]), posicion, plazo)
    #print(register)
    if float(register.Inversion_MMUS) > 0:
        formated_reduced_data.add(register)

print(len(formated_reduced_data))


with open("data_modules/data/trans_data_real_wh.csv", "w", encoding="utf-8") as file:
    print('Region', 'Comuna', 'Titular', 'Nombre', 'Inversion_MMUS', 'Posicion', 'Plazo', sep =";", file=file)
    for f in formated_reduced_data:
        print(*(f), sep=";", file=file)

with open("data_modules/data/trans_data_real.csv", "w", encoding="utf-8") as file:
    for f in formated_reduced_data:
        print(*(f), sep=";", file=file)
