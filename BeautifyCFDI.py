import argparse


def BeautifyCFDI(targetFiles = None, targetDir = None, configFile = "./config.json"):
    pass

def parseArguments():
    """Esta función analiza los argumentos proporcionados por el usuario desde la línea de comandos"""

    # Creamos una instancia de ArgumentParser
    main_parser = argparse.ArgumentParser()
    # Definimos una descripción del porgrama
    main_parser.description = "BeautifyCFDI genera representaciones impresas de CFDI que son esteticamente aceptables."

    #Agregamos argumentos
    #fileDirGroup es un conjunto de argumentos mutuamente exclusivos (o archivo o directorio)
    fileDirGroup = main_parser.add_argument_group("Argumentos posicionales")
    fileDirGroup.add_argument("target", nargs = 1, type = str, 
        help = "Ruta del archivo XML con el CFDI. Si el usuario suministra un directorio, entonces todos los XML con CFDI válidos serán usados.")
    #optionsGroup
    optGroup = main_parser.add_argument_group("Opciones")
    optGroup.add_argument("-c", "--config", nargs = 1, type = str, default = './config.json',
        help = "Ruta del archivo de configuración. Por default = ./config.json")

    main_parser.parse_args()


# El código se ejecuta directamente
if __name__ == "__main__":
    parseArguments()

