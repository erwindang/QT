import numpy as np
import matplotlib.pyplot as plt

# Constantes
g = 9.81  # Accélération due à la gravité (m/s²)
v0 = 20  # Vitesse initiale (m/s)
angle_deg = 30  # Angle de lancement en degrés
angle_rad = np.radians(angle_deg)  # Conversion en radians

# Composantes initiales de la vitesse
v0x = v0 * np.cos(angle_rad)  # Vitesse initiale en x
v0y = v0 * np.sin(angle_rad)  # Vitesse initiale en y

# Temps de vol total jusqu'à l'impact (sol y=0)
t_flight = 2 * v0y / g

# Vecteur temps
t = np.linspace(0, t_flight, num=500)

# Vitesse en fonction du temps
vx = np.full_like(t, v0x)  # vx reste constant sans résistance de l'air
vy = v0y - g * t  # vy diminue linéairement avec la gravité

# Vitesse résultante
v = np.sqrt(vx**2 + vy**2)

# Position en x en fonction du temps
x = v0x * t

# Création du graphe vitesse résultante en fonction de la position x
plt.figure(figsize=(8, 5))
plt.plot(x, v, label='Vitesse résultante')
plt.xlabel('Position x (m)')
plt.ylabel('Vitesse (m/s)')
plt.title('Vitesse d\'un solide en chute libre en fonction de la position x')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()