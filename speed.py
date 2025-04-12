from math import sin, cos, atan, pi, sqrt, pow, tan, radians


# Physical constants
g = 9.81        # gravity m.s-2



class SpeedVector:
    def __init__(self, radian =0, speed =0, unit ="m/s"):
        self.theta = radian      # angle from horizontal in radians
        self.speed = speed            # module scalar value
        self.unit = unit                # speed unit ("m/s", "km/h", ...)
        self.vx = speed*cos(radian) # projected vector on x-axis
        self.vz = speed*sin(radian) # projected vextor on z-axis

zero_speed = SpeedVector (0, 0, "m/s")

# detect jump
def jump_detect(v0: SpeedVector, phi: float) -> bool:
    threshold_angle = radians (2)
    if v0.theta > phi + threshold_angle:
        return True
    else:
        return False

# compute jump xB
def jump_z (dx: float, v0: SpeedVector, type: str) -> float:
    #type = Basic
    match type:
        case "basic":
            try :
                dz = -0.5*g/(v0.vx**2)*(dx**2) + tan(v0.theta)*dx
            except ZeroDivisionError:
                dz = 0
    return  (dz) 

# Compute speed vector in air
def jump_speed (dx: float, k: float, v0: SpeedVector) -> SpeedVector:
    vx = v0.speed*cos(v0.theta)
    vy = -g*dx/vx + v0.speed*sin(v0.theta) 
    speed = sqrt(pow(vx,2)+pow(vy,2)) #- airFrictionLoss(k, v0.speed) #Approximate constant air friction along dx segment
    unit = v0.unit
    theta = atan (vy/vx)
    return (SpeedVector(theta, speed, unit))

def airFrictionLoss(k: float, speed: float) -> float:
    return sqrt(k*pow(speed,2)) #speed loss

def rollingz (dx: float, theta: float) -> float:
    return (dx*sin(theta)) # dz

# Compute speed vector on ground
def rolling_speed (theta: float, dist: float, k: float, mu: float, v0: SpeedVector) -> SpeedVector:
    speed = sqrt((2*g*(sin(-theta) - mu*cos(theta)) - k*pow(v0.speed,2))*dist + pow(v0.speed,2)) 
    return (SpeedVector(theta, speed, v0.unit))

def vz(x:float, phi:float, v0:float) -> float:
    return (-g*x/(v0*cos(phi)) + v0*sin(phi))

def vx(x:float , phi:float, v0:float) -> float:
    return (v0*cos(phi))

def speed(vx:float , vz:float) -> float:
    return (sqrt(vx**2 + vz**2))
