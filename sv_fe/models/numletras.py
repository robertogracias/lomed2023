def numero_to_letras(numero):
    """
    Funciones para convertir las letas a numeros
    """
    indicador = [("",""),("MIL","MIL"),("MILLON","MILLONES"),("MIL","MIL"),("BILLON","BILLONES")]
    entero = int(numero)
    decimal = int(round((numero - entero)*100))
    #print 'decimal : ',decimal 
    contador = 0
    numero_letras = ""
    _logger.info('ENTERO:'+str(entero))
    while entero >0:
        a = entero % 1000
        if contador == 0:
            en_letras = convierte_cifra(a,1).strip()
            _logger.info('letras 1:'+en_letras)
        else :
            en_letras = convierte_cifra(a,0).strip()
            _logger.info('letras 2:'+en_letras)
        if a==0:
            numero_letras = en_letras+" "+numero_letras
            _logger.info('letras 3:'+numero_letras)
        elif a==1:
            if contador in (1,3):
                numero_letras = indicador[contador][0]+" "+numero_letras
                _logger.info('letras 4:'+numero_letras)
            else:
                numero_letras = en_letras+" "+indicador[contador][0]+" "+numero_letras
                _logger.info('letras 5:'+numero_letras)
        else:
            numero_letras = en_letras+" "+indicador[contador][1]+" "+numero_letras
            _logger.info('letras 6:'+numero_letras)
        numero_letras = numero_letras.strip()
        contador = contador + 1
        entero = int(entero / 1000)
    numero_letras = numero_letras+" CON " + str(decimal) +"/100"
    return numero_letras
 

def convierte_cifra(numero,sw):
    lista_centana = ["",("CIEN","CIENTO"),"DOSCIENTOS","TRESCIENTOS","CUATROCIENTOS","QUINIENTOS","SEISCIENTOS","SETECIENTOS","OCHOCIENTOS","NOVECIENTOS"]
    lista_decena = ["",("DIEZ","ONCE","DOCE","TRECE","CATORCE","QUINCE","DIECISEIS","DIECISIETE","DIECIOCHO","DIECINUEVE"),
                    ("VEINTE","VEINTIUNO","VEINTIDOS","VEINTITRES","VEINTICUATRO","VEINTICINCO","VEINTISEIS","VEINTISIETE","VEINTIOCHO","VEINTINUEVE")
                    ,("TREINTA","TREINTA Y "),("CUARENTA" , "CUARENTA Y "),
                    ("CINCUENTA" , "CINCUENTA Y "),("SESENTA" , "SESENTA Y "),
                    ("SETENTA" , "SETENTA Y "),("OCHENTA" , "OCHENTA Y "),
                    ("NOVENTA" , "NOVENTA Y ")
                ]
    lista_unidad = ["",("UN" , "UNO"),"DOS","TRES","CUATRO","CINCO","SEIS","SIETE","OCHO","NUEVE"]
    centena = int (numero / 100)
    decena = int((numero -(centena * 100))/10)
    unidad = int(numero - (centena * 100 + decena * 10))
    #print "centena: ",centena, "decena: ",decena,'unidad: ',unidad
    texto_centena = ""
    texto_decena = ""
    texto_unidad = ""
    #Validad las centenas
    texto_centena = lista_centana[centena]
    if centena == 1:
        if (decena + unidad)!=0:
            texto_centena = texto_centena[1]
        else :
            texto_centena = texto_centena[0]
    #Valida las decenas
    texto_decena = lista_decena[decena]
    if ((decena == 1) or (decena == 2)):
         texto_decena = texto_decena[unidad]
    elif decena > 2 :
        if unidad != 0 :
            texto_decena = texto_decena[1]
        else:
            texto_decena = texto_decena[0]
    #Validar las unidades
    #print "texto_unidad: ",texto_unidad
    if decena != 1:
        texto_unidad = lista_unidad[unidad]
        if unidad == 1:
            texto_unidad = texto_unidad[sw]
    return "%s %s %s" %(texto_centena,texto_decena,texto_unidad)


def calculo_letras(campo):
    cadena = list(campo)
    a = []
    for record in cadena: 
        if record=='0':
            a.append('cero')
        if record=='1':
            a.append('uno')
        if record=='2':
            a.append('dos')
        if record=='3':
            a.append('tres')
        if record=='4':
            a.append('cuatro')
        if record=='5':
            a.append('cinco')
        if record=='6':
            a.append('seis')
        if record=='7':
            a.append('siete')
        if record=='8':
            a.append('ocho')
        if record=='9':
            a.append('nueve')
        if record=='-':
            a.append('-')
            
    str1  = ' '.join(a)
    return str1