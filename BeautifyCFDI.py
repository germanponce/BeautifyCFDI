from xml.dom import minidom
import argparse
import json
import os


def getCatalogoValue(cat: str, id: str, configDict: dict):

    # Buscar la categoría y el id especificado
    try:
        targetValue = configDict.get("catDict").get(cat).get(id)
    except Exception as e:
        raise ValueError("El archivo de configuración tiene un error: {0}".format(e))

    return targetValue


def getDatosEmisor(CFDI: minidom.Document, configDict: dict):

    # Obtenemos configuración del emisor
    try:
        configEmisor = configDict.get("userInfo")
    except Exception as e:
        raise ValueError("El archivo de configuración tiene un error: {0}".format(e))

    # Obtenemos la raiz del documento
    Comprobante = CFDI.getElementsByTagName("cfdi:Comprobante")[0]
    EmisorNode = Comprobante.getElementsByTagName("cfdi:Emisor")[0]

    # Creamos un diccionario con los datos del emisor
    emisor = dict()

    # Nombre, RFC, Regimen, Domicilio y Contacto de emisor
    NombreEmisor = EmisorNode.getAttribute("Nombre")
    RfcEmisor = EmisorNode.getAttribute("Rfc")
    RegimenEmisor = EmisorNode.getAttribute("RegimenFiscal")
    RegimenEmisor = "{0} - {1}".format(RegimenEmisor, getCatalogoValue("regimenFiscal", RegimenEmisor, configDict))
    DomicilioEmisor = ""
    ContactoEmisor = ""
    emisor.update(NombreEmisor = NombreEmisor)
    emisor.update(RfcEmisor = RfcEmisor)
    emisor.update(RegimenEmisor = RegimenEmisor)
    emisor.update(DomicilioEmisor = DomicilioEmisor)
    emisor.update(ContactoEmisor = ContactoEmisor)
    # Verificamos si el usuario quiere sobreescribir opciones
    if configEmisor.get("useDefault") is False:
        emisor.update(NombreEmisor = configEmisor["user"].get("nombre") )
        emisor.update(DomicilioEmisor = configEmisor["user"].get("domicilio") )
        emisor.update(ContactoEmisor = configEmisor["user"].get("contacto") )

    # Regresamos datos del emisor
    return emisor

def getDatosReceptor(CFDI: minidom.Document, configDict: dict):

    # Obtenemos configuración del Receptor
    try:
        configReceptor = configDict.get("clientesInfo")
    except Exception as e:
        raise ValueError("El archivo de configuración tiene un error: {0}".format(e))

    # Obtenemos la raiz del documento
    Comprobante = CFDI.getElementsByTagName("cfdi:Comprobante")[0]
    ReceptorNode = Comprobante.getElementsByTagName("cfdi:Receptor")[0]

    # Creamos un diccionario con los datos del Receptor
    receptor = dict()

    # Nombre, RFC, Regimen, Domicilio y Contacto de receptor
    NombreReceptor = ReceptorNode.getAttribute("Nombre")
    RfcReceptor = ReceptorNode.getAttribute("Rfc")
    UsoReceptor = ReceptorNode.getAttribute("UsoCFDI")
    UsoReceptor = "{0} - {1}".format(UsoReceptor, getCatalogoValue("usoCFDI", UsoReceptor, configDict))
    DomicilioReceptor = ""
    receptor.update(NombreReceptor = NombreReceptor)
    receptor.update(RfcReceptor = RfcReceptor)
    receptor.update(UsoReceptor = UsoReceptor)
    receptor.update(DomicilioReceptor = DomicilioReceptor)
    # Verificamos si el usuario quiere sobreescribir opciones
    if configReceptor.get("useDefault") is False:

        if configReceptor["clientesDict"].get(RfcReceptor, None) is None:
            print("\tNo se encontró información para el cliente con RFC {0}".format(RfcReceptor))
        else:
            NombreReceptor = configReceptor["clientesDict"].get(RfcReceptor, {}).get("nombre", "")
            DomicilioReceptor = configReceptor["clientesDict"].get(RfcReceptor, {}).get("domicilio", "")
            receptor.update(NombreReceptor = NombreReceptor)
            receptor.update(DomicilioReceptor = DomicilioReceptor)

    # Regresamos datos del receptor
    return receptor


