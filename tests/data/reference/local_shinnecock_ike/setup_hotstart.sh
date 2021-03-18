#!/bin/bash --login

ln -sf output/local_shinnecock_ike/nems.configure.hotstart ./nems.configure
ln -sf output/local_shinnecock_ike/model_configure.hotstart ./model_configure
ln -sf output/local_shinnecock_ike/atm_namelist.rc.hotstart ./atm_namelist.rc
ln -sf output/local_shinnecock_ike/config.rc.hotstart ./config.rc

ln -sf output/local_shinnecock_ike/coldstart/fort.67.nc ./fort.67.nc
