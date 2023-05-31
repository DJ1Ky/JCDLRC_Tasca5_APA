'''

    Juan Camilo De Los Ríos

    Práctica 5:
   
    Lee el fichero WAVE ficEste, que debe contener una señal de audio estéreo, 
    y escribe el fichero ficMono, que debe incluir una señal monofónica.

'''

import struct 

def cod_2en1(uno, dos, /, *, numBits=16):
    
    return (uno << numBits) | dos + 2 ** (numBits - 1)

def dec_2en1(cod, /, *, numBits=16):
    ls
    mascara = (1 << numBits) - 1
    uno = (cod >> numBits)
    dos = (cod & mascara) - 2 ** (numBits - 1)
    return uno, dos

def bits2fmt(bitsPerSample):

    if bitsPerSample == 8:
        return 'b'
    elif bitsPerSample == 16:
        return 'h'
    elif bitsPerSample == 32:
        return 'i'
    else:
        raise ValueError('El número de bits debe ser 8, 16 o 32')


def leeWave(ficWave):

    with open(str(ficWave), 'rb') as fpWav: #abrimos el fichero
        formato = '<4sI4s4sIHHIIHH4sI' #formato de la cabecera
        buffer = fpWav.read(struct.calcsize(formato))#buffer con info de la cabecera
        (chunkID, chunkSize, format_, subcunkID, 
        subchunkSize, audioformat, numchannels, 
        samplerate, byterate, blockalign, bitspersample, 
        subchunk2id, subchunk2size) = struct.unpack(formato, buffer)

        if audioformat != 1: raise ValueError('Fichero no codificado con PCM lineal')
        else:
            longSen = subchunk2size // blockalign
            fmtData = '<' + str(longSen*numchannels) + bits2fmt(bitspersample)  #formato de la información
            buffData = fpWav.read(struct.calcsize(fmtData))
            data = struct.unpack(fmtData, buffData)

   

    infofichero = (numchannels, samplerate, bitspersample, data)
    return tuple(infofichero)
    

def escrWave(ficWave, /, *, numChannels = 2, sampleRate = 44100, bitsPerSample = 16, data = []):

    with open (ficWave, 'wb') as fic_wave:
        fcan = '<4sI4s4sIHHIIHH4sI' #formato canónico de la cabecera
        byteRate = int(sampleRate * numChannels *  bitsPerSample / 8)
        subchunk2id = b'data' #4s
        subchunk2Size = int(len(data) * numChannels *  bitsPerSample / 8)
        blockAlign = int(numChannels *  bitsPerSample / 8)
        
        
        chunkid = b'RIFF'#4s
        chunksize = int(36 + len(data)) #I
        formato = b'WAVE' #4s
        subchunk1id = b'fmt ' #4s
        subchunk1size = 16 #I
        audioformat = 1 #H
        
        #valores de la cabecera
        buffer = struct.pack(fcan, chunkid, chunksize,formato,subchunk1id, 
        subchunk1size, audioformat, numChannels, sampleRate, byteRate, blockAlign,
        bitsPerSample, subchunk2id, subchunk2Size)

        fic_wave.write(buffer)

        fmtData = '<' + str(len(data)) + bits2fmt(bitsPerSample)
        bufferData = struct.pack(fmtData, *data)
        fic_wave.write(bufferData)

def estereo2mono(ficEste, ficMono, canal=2):
    
    """
    Lee el fichero WAVE ficEste, que debe contener una señal de audio estéreo, y escribe el
    fichero ficMono, que debe incluir una señal monofónica.
    El tipo de señal concreto que se almacena en el fichero ficMono depende del valor del
    argumento canal:
    canal=0: Se almacena el canal izquierdo, L.
    canal=1: Se almacena el canal derecho, R.
    canal=2: Se almacena la semisuma de los dos canales, (L+R)/2. Es la opción por defecto.
    canal=3: Se almacena la señal semidiferencia, (L − R)/2.
    """

    numchannels, samplerate, bitspersample, data = leeWave(ficEste)

    if numchannels != 2: raise ValueError
    else:
        if canal == 0:
            escrWave(ficMono, numChannels = 1, sampleRate = samplerate, 
            bitsPerSample = bitspersample, data = data[::2])
        elif canal == 1:
            escrWave(ficMono, numChannels = 1, sampleRate = samplerate, 
            bitsPerSample = bitspersample, data = data[1::2])
        elif canal == 2:
            escrWave(ficMono, numChannels = 1, sampleRate = samplerate, 
            bitsPerSample = bitspersample,
            data = [int((l + r) / 2) for l, r in zip(data[::2], data[1::2])])
        elif canal == 3:
            escrWave(ficMono, numChannels = 1, sampleRate = samplerate, 
            bitsPerSample = bitspersample,
            data = [int((l - r) / 2) for l, r in zip(data[::2], data[1::2])])


def mono2estereo ( ficIzq, ficDer, ficEste):
    
    '''
    Lee los ficheros ficIzq y ficDer, que contienen las señales monofónicas correspondientes a
    los canales izquierdo y derecho, respectivamente, y construye con ellas una señal estéreo
    que almacena en el fichero ficEste.
    
    '''

    # Guardamos los datos de los dos ficheros

    numchannels_l, samplerate_l, bitspersample_l, L = leeWave(ficIzq)
    numchannels_r, samplerate_r, bitspersample_r, R = leeWave(ficDer)

    if (numchannels_l, samplerate_l, bitspersample_l) != (numchannels_r, samplerate_r, bitspersample_r):
        raise ValueError

    else:
        data = [None] * (len(L) + len(R))
        data[::2] = L
        data[1::2] = R

        #para los dos ficheros tenemos cabeceras iguales
        escrWave(ficEste, 2, sampleRate=samplerate_l, bitsPerSample=bitspersample_l, data=data) 

def codEstereo(ficEste, ficCod):

    """
    Lee el fichero ficEste, que contiene una señal estéreo codificada con PCM lineal de 16 bits,
    y construye con ellas una señal codificada con 32 bits que permita su reproducción tanto
    por sistemas monofónicos como por sistemas estéreo preparados para ello.
    
    """

    with open(ficEste, 'rb') as ficEs , open(ficCod, 'wb') as ficCodif:
        
        datosF = leeWave(ficEs)
        datosL = datosF[3][::2]
        datosR = datosF[3][1::2]
        semiSum = [(sampleL + sampleR) // 2 for sampleL, sampleR in zip(datosL, datosR)] 
        semiRes = [(sampleL - sampleR) // 2 for sampleL, sampleR in zip(datosL, datosR)]
        cod = [cod_2en1(sampleSum, sampleRes) for sampleSum, sampleRes in zip(semiSum,semiRes)]
        escrWave(ficCodif, numChannels=1, sampleRate=16000, bitsPerSample=32, data=cod)

    
def decEstereo(ficCod, ficEste):
   
    """
    Lee el fichero ficCod con una señal monofónica de 32 bits en la que los 16 bits más significativos
    contienen la semisuma de los dos canales de una señal estéreo y los 16 bits menos
    significativos la semidiferencia, y escribe el fichero ficEste con los dos canales por separado.
    
    """
    with open(ficCod, 'rb') as ficC , open(ficEste, 'wb') as ficE:
        d32b = leeWave(ficC)
        d16b = [dec_2en1(value) for value in d32b[3]]
        Sum = [L + R for L , R in d16b]
        Res = [L - R for L , R in d16b]

        vector_LR = [sample[i] for i in range(len(Sum)) for sample in [Sum, Res]]
        escrWave(ficE, 2, 16000, bitsPerSample=16, data=vector_LR)
    