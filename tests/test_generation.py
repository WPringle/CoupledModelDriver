from datetime import datetime, timedelta
import logging
import os
from os import PathLike
from pathlib import Path
import tarfile

from adcircpy import Tides
from adcircpy.forcing.waves.ww3 import WaveWatch3DataForcing
from adcircpy.forcing.winds.atmesh import AtmosphericMeshForcing
import appdirs
from nemspy import ModelingSystem
from nemspy.model import ADCIRCEntry, AtmosphericMeshEntry, WaveMeshEntry
import pytest
import wget

from coupledmodeldriver.adcirc import write_adcirc_configurations
from coupledmodeldriver.job_script import Platform

NEMS_PATH = 'NEMS.x'
ADCPREP_PATH = 'adcprep'

DATA_DIRECTORY = Path(__file__).parent / 'data'

INPUT_DIRECTORY = DATA_DIRECTORY / 'input'

MESH_URLS = {
    'shinnecock': {
        'ike': 'https://www.dropbox.com/s/1wk91r67cacf132/NetCDF_shinnecock_inlet.tar.bz2?dl=1',
    },
}


def test_local_shinnecock_ike():
    platform = Platform.LOCAL
    mesh = 'shinnecock'
    storm = 'ike'
    adcirc_processors = 11

    input_directory = Path('.') / 'input' / f'{mesh}_{storm}'
    mesh_directory = download_mesh(mesh, storm, input_directory)
    forcings_directory = input_directory / 'forcings'

    output_directory = Path('.') / 'output' / f'{platform.name.lower()}_{mesh}_{storm}'
    reference_directory = Path('.') / 'reference' / f'{platform.name.lower()}_{mesh}_{storm}'

    runs = {f'test_case_1': (None, None)}

    nems = ModelingSystem(
        start_time=datetime(2008, 8, 23),
        end_time=datetime(2008, 8, 23) + timedelta(days=14.5),
        interval=timedelta(hours=1),
        atm=AtmosphericMeshEntry(forcings_directory / 'wind_atm_fin_ch_time_vec.nc'),
        wav=WaveMeshEntry(forcings_directory / 'ww3.Constant.20151214_sxy_ike_date.nc'),
        ocn=ADCIRCEntry(adcirc_processors),
    )

    nems.connect('ATM', 'OCN')
    nems.connect('WAV', 'OCN')
    nems.sequence = [
        'ATM -> OCN',
        'WAV -> OCN',
        'ATM',
        'WAV',
        'OCN',
    ]

    tidal_forcing = Tides()
    tidal_forcing.use_all()
    wind_forcing = AtmosphericMeshForcing(nws=17, interval_seconds=3600)
    wave_forcing = WaveWatch3DataForcing(nrs=5, interval_seconds=3600)

    write_adcirc_configurations(
        output_directory=output_directory,
        fort13_filename=None,
        fort14_filename=mesh_directory,
        nems=nems,
        platform=platform,
        runs=runs,
        nems_executable=NEMS_PATH,
        adcprep_executable=ADCPREP_PATH,
        forcings=[tidal_forcing, wind_forcing, wave_forcing],
        spinup=timedelta(days=12.5),
        email_address='example@email.gov',
        overwrite=True,
        verbose=True,
    )

    check_reference_directory(
        DATA_DIRECTORY / output_directory, DATA_DIRECTORY / reference_directory
    )


def test_hera_shinnecock_ike():
    platform = Platform.HERA
    mesh = 'shinnecock'
    storm = 'ike'
    adcirc_processors = 15 * platform.value['processors_per_node']

    input_directory = Path('.') / 'input' / f'{mesh}_{storm}'
    mesh_directory = download_mesh(mesh, storm, input_directory)
    forcings_directory = input_directory / 'forcings'

    output_directory = Path('.') / 'output' / f'{platform.name.lower()}_{mesh}_{storm}'
    reference_directory = Path('.') / 'reference' / f'{platform.name.lower()}_{mesh}_{storm}'

    runs = {f'test_case_1': (None, None)}

    nems = ModelingSystem(
        start_time=datetime(2008, 8, 23),
        end_time=datetime(2008, 8, 23) + timedelta(days=14.5),
        interval=timedelta(hours=1),
        atm=AtmosphericMeshEntry(forcings_directory / 'wind_atm_fin_ch_time_vec.nc'),
        wav=WaveMeshEntry(forcings_directory / 'ww3.Constant.20151214_sxy_ike_date.nc'),
        ocn=ADCIRCEntry(adcirc_processors),
    )

    nems.connect('ATM', 'OCN')
    nems.connect('WAV', 'OCN')
    nems.sequence = [
        'ATM -> OCN',
        'WAV -> OCN',
        'ATM',
        'WAV',
        'OCN',
    ]

    tidal_forcing = Tides()
    tidal_forcing.use_all()
    wind_forcing = AtmosphericMeshForcing(nws=17, interval_seconds=3600)
    wave_forcing = WaveWatch3DataForcing(nrs=5, interval_seconds=3600)

    write_adcirc_configurations(
        output_directory=output_directory,
        fort13_filename=None,
        fort14_filename=mesh_directory,
        nems=nems,
        platform=platform,
        runs=runs,
        nems_executable=NEMS_PATH,
        adcprep_executable=ADCPREP_PATH,
        forcings=[tidal_forcing, wind_forcing, wave_forcing],
        spinup=timedelta(days=12.5),
        email_address='example@email.gov',
        overwrite=True,
        verbose=True,
    )

    check_reference_directory(
        DATA_DIRECTORY / output_directory, DATA_DIRECTORY / reference_directory
    )


