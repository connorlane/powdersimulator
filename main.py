import PowderSimulator
import matplotlib.pyplot as plt
import numpy as np

simulationDuration = 1.0
meltpoolVolume = 2e-3
particleMeltpoolRatio = 100
meltpoolVolumesPerMinute = 1000
percentAddition = 0.001

M = []
OUT = dict()
while percentAddition < 0.999:
    Met1 = PowderSimulator.Material("Met1", 1.0)
    Met2 = PowderSimulator.Material("Met2", 1.0)

    overallFlowRate = meltpoolVolume * meltpoolVolumesPerMinute
    Met1_Generator = PowderSimulator.NormalParticleGenerator(Met1, 0.5 * meltpoolVolume / particleMeltpoolRatio, meltpoolVolume / particleMeltpoolRatio, overallFlowRate * (1 - percentAddition))
    Met2_Generator = PowderSimulator.NormalParticleGenerator(Met2, 0.5 * meltpoolVolume / particleMeltpoolRatio, meltpoolVolume / particleMeltpoolRatio, overallFlowRate * percentAddition)
    #Met1_Generator = PowderSimulator.IdenticalParticleGenerator(Met1, meltpoolVolume / particleMeltpoolRatio, overallFlowRate * 0.99)
    #Met2_Generator = PowderSimulator.IdenticalParticleGenerator(Met2, meltpoolVolume / particleMeltpoolRatio, overallFlowRate * 0.01)

    ParticleGenerators = [Met2_Generator, Met1_Generator]

    meltpool = PowderSimulator.Meltpool(meltpoolVolume, {Met1: (1 - percentAddition), Met2: percentAddition})

    T, result = PowderSimulator.Run(meltpool, ParticleGenerators, simulationDuration)

    print "\r\PercentAddition:", percentAddition
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

    percentAddition = percentAddition + percentAddition * (1 - percentAddition) * 0.1


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

