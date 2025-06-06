#!/usr/bin/env python3
# Copyright (c) 2016-2024 Association of Universities for Research in Astronomy, Inc. (AURA)
# For license information see LICENSE or https://opensource.org/licenses/BSD-3-Clause

import os, sys

# Requires https://github.com/andrewwstephens/pyexplore
# sys.path.append(os.path.join(os.environ['PYEXPLORE']))
# Uncomment the next three lines to run from the pycharm terminal, better to redefine PYTHONPATH in the terminal
# sys.path.append(os.path.join(os.environ['HOME'], 'python', 'pyexplore'))
# sys.path.append(os.path.join(os.environ['HOME'], 'python', 'scheduler'))
# sys.path.append(os.path.join(os.environ['HOME'], 'python', 'lucupy'))
# from pyexplore import explore

from scheduler.core.programprovider.gpp.gppprogramprovider import GppProgramProvider
from scheduler.core.sources.sources import Sources
from lucupy.minimodel.observation import ObservationClass

if __name__ == '__main__':
    # List programs
    # TODO change pyexplore to other api query
    # programs = explore.programs()
    programs = []
    progid = None
    for p in programs:
        print(f'{p.id}: {p.name}')
        progid = p.id if progid is None else progid
    print("")

    # Information from the first program
    # print(progid)
    # TODO change pyexplore to other api query
    # prog = explore.program(progid)
    prog = {}
    # print(prog)
    print(f'{progid} {prog.reference}: {prog.name} {prog.pi.orcid_family_name}')
    print("")

    # Query obserations appropriate for the scheduler (READY/ONGOING)
    sources = Sources()
    provider = GppProgramProvider(frozenset([ObservationClass.SCIENCE]), sources)

    # TODO change pyexplore to other api query
    # obs_for_sched = explore.observations_for_scheduler(include_deleted=False)
    obs_for_sched = []
    for o in obs_for_sched:
        print(f'{o.id}: {o.title} {o.active_status} {o.status}')
        # TODO change pyexplore to other api query
        # obs = explore.observation(o.id)
        obs = {}

        obs_mini = provider.parse_observation(data=obs.__dict__, num=(0,0), program_id=obs.program.id)
        print(obs_mini.targets)
        print(obs_mini.guiding)
        print('Output Atoms')
        for atom in obs_mini.sequence:
            print(atom.id, atom.obs_mode.name, atom.exec_time, atom.resources, atom.wavelengths)

        print()