def test_stampede2_shinnecock_ike():
    platform = Platform.STAMPEDE2
    mesh = 'shinnecock'
    storm = 'ike'
    adcirc_processors = 15 * platform.value['processors_per_node']

    input_directory = Path('.') / 'input' / f'{mesh}_{storm}'
    mesh_directory = download_mesh(mesh, storm, input_directory)
    forcings_directory = input_directory / 'forcings'

    output_directory = Path('.') / 'output' / f'{platform.name.lower()}_{mesh}_{storm}'
    reference_directory = Path('.') / 'reference' / f'{platform.name.lower()}_{mesh}_{storm}'

    runs = {f'test_case_1': (None, None)}

    nems = ModelingSystem(
        start_time=datetime(2008, 8, 23),
        end_time=datetime(2008, 8, 23) + timedelta(days=14.5),
        interval=timedelta(hours=1),
        atm=AtmosphericMeshEntry(forcings_directory / 'wind_atm_fin_ch_time_vec.nc'),
        wav=WaveMeshEntry(forcings_directory / 'ww3.Constant.20151214_sxy_ike_date.nc'),
        ocn=ADCIRCEntry(adcirc_processors),
    )

    nems.connect('ATM', 'OCN')
    nems.connect('WAV', 'OCN')
    nems.sequence = [
        'ATM -> OCN',
        'WAV -> OCN',
        'ATM',
        'WAV',
        'OCN',
    ]

    tidal_forcing = Tides()
    tidal_forcing.use_all()
    wind_forcing = AtmosphericMeshForcing(nws=17, interval_seconds=3600)
    wave_forcing = WaveWatch3DataForcing(nrs=5, interval_seconds=3600)

    write_adcirc_configurations(
        output_directory=output_directory,
        fort13_filename=None,
        fort14_filename=mesh_directory,
        nems=nems,
        platform=platform,
        runs=runs,
        nems_executable=NEMS_PATH,
        adcprep_executable=ADCPREP_PATH,
        forcings=[tidal_forcing, wind_forcing, wave_forcing],
        spinup=timedelta(days=12.5),
        email_address='example@email.gov',
        overwrite=True,
        verbose=True,
    )

    check_reference_directory(
        DATA_DIRECTORY / output_directory, DATA_DIRECTORY / reference_directory
    )


@pytest.fixture(scope='session', autouse=False)
def download_tpxo():
    tpxo_filename = Path(appdirs.user_data_dir('tpxo')) / 'h_tpxo9.v1.nc'
    if not tpxo_filename.exists():
        url = 'https://www.dropbox.com/s/uc44cbo5s2x4n93/h_tpxo9.v1.tar.gz?dl=1'
        extract_download(url, tpxo_filename.parent, ['h_tpxo9.v1.nc'])


@pytest.fixture(scope='session', autouse=True)
def data_directory():
    os.chdir(DATA_DIRECTORY)


def download_mesh(
    mesh: str, storm: str, input_directory: PathLike = None, overwrite: bool = False
):
    try:
        url = MESH_URLS[mesh][storm]
    except KeyError:
        raise NotImplementedError(f'no test mesh available for "{mesh} {storm}"')

    if input_directory is None:
        input_directory = INPUT_DIRECTORY / f'{mesh}_{storm}'

    mesh_directory = input_directory / 'mesh'
    if not (mesh_directory / 'fort.14').exists() or overwrite:
        logging.info(f'downloading mesh files to {mesh_directory}')
        extract_download(url, mesh_directory, ['fort.13', 'fort.14'])

    return mesh_directory


def extract_download(
    url: str, directory: PathLike, filenames: [str] = None, overwrite: bool = False
):
    if not isinstance(directory, Path):
        directory = Path(directory)

    if filenames is None:
        filenames = []

    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)

    temporary_filename = directory / 'temp.tar.gz'
    logging.debug(f'downloading {url} -> {temporary_filename}')
    wget.download(url, f'{temporary_filename}')
    logging.debug(f'extracting {temporary_filename} -> {directory}')
    with tarfile.open(temporary_filename) as local_file:
        if len(filenames) > 0:
            for filename in filenames:
                if filename in local_file.getnames():
                    path = directory / filename
                    if not path.exists() or overwrite:
                        if path.exists():
                            os.remove(path)
                        local_file.extract(filename, directory)
        else:
            local_file.extractall(directory)

    os.remove(temporary_filename)


def check_reference_directory(test_directory: PathLike, reference_directory: PathLike):
    if not isinstance(test_directory, Path):
        test_directory = Path(test_directory)
    if not isinstance(reference_directory, Path):
        reference_directory = Path(reference_directory)

    for reference_filename in reference_directory.iterdir():
        if reference_filename.is_dir():
            check_reference_directory(
                test_directory / reference_filename.name, reference_filename
            )
        else:
            test_filename = test_directory / reference_filename.name
            with open(test_filename) as test_file, open(reference_filename) as reference_file:
                assert test_file.readlines()[1:] == reference_file.readlines()[1:]
