from parapy.core import *
from parapy.geom import *

class SphereClass(GeomBase):
    sphereDiameter=Input()
    sphereAngle=Input()

    @Part
    def spherePart(self):
        return Sphere(radius=self.sphereDiameter/2,
                      angle=self.sphereAngle)


if __name__ == '__main__':
    from parapy.gui import display

    obj = SphereClass()
    display(obj)
