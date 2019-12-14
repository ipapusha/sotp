#!/bin/sh

# downloads ephemerides from NAIF
# (only if they already do not exist)

# leapseconds
wget --no-clobber https://naif.jpl.nasa.gov/pub/naif/generic_kernels/lsk/naif0012.tls
wget --no-clobber https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de430.bsp

