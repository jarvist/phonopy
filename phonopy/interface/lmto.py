# LMTO INTERFACE TO PHONOPY
# -------------------------
# --- LMTO CLASS: Parses an lmto site file. Need to rewrite some
#                 sections. LMTO can now read site files generated by 
#                 phonopy. Since the LMTO site file doesn't lend itself
#                 so easily to the iterator structure, I will make the 
#                 site file into a meta class with the header and site
#                 positions extending it. This code is stable yet 
#                 inefficient.                 
#     LAST EDITED: 18.59 15/03/2016
#     VERSION: 0.5 --- gcgs

import sys
import numpy as np

from phonopy.file_IO import collect_forces, get_drift_forces
from phonopy.interface.vasp import get_scaled_positions_lines, sort_positions_by_symbols
from phonopy.units import Bohr
from phonopy.structure.atoms import Atoms, symbol_map

def parse_set_of_forces(num_atoms, forces_filenames):
    # No need to use collect_forces => no 'hook'
    force_sets = []
    for filename in forces_filenames:
        
        # Read in Forces
        lmto_forces = []
        with open(filename, 'r') as f:
            for lines in f:
                if lines.strip().startswith('%'): continue
                else:
                    lmto_forces.append(
                        [float(lines.split()[i]) for i in range(3)])
                    if len(lmto_forces) == num_atoms: break
    
        if not lmto_forces:
            return []

        drift_force = get_drift_forces(lmto_forces)
        force_sets.append(np.array(lmto_forces) - drift_force)

    return force_sets

def read_lmto(filename):
    lines = open(filename).readlines()

    # Try to define this in the class
    for i in lines:
        if i.strip().startswith('%'):
            header = i.split()
            if not 'xpos' in header:
                print 'LMTO site file not in cartesian coords'
                exit(-1)

    lmto_in = LMTOIn(lines)
    tags = lmto_in._get_variables(lines)
    plat = [tags['alat'] * np.array(tags['plat'][i]) for i in range(3)]
    symbols = tags['atoms']['spfnames']
    spfnames = list(set(symbols))
    numbers = []
    for s in symbols:
        numbers.append(symbol_map[s])

    positions = tags['atoms']['positions'] 

    return Atoms(numbers=numbers,
                 cell=plat,
                 scaled_positions=positions)

def write_lmto(filename, cell):
    with open(filename, 'w') as f:
        f.write(get_lmto_structure(cell))

def write_supercells_with_displacements(supercell,
                                        cells_with_displacements, ext):
    write_lmto('supercell.' + ext, supercell)
    for i, cell in enumerate(cells_with_displacements):
        write_lmto('supercell-%03d.' % (i + 1) + ext, cell)

def get_lmto_structure(cell):
    lattice = cell.get_cell()
    (num_atoms,
     symbols,
     scaled_positions,
     sort_list) = sort_positions_by_symbols(cell.get_chemical_symbols(),
                                            cell.get_scaled_positions())
    
    lines = '% site-data vn=3.0 xpos fast io=62'
    lines += ' nbas=%d' % sum(num_atoms)
    lines += ' alat=1.0'
    lines += ' plat=' + (' %10.7f' * 9 + '\n') % tuple(lattice.ravel())
    lines += '#' + '                        ' + 'pos'
    lines += '                                   ' + 'vel'
    lines += '                                    ' + 'eula'
    lines += '                   ' + 'vshft  PL rlx\n'
    count = 0
    for n in range(len(num_atoms)):
        i = 0
        while i < num_atoms[n]:
            lines += ' ' + symbols[n]
            for x in range(3):
                lines += 3*' ' + '%10.7f' % scaled_positions[count, x]
            for y in range(7):
                lines += 3*' ' + '%10.7f' % 0
            lines += ' 0 111'
            lines += '\n'
            i += 1; count += 1

    return lines
    

class LMTOIn:
    def __init__(self, lines):
        self._set_methods = {'atoms': self._set_atoms, 
                             'plat':  self._set_plat,
                             'alat':  self._set_alat}
        self._tags = {'atoms': None, 
                      'plat':  None,
                      'alat':  1.0}

    def _set_atoms(self, lines):
        spfnames = []
        positions = []
        for i in lines:
            if i.strip().startswith('%'):
                continue
            elif i.strip().startswith('#'):
                continue
            else:
                spfnames.append(i.split()[0])
                positions.append([float(x) for x in i.split()[1:4]])
        self._tags['atoms'] = {'spfnames':  spfnames,
                               'positions': positions}

    def _set_plat(self, lines):
        plat = []
        for i in lines:
            if i.strip().startswith('%'):
                index = i.split().index('plat=')
                j = 1
                while j < 10:
                    plat.append([
                        float(x) for x in i.split()[index+j:index+j+3]])
                    j += 3

        self._tags['plat'] = plat

    def _set_alat(self, lines):
        for i in lines:
            if i.strip().startswith('%'):
                header = i.split()
                for j in header:
                    if j.startswith('alat'):
                        alat = float(j.split('=')[1])

        self._tags['alat'] = alat

    def _get_variables(self, lines):
        self._set_atoms(lines)
        self._set_plat(lines)
        self._set_alat(lines)
        return self._tags

if __name__ == '__main__':
    import sys
    from phonopy.structure.symmetry import Symmetry
    cell = read_lmto(sys.argv[1])
    symmetry = Symmetry(cell)
    print('# %s' % symmetry.get_international_table())
    print(get_elk_structure(cell, sp_filenames=sp_filenames))
