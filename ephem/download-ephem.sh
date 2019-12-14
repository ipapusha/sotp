#!/bin/sh

# downloads ephemerides from JPL/NAIF
# (if they are not already available)
WGET="wget --no-clobber"
NAIF_GENERIC="https://naif.jpl.nasa.gov/pub/naif/generic_kernels"

# leapseconds kernel
$WGET $NAIF_GENERIC/lsk/naif0012.tls

# barycenters of all planets, inner planets, and the moon
$WGET $NAIF_GENERIC/spk/planets/de430.bsp

# planetary geometry and gravity constants
$WGET $NAIF_GENERIC/pck/pck00010.tpc
$WGET $NAIF_GENERIC/pck/gm_de431.tpc

