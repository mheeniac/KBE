import matplotlib.pyplot as plt
import numpy
import numpy.linalg as np
from parapy.core import *
from parapy.geom import *


class ForceLines(Base):
    craft = Input()
    plot = Input()

    @Attribute
    def force_lines(self):
        dx = 0.001
        L = self.craft.def_v_tail_wing.b_rudder
        X = numpy.linspace(0, L, int(L / dx) + 1)
        q = self.craft.hinge_side_force[1]

        y_hinge_forces = []
        for i in xrange(len(self.craft.total_hinge_force[2])):
            y_hinge_forces.append(self.craft.total_hinge_force[2][i])
            if i == self.craft.force_distances[1][0]:
                y_hinge_forces.append(self.craft.actuator_forces[0][1])

        x_hinge_forces = []
        for i in xrange(len(self.craft.force_distances[1])):
            x_hinge_forces.append(self.craft.total_hinge_force[1][self.craft.force_distances[1][i]])
            if i == self.craft.force_distances[1][0]:
                x_hinge_forces.append(self.craft.actuator_forces[0][0])

        pos_y_hinge_forces = []
        for x in xrange(len(self.craft.def_v_tail_wing.hinges)):
           pos_y_hinge_forces.append(int((self.craft.def_v_tail_wing.hinges[x].center.z - self.craft.def_v_tail_wing.closure_ribs[0].vertices[0].point.z)/dx))
           if x == self.craft.force_distances[1][0]:
               pos_y_hinge_forces.append(int((self.craft.def_v_tail_wing.actuator_hinge_line.midpoint.z - self.craft.def_v_tail_wing.closure_ribs[0].vertices[0].point.z)/dx))

        pos_x_hinge_forces = []
        for x in xrange(len(self.craft.force_distances[1])):
           pos_x_hinge_forces.append(int((self.craft.def_v_tail_wing.hinges[self.craft.force_distances[1][x]].center.z - self.craft.def_v_tail_wing.closure_ribs[0].vertices[0].point.z)/dx))
           if x == self.craft.force_distances[1][0]:
               pos_x_hinge_forces.append(int((self.craft.def_v_tail_wing.actuator_hinge_line.midpoint.z - self.craft.def_v_tail_wing.closure_ribs[0].vertices[0].point.z)/dx))


        D = [0]
        x = 0
        Vx = []
        Vy = []
        Mx = []
        My = [0]
        Mz = []
        nmb = 0

        for i in xrange(int(L / dx) + 1):
            if i in pos_y_hinge_forces:
                D.append(y_hinge_forces[nmb])
                nmb = nmb + 1
            Vyy = -q*x - sum(D)
            Vy.append(Vyy)
            x = x + dx

        Mxxx = []
        for i in xrange(int(L / dx) + 1):
            Mxxx.append(Vy[i])
            Mxx = numpy.trapz(Mxxx, dx=dx)
            Mx.append(Mxx)

        nmb = 0
        D = [0]
        for i in xrange(int(L / dx) + 1):
            if i in pos_x_hinge_forces:
                D.append(x_hinge_forces[nmb])
                nmb = nmb + 1
            Vxx = -sum(D)
            Vx.append(Vxx)

        x=0
        for i in xrange(int(L / dx)):
            if i > pos_x_hinge_forces[0] and i < pos_x_hinge_forces[1]:
                Myy = My[i] + (x_hinge_forces[0]/(pos_x_hinge_forces[1]-pos_x_hinge_forces[0])*(x-pos_x_hinge_forces[0]))
                My.append(Myy)
            elif i >= pos_x_hinge_forces[1] and i <= pos_x_hinge_forces[2]:
                Myy = My[i] - (x_hinge_forces[2] / (pos_x_hinge_forces[2] - pos_x_hinge_forces[1])*(x - pos_x_hinge_forces[1]))
                My.append(Myy)
            elif i > pos_x_hinge_forces[2]:
                My.append(0)
            else:
                My.append(0)
            x=x+dx

        x=0
        r = self.craft.def_v_tail_wing.d_hinge * self.craft.x_fc
        point_act = self.craft.def_v_tail_wing.actuator_hinge_line.midpoint  # Point on act line
        point_hinge = self.craft.def_v_tail_wing.hingerib_line.midpoint  # point on hinge line
        min_1 = point_act - self.craft.def_v_tail_wing.hingerib_line.start
        min_2 = point_act - self.craft.def_v_tail_wing.hingerib_line.end
        d1 = self.craft.def_v_tail_wing.hingerib_line.start.distance(self.craft.def_v_tail_wing.hingerib_line.end)
        d = numpy.cross(min_1, min_2) / d1
        da = d[0]
        for i in xrange(int(L / dx)+1):

            if i >= pos_x_hinge_forces[1]:
                Mzz = -q*x*r + q*L*r
                Mz.append(Mzz)
            else:
                Mzz = -q * x * r
                Mz.append(Mzz)
            x = x+dx
        return [Vx,Vy,Mx,My,Mz,X]

    @Attribute
    def plot_lines(self):
        plt.plot(self.force_lines[5],self.force_lines[self.plot])
        return plt.show()