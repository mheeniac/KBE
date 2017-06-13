import matplotlib.pyplot as plt
import numpy
from parapy.core import *
from parapy.geom import *


class ForceLines(Base):
    craft = Input()

    V = []
    q = 0.2 #N/m
    L = 3.2
    dx = 0.1
    x = 0
    X = numpy.linspace(0,L,int(L/dx)+1)
    D = 0
    for i in xrange(int(L/dx)+1):
        if i == int(2/dx):
            D = -1
            print D
            print i
        F = q*x + D
        V.append(F)
        x=x+dx

    print q*L
    print V

    S=[]
    M=[]
    for i in xrange(int(L/dx)+1):
        S.append(V[i])
        T = numpy.trapz(S, dx=0.1 )
        M.append(T)
    print 0.5*q*L**2
    print M

    # plt.plot(X,V)
    # plt.show()
    # plt.plot(X,M)
    # plt.show()


    @Attribute
    def force_lines(self):
        dx = 0.001
        L = self.craft.def_v_tail_wing.b_rudder
        X = numpy.linspace(0, L, int(L / dx) + 1)
        q = self.craft.hinge_side_force[1]
        y_hinge_forces = self.craft.total_hinge_force[2]
        pos_y_hinge_forces = []
        for x in xrange(len(self.craft.def_v_tail_wing.hinges)):
           pos_y_hinge_forces.append(int((self.craft.def_v_tail_wing.hinges[x].center.z - self.craft.def_v_tail_wing.closure_ribs[0].vertices[0].point.z)/dx))
           print pos_y_hinge_forces
        D = 0
        x = 0
        Vx = []
        Vy = []
        Mx = []
        My = []
        Mz = []
        nmb = 0

        for i in xrange(int(L / dx) + 1):
            if i in pos_y_hinge_forces:
                print pos_y_hinge_forces[nmb]
                print i
                D = y_hinge_forces[nmb]
                nmb = nmb + 1
            Vyy = -q*x + D
            Vy.append(Vyy)
            x = x + dx
        return [Vx,Vy,Mx,My,Mz,X]

    @Attribute
    def plot_lines(self):
        plt.plot(self.force_lines[5],self.force_lines[1])
        return plt.show()