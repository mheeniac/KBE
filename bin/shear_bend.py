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

    plt.plot(X,V)
    plt.show()
    plt.plot(X,M)
    plt.show()


    # @Attribute
    # def force_lines(self):
    #     dx = 0.01
    #     L = self.r_rudder
    #     X = numpy.linspace(0, L, int(L / dx) + 1)
    #     for i in xrange(int(L / dx) + 1):
    #         Vx =
    #     return [Vx, Vy, Mx, My, Mz, X]