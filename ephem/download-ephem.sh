#!/bin/sh

# downloads ephemerides from JPL/NAIF
# (if they are not already available)

# leapseconds kernel
wget --no-clobber https://naif.jpl.nasa.gov/pub/naif/generic_kernels/lsk/naif0012.tls

# barycenters of all planets, inner planets, and the moon
wget --no-clobber https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de430.bsp

