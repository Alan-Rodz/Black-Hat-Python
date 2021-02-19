import win32gui
import win32ui
import win32con
import win32api

# handle a la ventana principal del escritorio
hdesktop = win32gui.GetDesktopWindow()

# determinamos el tamaño de todos los monitores en pixeles
width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

# creamos un device context
desktop_dc = win32gui.GetWindowDC(hdesktop)
img_dc = win32ui.CreateDCFromHandle(desktop_dc)

# creamos un device context basado en memoria
mem_dc = img_dc.CreateCompatibleDC()

# creamos objeto bitmap
screenshot = win32ui.CreateBitmap()
screenshot.CreateCompatibleBitmap(img_dc, width, height)
mem_dc.SelectObject(screenshot)

# copiamos la pantalla a nuestro device context de memoria
mem_dc.BitBlt((0, 0), (width, height), img_dc, (left, top), win32con.SRCCOPY)

# guardamos el bitmap a un archivo
screenshot.SaveBitmapFile(mem_dc, 'c:\\WINDOWS\\Temp\\screenshot.bmp')

# liberamos nuestros objetos
mem_dc.DeleteDC()
win32gui.DeleteObject(screenshot.GetHandle())
