import thumbycolor
from time import sleep
import thumbycolorButton as button

thumbycolor.drawPic('/Games/TinyFlight/splash.png', 0, 0)
sleep(2)
thumbycolor.setFont('/lib/font6x10.bin', 6, 10, 1)

sel = 0
spsel = 0
planes = ['F14 TOMCAT', 'F35B LIGHTNING II', 'SU-57 FELON', 'F15 EAGLE', 'F22 RAPTOR', 'SU-35 FLANKER-E']
cursorPosx = [14, 19, 28, 40]
cursorPosy = [59, 73, 84, 98]
spcursorPosx = [22, 23, 44]

def spobjmenu():

def spmenu():
    sel = 0
    while(1):
        thumbycolor.display.drawPic('/Games/TinyFlight/spmenu.png', 0, 0)
        if button.buttonU.justPressed():
            spsel -= 1
        elif button.buttonD.justPressed():
            spsel += 1
        if sel < 0:
            sel = 2
        elif sel > 2:
            sel = 0
        thumbycolor.display.drawFilledRectangle(spcursorPosx[sel], cursorPosy[sel], 6, 6, green)
        thumbycolor.display.update()
        if button.buttonA.justPressed():
            if sel == 0:
                return 0
            elif sel == 1:
                return spobjmenu()


def menu():
    sel = 0
    while(1):
        thumbycolor.display.drawPic('/Games/TinyFlight/menu.png', 0, 0)
        if button.buttonU.justPressed():
            sel -= 1
        elif button.buttonD.justPressed():
            sel += 1
        if sel < 0:
            sel = 3
        elif sel > 3:
            sel = 0
        thumbycolor.display.drawFilledRectangle(cursorPosx[sel], cursorPosy[sel], 6, 6, green)
        thumbycolor.display.update()
        if button.buttonA.justPressed():
            if sel == 1:
                return spmenu()
            

while(1):
    sel = menu()
    if sel == 0:


# thumbycolor.drawText(planes[sel], (128 - len(planes[sel]))//2, 2, green)