import numpy as np
import antenna
import itertools
import json

class AntennaArray:
    def __init__(self, antennas):
        self.antennas = antennas
        # "Circular" around a reference element

#        for el_idx, el_val in enumerate(self.antennas):
#            print("Element: {e}. x: {x}, y: {y}".format(e=el_idx, x=el_val.x, y=el_val.y))

    @classmethod
    def mk_from_config(cls, array_geometry_file):
        json_data = open(array_geometry_file).read()
        array_geometry = json.loads(json_data)
        antennas = []
        for ant_geo in array_geometry:
            antenna = antenna.Antenna(ant_geo['x'], ant_geo['y'])
            antennas.append(antenna)
        return cls(antennas)

    @classmethod
    def mk_circular(cls, d, num_elements):
        antennas = []
        arc_length_per_element = (2*np.pi)/num_elements
        for el in range(0, num_elements):
            antennas.append(antenna.Antenna(d,0).rotated(el * arc_length_per_element))
        return cls(antennas)

    @classmethod
    def mk_circular_with_ref(cls, d, num_elements):
        antennas = []
        antennas.append(antenna.Antenna(0, 0))
        arc_length_per_element = (2*np.pi)/(num_elements-1)
        for el in range(0, num_elements-1):
            antennas.append(antenna.Antenna(d,0).rotated(el * arc_length_per_element))
        return cls(antennas)

    def phases_at_angle(self, phi):
        phases_of_elements = np.array([])
        for antenna in self:
            phases_of_elements = np.append(phases_of_elements, antenna.phase_at_angle(phi))
        return phases_of_elements

    def __iter__(self):
        self.current = 0
        return self

    def __len__(self):
        return len(self.antennas)

    def next(self):
        if self.current >= len(self.antennas):
            raise StopIteration
        self.current += 1
        return self.antennas[self.current - 1]

    def each_pair(self):
        pairs = itertools.combinations(self.antennas, 2)
        for pair in pairs:
            yield pair

    def each_pair_phase_difference_at_angle(self, phi, f):
        phases_of_pairs = np.array([])
        for ant0, ant1 in self.each_pair():
            phases_of_pairs = np.append(
                phases_of_pairs,
                self.phase_difference_between_two_antennas_at_angle(
                    ant0, 
                    ant1, 
                    phi, 
                    f
                )
            )
        return phases_of_pairs

    def phase_difference_between_two_antennas_at_angle(self, antA, antB, phi, f):
        """Implements antB.phase - antA.phase"""
        antA_phase = antA.phase_at_angle(phi, f)
        antB_phase = antB.phase_at_angle(phi, f)
        delta_phase = antB_phase - antA_phase
        # force phase to range from -pi to pi. I sort of know how this works...
        normalised_phase = np.arctan2(np.sin(delta_phase), np.cos(delta_phase))
        return normalised_phase
