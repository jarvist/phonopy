.. _lmto_interface:

LM & phonopy calculation
=========================================

This is a tutorial for the interface between phonopy & Mark van
Schilfgaarde's electronic structure codes http://www.lmsuite.org/.

Supported LM tokens
---------------------------

The interface uses LM suite site files. Such files have only a small amount
of information within them relating to the calculation. At present,
the interface requires the use of fractional co-ordinates. Since
phonopy is capable of handling cartesian co-ordinates such an
extension will be realised soon. 

::

   XPOS, ATOM, ALAT, PLAT

How to run
----------

The following is a walkthrough for a phonopy calculation with LM:

1) Create a site file with the LM suite supercell maker, *lmscell*. For
   instance, use this command,

   ::

      % echo 'm 1 0 0 0 1 0 0 0 1' | lmscell --wsitex ext

   This will write ``site.ext`` to disk in the current directory. Note
   that this site file will be written in fractional co-ordinates. At
   present, the LM interface supports just fractional co-ordinates.  

2) Read the LM site file and create supercells with a command of the
   form,

   ::

      % phonopy --lmto -d --dim='2 2 2' -c site.ext

   In this example, 2x2x2 supercells are created. ``supercell.ext``
   and ``supercell-xxx.ext`` (``xxx`` are integers) correspond to the
   perfect supercell and supercells with displacements,
   respectively. These supercell files, are LM site files ready to be
   used in ``ctrl.ext``. A file named ``disp.yaml`` is also created in
   the current directory. This file contains information pertaining to
   displacements.

3) Next, run the calculation and be sure to use the ``--wforce=force``
   flag. This will write a file containing forces to disk. Phonopy
   will require this file to be read in the next step.

4) Create ``FORCE_SETS`` by

   ::
   
     % phonopy --lmto -f force-001.ext force-002.ext  ...

   To run this command, ``disp.yaml`` has to be located in the current
   directory because the atomic displacements are written into the
   ``FORCE_SETS`` file. 
   
5) Run post-process of phonopy with the LM site file for the unit cell
   used in the first step 

   ::

      % phonopy --lmto -c site.ext -p band.conf
   
   or 

   ::
   
      % phonopy --lmto -c site.ext --dim="2 2 2" [other-OPTIONS] [setting-file]