def BeautifyCFDI(target = None, out = 'pdf', configPath = "./config.json"):

    # Verificamos argumento target
    target = os.fsencode(target)
    isTargetFile = os.path.isfile(target)
    isTargetDir = os.path.isdir(target)

    # Si es directorio
    if isTargetDir:
        targetFiles = os.listdir(target)
    elif isTargetFile:
        targetFiles = list()
        targetFiles.append(target)
    else:
        raise ValueError("El archivo o directorio especificado no existe")

    # Verificamos argumento out
    if out not in ["html", "docx", "pdf"]:
        raise ValueError("Formato desconocido en opcion 'out'!")

    # Abrimos configPath
    configPath = os.fsencode(configPath)
    try:
        with open(configPath, "r") as configFile:
            configFileContents = configFile.read()
            configDict = json.loads(configFileContents)
    except Exception as e:
        raise ValueError("Ocurrió un error al abrir el archivo de configuración especificado: {0}".format(e))

    # Quitar de targetFiles todos los archivos que no son xml
    targetFiles_foo = list()
    for i in range(len(targetFiles)):
        fileNameDecoded = os.fsdecode(targetFiles[i])
        if fileNameDecoded.endswith(".xml"):
            targetFiles_foo.append(targetFiles[i])

    targetFiles = targetFiles_foo

    if len(targetFiles) < 1:
        raise ValueError("El archivo especificado no tiene extensión xml. O bien, el directorio especificado no contiene algún xml")

    # Entrar al loop para procesar los CFDI
    for fileName in targetFiles:
        print("> Porcesando archivo {0}".format(fileName.decode("utf-8")))
        fileNameDecoded = os.fsdecode(fileName)

        # Abrimos el cfdi
        CFDI = minidom.parse(fileNameDecoded)

        # Extraemos datos del emisor
        emisor = getDatosEmisor(CFDI, configDict)
        #EXtraemos datos del receptor
        receptor = getDatosReceptor(CFDI, configDict)
        print(emisor)
        print(receptor)



def parseArguments():
    """Esta función analiza los argumentos proporcionados por el usuario desde la línea de comandos"""

    # Creamos una instancia de ArgumentParser
    main_parser = argparse.ArgumentParser()
    # Definimos una descripción del porgrama
    main_parser.description = "BeautifyCFDI: imprimibles estéticos de CFDIs."

    # Agregamos argumentos
    # fileDirGroup es un conjunto de argumentos mutuamente exclusivos (o archivo o directorio)
    fileDirGroup = main_parser.add_argument_group("Argumentos posicionales")
    fileDirGroup.add_argument("target", type = str,
                              help = "Ruta del archivo XML con el CFDI. Si el usuario suministra un directorio, entonces todos los XML con CFDI válidos serán usados.")
    # optionsGroup
    optGroup = main_parser.add_argument_group("Opciones")
    optGroup.add_argument("-c", "--config", type = str, default = './config.json', dest = "configFile",
                          help = "Ruta del archivo de configuración. Por default = ./config.json")
    optGroup.add_argument("-o", "--output", type = str, default = 'pdf', choices = ['pdf', 'html', 'docx'],
                          dest = "out", help = "Formato de salida. Por el momento, BeautifyCFDI soporta pdf, html y docx.")

    # Parseamos argumentos
    parsed_args = main_parser.parse_args()

    # Mandamos los argumentos a la función
    BeautifyCFDI(parsed_args.target, parsed_args.out, parsed_args.configFile)


# El código se ejecuta directamente
if __name__ == "__main__":
    parseArguments()
