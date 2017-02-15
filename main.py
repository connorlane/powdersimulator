import PowderSimulator
import matplotlib.pyplot as plt
import numpy as np

numberOfParticles = 5e4
particleVolume = 1e-4
percentAddition = 0.001

M = []
OUT = dict()
while percentAddition < 1:
    simulationDuration = numberOfParticles

    Met1 = PowderSimulator.Material("Met1", 1.0)
    Met2 = PowderSimulator.Material("Met2", 1.0)

    overallFlowRate = particleVolume

    #Met1_Generator = PowderSimulator.NormalParticleGenerator(
    #        Met1, 
    #        0.5 * meltpoolVolume / particleMeltpoolRatio, 
    #        meltpoolVolume / particleMeltpoolRatio, 
    #        overallFlowRate * (1 - percentAddition))
    #Met2_Generator = PowderSimulator.NormalParticleGenerator(
    #        Met2, 
    #        0.5 * meltpoolVolume / particleMeltpoolRatio, 
    #        meltpoolVolume / particleMeltpoolRatio, 
    #        overallFlowRate * percentAddition)

    Met1_Generator = PowderSimulator.IdenticalParticleGenerator(
            Met1, 
            particleVolume, 
            overallFlowRate * (1 - percentAddition))
    Met2_Generator = PowderSimulator.IdenticalParticleGenerator(
            Met2, 
            particleVolume, 
            overallFlowRate * percentAddition)

    ParticleGenerators = [Met2_Generator, Met1_Generator]

    meltpool = PowderSimulator.Meltpool(1.0, {Met1: (1 - percentAddition), Met2: percentAddition})

    T, result = PowderSimulator.Run(meltpool, ParticleGenerators, simulationDuration)

    print "\r\n percentAddition:", percentAddition
    M.append(percentAddition)

    for material, massPercent in result.iteritems():
        standardDeviation = np.std(massPercent)
        mean = np.mean(massPercent)
        print "\tMaterial:", material
        print "\t\tStandard Deviation", standardDeviation
        print "\t\tMean", mean

        if not material.label in OUT:
            OUT[material.label] = []
        OUT[material.label].append((standardDeviation, mean))

    percentAddition = percentAddition + 0.001

for material, stats in OUT.iteritems():
    #CV = [sd / mean for sd, mean in stats]
    CV = [sd for sd, mean in stats]
    plt.loglog(M, CV, label=material)

f = open('output.csv', 'w')
for i in xrange(0, len(M)):
    f.write(str(M[i]))
    for material, stats in OUT.iteritems():
        #cv = stats[i][0] / stats[i][1]
        f.write(', ' + str(stats[i][0]) + ', ' + str(stats[i][1]))
    f.write('\n')

f.close()
plt.show()

