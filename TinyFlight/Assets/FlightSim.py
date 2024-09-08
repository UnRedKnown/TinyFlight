from math import pi

alt = 5000
hdg = 000
spd = 300
x = 10
z = 10
isroll = 1
ispitch = 1
isyaw = 1
rollrate = 0
pitchrate = 0
yawrate = 0
roll = 0
pitch = 0
yaw = 0
fps = 60
glimitmaxturn = 0
airdensity = 0
liftforce = 0
liftcoef = 0

thumbycolor.setFPS(fps)

# F-15C Eagle, clean config, for testing purposes
maxthrust = 211400
fuel = 6103
weight = 12701 + fuel
wingspan = 13.06
length = 19.43
height = 5.64
wingarea = 56.5
maxspeed = 1433
maxalt = 65000
glimit = 9

while(1):
    glimitmaxturn = ((glimit*9.81)/(spd/1.944)) * 180/pi
    twr = maxthrust / (weight * 9.81)
    airdensity = 101325 * (1 - 2.25577*10**-5*(alt/3.281))**5.25588
    
    if button.buttonU.pressed():
        ispitch = 2
    elif button.buttonD.pressed():
        ispitch = 0
    else: ispitch = 1
    if button.buttonR.pressed():
        isroll = 2
    elif button.buttonL.pressed():
        isroll = 0
    else: isroll = 1
    if button.buttonRB.pressed():
        isyaw = 2
    elif button.buttonLB.pressed():
        isyaw = 0
    else: isyaw = 1

    
