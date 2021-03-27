#! /usr/bin/env python

from datetime import datetime, timedelta
from pathlib import Path
import sys

from adcircpy import Tides
from adcircpy.forcing.tides.tides import TidalSource
from adcircpy.forcing.waves.ww3 import WaveWatch3DataForcing
from adcircpy.forcing.winds.atmesh import AtmosphericMeshForcing
from nemspy import ModelingSystem
from nemspy.model import ADCIRCEntry, AtmosphericMeshEntry, \
    WaveMeshEntry
import numpy

sys.path.append((Path(__file__).parent / '..').absolute())

from coupledmodeldriver.adcirc import write_adcirc_configurations
from coupledmodeldriver.platforms import Platform

# paths to compiled `NEMS.x` and `adcprep`
NEMS_EXECUTABLE = '/scratch2/COASTAL/coastal/save/shared/repositories/ADC-WW3-NWM-NEMS/ALLBIN_INSTALL/NEMS-adcirc_atmesh_ww3data.x'
ADCPREP_EXECUTABLE = '/scratch2/COASTAL/coastal/save/shared/repositories/ADC-WW3-NWM-NEMS/ALLBIN_INSTALL/adcprep'

# directory containing input ADCIRC mesh nodes (`fort.14`) and (optionally) mesh values (`fort.13`)
MESH_DIRECTORY = (
    Path('/scratch2/COASTAL/coastal/save/shared/models') / 'meshes' / 'shinnecock' / 'grid_v1'
)

# directory containing input atmospheric mesh forcings (`wind_atm_fin_ch_time_vec.nc`) and WaveWatch III forcings (`ww3.Constant.20151214_sxy_ike_date.nc`)
FORCINGS_DIRECTORY = (
    Path('/scratch2/COASTAL/coastal/save/shared/models') / 'forcings' / 'shinnecock' / 'ike'
)

# directory to which to write configuration
OUTPUT_DIRECTORY = (
    Path(__file__).parent.parent
    / 'data'
    / 'configuration'
    / 'hera_shinnecock_ike_perturbed_mannings_n'
)

HAMTIDE_DIRECTORY = '/scratch2/COASTAL/coastal/save/shared/models/forcings/tides/hamtide'
TPXO_FILENAME = '/scratch2/COASTAL/coastal/save/shared/models/forcings/tides/h_tpxo9.v1.nc'

if __name__ == '__main__':
    platform = Platform.HERA
    adcirc_processors = 11

    # dictionary defining runs with ADCIRC value perturbations - in this case, a range of Manning's N values
    range = [0.016, 0.08]
    mean = numpy.mean(range)
    std = mean / 3
    values = numpy.random.normal(mean, std, 5)
    runs = {
        f'mannings_n_{mannings_n:.3}': (mannings_n, 'mannings_n_at_sea_floor')
        for mannings_n in values
    }

    # initialize `nemspy` configuration object with forcing file locations, start and end times,  and processor assignment
    nems = ModelingSystem(
        start_time=datetime(2008, 8, 23),
        end_time=datetime(2008, 8, 23) + timedelta(days=14.5),
        interval=timedelta(hours=1),
        atm=AtmosphericMeshEntry(FORCINGS_DIRECTORY / 'wind_atm_fin_ch_time_vec.nc'),
        wav=WaveMeshEntry(FORCINGS_DIRECTORY / 'ww3.Constant.20151214_sxy_ike_date.nc'),
        ocn=ADCIRCEntry(adcirc_processors),
    )

    # describe connections between coupled components
    nems.connect('ATM', 'OCN')
    nems.connect('WAV', 'OCN')
    nems.sequence = [
        'ATM -> OCN',
        'WAV -> OCN',
        'ATM',
        'WAV',
        'OCN',
    ]

    # initialize `adcircpy` forcing objects
    tidal_forcing = Tides(tidal_source=TidalSource.TPXO, resource=TPXO_FILENAME)
    tidal_forcing.use_all()
    wind_forcing = AtmosphericMeshForcing(nws=17, interval_seconds=3600)
    wave_forcing = WaveWatch3DataForcing(nrs=5, interval_seconds=3600)

    # send run information to `adcircpy` and write the resulting configuration to output directory
    write_adcirc_configurations(
        output_directory=OUTPUT_DIRECTORY,
        fort13_filename=None,
        fort14_filename=MESH_DIRECTORY,
        nems=nems,
        platform=platform,
        runs=runs,
        nems_executable=NEMS_EXECUTABLE,
        adcprep_executable=ADCPREP_EXECUTABLE,
        forcings=[tidal_forcing, wind_forcing, wave_forcing],
        spinup=timedelta(days=12.5),
        wall_clock_time=timedelta(hours=0.5),
        email_address='example@email.gov',
        overwrite=True,
        verbose=True,
    )
