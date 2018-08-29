.. _lmto_interface:

LMTO (Questaal) phonopy interface
=========================================

This is a tutorial for the interface between phonopy & the Questaal 
(LMTO) electronic structure codes https://www.questaal.org/.

Supported LMTO tokens
---------------------------

The interface uses Questaal `site` files. Such files have only a small amount
of information within them relating to the calculation. 

At present,
the interface requires the use of fractional co-ordinates. Since
phonopy is capable of handling cartesian co-ordinates such an
extension will be realised soon. 

::

   XPOS, ATOM, ALAT, PLAT

How to run
----------

The following is a walkthrough for a phonopy calculation with Questaal / LMTO.

Questaal uses a 'back to front' extension, with the common extension to files usually specifying the material (i.e. ``Si``).
We assume that you are starting (at least) with a ``ctrl.ext`` file for the material of interest.

1) Create a site file with the Questaal supercell maker, ``lmscell``. 
   The following outputs a unit-cell via the supercell maker and a unit matrix.

   ::

      % echo 'm 1 0 0 0 1 0 0 0 1' | lmscell --wsitex ext

   This will write ``site.ext`` to disk in the current directory. Note
   that this site file will be written in fractional co-ordinates.   

2) Phonopy can now read this site file, and generate the supercells with the displacements,

   ::

      % phonopy --lmto -d --dim='2 2 2' -c site.ext

   In this example, 2x2x2 supercells are created. ``supercell.ext``
   and ``supercell-xxx.ext`` (``xxx`` are integers) correspond to the
   perfect supercell and supercells with displacements,
   respectively. These supercell files, are Questaal `site` files ready to be
   used in ``ctrl.ext``. A file named ``disp.yaml`` is also created in
   the current directory. This file describes the 
   displacements taken by phonopy.

3) Run the calculations within your choice of electronic structure method in Questaal. 
   The aim is to generate ``forces-xxx.ext`` for every ``supercell-xxx.ext`` file that Phonopy generated. 
   This currently requires a manual editing of ``ctrl.ext``, to override ``SPEC`` and ``STRUC`` sections.
   
   Forces are output via a tag to the LMTO programs: ``--wforce=force``, which will write to `force.ext`.
      
   Phonopy will require these force files to be read in the next step.

4) Create ``FORCE_SETS`` by

   ::
   
     % phonopy --lmto -f force-001.ext force-002.ext  ...

   To run this command, ``disp.yaml`` has to be located in the current
   directory because the atomic displacements are written into the
   ``FORCE_SETS`` file. 
   
5) Run post-process of phonopy with the initial `site` file for the unit cell, generated in the first step.

   ::

      % phonopy --lmto -c site.ext -p band.conf
   
   or 

   ::
   
      % phonopy --lmto -c site.ext --dim="2 2 2" [other-OPTIONS] [setting-file]

