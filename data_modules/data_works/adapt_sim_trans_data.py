#from collections import namedtuple
#from random import randint


#RegionNum = {

#    'Región de Tarapacá' : 1,
#    'Región de Antofagasta' : 2,
#    'Región de Atacama' : 3,
#    'Región de Coquimbo' : 4,
#    'Región de Valparaíso' : 5,
#    'Región del Libertador Gral. Bernardo O’Higgins' : 6,
#    'Región del Maule' : 7,
#    'Región del Biobío' : 8,
#    'Región de La Araucanía' : 9,
#    'Región de Los Lagos' : 10,
#    'Región Aisén del Gral.Carlos Ibáñez del Campo' : 11,
#    'Región de Magallanes y de la Antártica Chilena' : 12,
#    'Región Metropolitana de Santiago' : 13,
#    'Región de Los Ríos' : 14,
#    'Región de Arica y Parinacota' : 15,
#    'Región de Ñuble' : 16

#    }


##with open("stuff.txt", "r", encoding="utf-8") as file:
##    E = set(map(lambda x : x.strip(), file.readlines()))


#RegistroUsable = namedtuple('Reducido', ['Region', 'Comuna', 'Titular', 'Nombre', 'Tecnologia', 'Inversion_MMUS', 'Capacidad_MW', 'Posicion', 'Plazo'])

#with open("data_modules/sim_data/gen_data_simulados_2800(2).csv", "r", encoding="utf-8") as file:
#    format = file.readline().strip().split(";")
#    format[-1] = format[-1].replace(",", "")
#    print("Formato de los datos completos:")
#    for f in format:
#        print(f)
#    print()
#    data = file.readlines()
#    formated_full_data = set()
#    cont = 1
#    for d in data:
#        cont += 1
#        d = d.strip().replace("\"", "").replace("\\", "").split(";")
#        register = RegistroUsable(*(d[:7]), RegionNum[d[0]] * randint(1, 50), d[-2])
#        formated_full_data.add(register)


#with open("data_modules/data/usable_gen_data_sim_wh.csv", "w", encoding="utf-8") as file:
#    print('Region', 'Comuna', 'Titular', 'Nombre', 'Tecnologia', 'Inversion_MUF', 'Capacidad_MW', 'Posicion', 'Plazo', sep =";", file=file)
#    for f in formated_full_data:
#        print(*(f), sep=";", file=file)

#with open("data_modules/data/usable_gen_data_sim.csv", "w", encoding="utf-8") as file:
#    for f in formated_full_data:
#        print(*(f), sep=";", file=file)