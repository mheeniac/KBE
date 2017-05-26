from aircraft import Aircraft

def def_aircraft():
    return Aircraft()

hingepos = def_aircraft().def_v_tail_wing.pick_hingeribs


def forces():
    return def_aircraft().actuator_forces

# F1 = forces()[1][0]
# F2 = forces()[1][1]
# FA = forces()[0]
#
# print F1,hingepos
#
# FX = []
# for i in xrange(len(hingepos)):
#    if i+1 == forces()[1][2][0]:
#         FX.append(F1)
#         FX.append(-F2)
#         FX.append(-F2)
#         i = i + 4
#    else:
#        FX.append(0)
#
#
#
# distance = def_aircraft().force_distances
# MY1 = F1 * distance[0][1] / sum(distance[0])
# MY = []
# for i in xrange(len(hingepos)-1):
#    if i+1 == forces()[1][2][0]:
#         MY.append(0)
#         MY.append(MY1)
#         MY.append(0)
#         i = i + 4
#    else:
#        MY.append(0)



q = def_aircraft().hinge_side_force[1]

FY = []
for x in xrange(len(hingepos)):
    p2_z = def_aircraft().def_v_tail_wing.hinges[x].position.z
    p3_z = def_aircraft().def_v_tail_wing.hinges[x-1].position.z
    p4_z = def_aircraft().def_v_tail_wing.hinges[x].position.z

    if x == 0:
        p1_z = def_aircraft().def_v_tail_wing.fixed_part.position.z
        Fy = 0
        FY.append(0)
        x=x+1
        Fy = FY[x - 1] + (p2_z-p1_z)*q - def_aircraft().hinge_reaction_forces[0][x-1]
        FY.append(Fy)
        x=x+1
    elif x == forces()[1][2][0]+1:
        Fy = FY[x-1] + (p2_z - p3_z) * q
        FY.append(Fy)
    else:
        Fy = FY[x - 1] + (p2_z-p3_z)*q - def_aircraft().hinge_reaction_forces[0][x-2]
        FY.append(Fy)


FY


print FY

