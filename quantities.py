import math

class Quantity:
    def __init__(self, value, mass=0, length=0, time=0, current=0, temperature=0, n=0, j=0):
        self.value = value
        self.dimension = [mass, length, time, current, temperature, n, j]
        
    def __add__(self, other):
        if self.dimension == other.dimension:
            return Quantity(self.value + other.value, *self.dimension)
        else:
            raise Exception(f"Quantities' dimensions don't match")
        
    def __sub__(self, other):
        if self.dimension == other.dimension:
            return Quantity(self.value + -other.value, *self.dimension)
        else:
            raise Exception(f"Quantities' dimensions don't match")
        
    def __mul__(self, other):
        return Quantity(self.value * other.value, *(x + y for x, y in zip(self.dimension, other.dimension)))
    
    def __truediv__(self, other):
        return Quantity(self.value / other.value, *(x - y for x, y in zip(self.dimension, other.dimension)))
    
    def __pow__(self, other):
        if other.dimension == [0, 0, 0, 0, 0, 0, 0]:
            return Quantity(self.value ** other.value, *(x * other.value for x in self.dimension))
        raise Exception("Can't raise a quantity to a dimensional power")
    
    def __neg__(self):
        return Quantity(-self.value, *self.dimension)

    def __eq__(self, other):
        return self.value == other.value and self.dimension == other.dimension

    def __repr__(self):
        return f"Quantity({self.value}, mass={self.dimension[0]}, length={self.dimension[1]}, time={self.dimension[2]}, current={self.dimension[3]}, temperature={self.dimension[4]}, n={self.dimension[5]}, j={self.dimension[6]})"

    def to_string(self, method="base"):
        if method == "base":
            ans = f"{self.value}"
            for dimension in self.dimension:
                if dimension != 0:
                    ans += " "
                    break
            return ans + " ".join([f"{QSTRINGS[i]}" + (f"^{dimension}" if dimension != 1 else "") for i, dimension in enumerate(self.dimension) if dimension])
        elif method == "derived":
            self_unit = Quantity(1.0, *self.dimension)
            for unit_name, unit in UNITS.items():
                if unit == self_unit:
                    return f"{self.value} {unit_name}"
            return self.to_string()
        else:
            raise Exception(f"Unkown string conversion method for Quantity: \"{method}\"")


QSTRINGS = ["kg", "m", "s", "A", "K", "mol", "cd"]

kg = Quantity(1, mass=1.0)
m = Quantity(1, length=1.0)
s = Quantity(1, time=1.0)
A = Quantity(1, current=1.0)
K = Quantity(1, temperature=1.0)
mol = Quantity(1, n=1.0)
cd = Quantity(1, j=1.0)

lb = Quantity(0.45359237) * kg
inch = Quantity(0.0254) * m
ft = Quantity(0.3048) * m
yd = Quantity(3) * ft
mi = Quantity(5280) * ft

minute = Quantity(60) * s
hr = Quantity(3600) * s
day = Quantity(24) * hr

N = kg * m / s / s
J = N * m
W = J / s
V = W/A
ohm = V/A
C = A * s
F = C / V
H = V * s / A

earth_gravity = Quantity(9.80665) * m / s / s

lbf = lb * earth_gravity
horsepower = Quantity(550) * lbf * ft / s

UNITS = {
    "kg": kg,
    "m": m,
    "s": s,
    "A": A,
    "K": K,
    "mol": mol,
    "cd": cd,
    "lb": lb,
    "in": inch,
    "ft": ft,
    "yd": yd,
    "mi": mi,

    "min": minute,
    "hr": hr,
    "day": day,

    "N": N,
    "J": J,
    "W": W,
    "Pa": N / m / m,
    "V": V,
    "ohm": ohm,
    "C": C,
    "F": F,
    "H": H,

    "gravity": earth_gravity,
    "pi": Quantity(math.pi),

    "lbf": lbf,
    "hp": horsepower,
    "g": Quantity(1e-3) * kg,
    "km": Quantity(1e3) * m,
    "L": Quantity(1e-3) * m ** Quantity(3)
}