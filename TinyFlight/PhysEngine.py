import math
# raptor = [maxthrust, abmaxthrust, minweight, weight, wingarea, wingspan, oswaldefficiency, wingangle, thickchordratio, liftcoef0, parasitedrag, baselineclmax, chordlength]
class Physics:
    def __init__(self, aircraft_params):
        # Initialize aircraft constants and parameters
        self.maxthrust = aircraft_params[0]
        self.abmaxthrust = aircraft_params[1]
        self.minweight = aircraft_params[2]
        self.weight = aircraft_params[3]
        self.wingarea = aircraft_params[4]
        self.wingspan = aircraft_params[5]
        self.oswaldefficiency = aircraft_params[6]
        self.wingangle = aircraft_params[7]
        self.thickchordratio = aircraft_params[8]
        self.liftcoef0 = aircraft_params[9]
        self.parasitedrag = aircraft_params[10]
        self.baselineclmax = aircraft_params[11]
        self.chordlength = aircraft_params[12]

        self.aspectratio = (self.wingspan ** 2) / self.wingarea
        self.liftslope = (2 * math.pi * self.aspectratio) / (2 + math.sqrt(4 + (self.aspectratio**2) * (1 + (math.tan(math.radians(self.wingangle))**2))))
        self.totalweight = self.minweight + self.weight

        self.elevator_deflection = 0
        self.aileron_deflection = 0
        self.pitchrate = 0
        self.rollrate = 0
        self.y = 0
        self.aoa = 0
        self.velocity = 0
        self.throttle = 0
        self.abtoggle = 0
        self.pitchmomentcoef = 1

    def update_vars(self, variables):
        self.y, self.aoa, self.velocity, self.throttle, self.elevatordeflection, self.ailerondeflection = variables
        self.abtoggle = 0 if 0 <= self.throttle <= 80 else 1

    def update_data(self):
        temp = 288.15 - 0.0065 * self.y
        self.machspd = self.velocity / (math.sqrt(1.4 * 287.05 * temp))
        airdensity = ((101325 * ((1 - (0.00976 * self.y / 288.15)) ** ((9.81 * 0.02896968) / (8.314462618 * 0.00976)))) * 0.0289644) / (8.31447 * temp)
        liftcoef = self.liftcoef0 + self.liftslope * math.radians(self.aoa)
        self.lift = 0.5 * airdensity * (self.velocity ** 2) * liftcoef * self.wingarea
        induceddrag = (liftcoef ** 2) / (math.pi * self.aspectratio * self.oswaldefficiency)
        dragcoef = self.parasitedrag + induceddrag
        drag = 0.5 * airdensity * (self.velocity ** 2) * dragcoef * self.wingarea
        if self.abtoggle == 0:
            netforcefwd = self.maxthrust * (self.throttle / 100) - drag
            twr = self.maxthrust * (self.throttle / 100) / self.totalweight
        elif self.abtoggle == 1:
            netforcefwd = self.abmaxthrust - drag
            twr = self.abmaxthrust / self.totalweight
        self.acceleration = netforcefwd / (self.totalweight / 9.81)
        clmax = self.baselineclmax + (self.thickchordratio/0.1)
        self.stallspd = math.sqrt((self.totalweight * 2) / (airdensity * self.wingarea * clmax))
        dynamicpressure = 0.5*1.225*(self.velocity**2)

        pitchmoment = 0.5*airdensity*(self.velocity ** 2)*self.wingarea*self.pitchmomentcoef
        self.pitchmomentcoef = pitchmoment/(dynamicpressure*self.wingarea*self.chordlength)
    def update_physics(self, delta_time):
        self.update_data()


        # Return some key physics values for display/debugging
        return {
            'lift': lift,
            'drag': self.calculate_drag(self.liftcoef0 + self.liftslope * math.radians(self.aoa)),
            'net_force_forward': net_force_forward,
            'acceleration': acceleration,
            'stall_speed': self.calculate_stall_speed(),
            'roll_rate': self.roll_rate,
            'yaw_rate': self.yaw_rate,
            'pitch_rate': self.pitch_rate
        }
