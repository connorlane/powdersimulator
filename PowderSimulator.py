import numpy as np

SIMULATION_DURATION = 1

class Material:
    def __init__(self, label, density):
        self.label = label
        self.density = density
    
    def __str__(self):
        return self.label

class Particle:
    def __init__(self, material, mass, volume):
        self.mass = mass
        self.volume = volume
        self.material = material

class NormalParticleGenerator:
    def _RegenerateNextParticleTime(self, t):
        self._nextParticleTime = t + np.random.exponential(self._beta)

    def __init__(self, material, mass_sigma, mass_mean, mass_flow_rate, t = 0):
        self._material = material
        self._mass_sigma = mass_sigma
        self._mass_mean = mass_mean
        self._beta = mass_mean / mass_flow_rate
        self._RegenerateNextParticleTime(t)

    def GenerateParticle(self, t):
        self._RegenerateNextParticleTime(t)
        mass = np.random.normal(self._mass_mean, self._mass_sigma)
        volume = mass / self._material.density
        return Particle(self._material, mass, volume)

    def GetNextParticleTime(self):
        return self._nextParticleTime

class Meltpool:
    def __init__(self, volume, initial_composition):
        totalMass = 0
        self.composition = initial_composition
        self.volume = volume
        self._NormalizeVolume()

    def _NormalizeVolume(self):
        volumeSum = 0
        for material, partial_mass in self.composition.iteritems():
            volumeSum = volumeSum + partial_mass / material.density
        for material, partial_mass in self.composition.iteritems():
            volume = partial_mass / material.density
            newVolume = volume * self.volume / volumeSum
            self.composition[material] = newVolume * material.density

    def GetComposition(self):
        return self.composition

    def AddParticle(self, particle):
        if particle.material in self.composition:
            self.composition[particle.material] = self.composition[particle.material] + particle.mass
        else:
            self.composition[particle.material] = particle.mass
        self._NormalizeVolume()

Ti64 = Material("Ti64", 4.5)
H13 = Material("H13", 8.5)

H13_ParticleGenerator = NormalParticleGenerator(H13, 0, 1e-5, 1.0)
Ti64_ParticleGenerator = NormalParticleGenerator(Ti64, 0, 4e-6, 0.02)

ParticleGenerators = [H13_ParticleGenerator, Ti64_ParticleGenerator]

meltpool = Meltpool(3e-4, {Ti64: 0.0, H13: 100.0})

f = open("output.csv", "w")

printTime = 0
t = 0
while t < SIMULATION_DURATION:
    # Record the material composition
    if t >= printTime:
        composition = meltpool.GetComposition()

        massSum = 0
        for material, mass in composition.iteritems():
            massSum = massSum + mass

        print "t:", t
        print "Composition:"
        
        for material, mass in composition.iteritems():
            print '\t', material,': ', mass / massSum

        f.write(str(t))
        for material, mass in composition.iteritems():
            f.write(', ' + str(mass / massSum))
        f.write('\n')

        printTime = printTime + 0.001

    # Get the time of the next particle intersection
    nextParticleGenerator = ParticleGenerators[0]
    for p in ParticleGenerators[1:]:
        if p.GetNextParticleTime() < nextParticleGenerator.GetNextParticleTime():
            nextParticleGenerator = p

    # Fast forward to next particle collision
    t = nextParticleGenerator.GetNextParticleTime()

    # Get the particle & add to the meltpool
    particle = nextParticleGenerator.GenerateParticle(t)
    meltpool.AddParticle(particle)

f.close()