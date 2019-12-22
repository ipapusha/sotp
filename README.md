# SOTP: State of the Planets
Exposes key parameters from the DE430 ephemeris as a REST API, such as the
current position and velocity of the planets (in the J2000 frame), and draws a
picture of the solar system to scale.

# Installation
```bash
# create virtual environment and download dependencies
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ make init

# run flask test server
(venv) $ make run
```

# Endpoints
Endpoint                | Method              | Function
------------------------|---------------------|-------------------
`/`                     |(GET, HEAD, OPTIONS) | get_root
`/now`                  |(GET, HEAD, OPTIONS) | get_now
`/planets`              |(GET, HEAD, OPTIONS) | get_planets
`/inner_planets.png`    |(GET, HEAD, OPTIONS) | inner_planets_png
`/outer_planets.png`    |(GET, HEAD, OPTIONS) | outer_planets_png
`/state/<naif_id>/<et>` |(GET, HEAD, OPTIONS) | get_state
`/state/<naif_id>/<et>` |(GET, HEAD, OPTIONS) | get_state
`/state/<naif_id>`      |(GET, HEAD, OPTIONS) | get_state


# Examples
An image of all the planets (at the current time, TDB) is obtained through the
`.png` endpoints. For example, the URL `localhost:5000/inner_planets.png` shows
the inner planets.

The JSON endpoints can be accessed from the command line; for example `curl -s
localhost:5000/now` returns a JSON object containing the current TDB time, UTC
time, and the time picture used to produce the UTC time from the TDB time.

`/now`
```json
{
  "et": 630223895.187479, 
  "pictur": "YYYY-MM-DD HR:MN:SC.###### UTC ::RND ::UTC", 
  "time": "2019-12-21 18:10:26.003865 UTC"
}
```

Key parameters of the Earth (an inner planet), such as its distance, speed, and
position/velocity vectors relative to the solar system barycenter at the current
TDB time is available from `/state`.

`/state/399`
```json
{
  "abcorr": "NONE", 
  "dist": 148274490.74003318, 
  "et": 630224046.005019, 
  "lt": 494.59046344665944, 
  "naif_id": 399, 
  "obs": "SOLAR SYSTEM BARYCENTER", 
  "radii": [
    6378.1366, 
    6378.1366, 
    6356.7519
  ], 
  "ref": "J2000", 
  "speed": 30.295217333585782, 
  "state": [
    1235847.5788177096, 
    136036068.16893277, 
    58974447.365919374, 
    -30.294127766281377, 
    0.23536043831059478, 
    0.10306130939597859
  ], 
  "targ": "EARTH", 
  "time": "2019-12-21 18:12:56.821405 UTC"
}
```

A list of the available ephemeris objects and their corresponding NAIF IDs are
obtained with `/planets`.

`/planets`
```json
{
  "naif_ids": [
    1, 
    2, 
    3, 
    4, 
    5, 
    6, 
    7, 
    8, 
    9, 
    10, 
    199, 
    299, 
    301, 
    399
  ], 
  "naif_names": [
    "MERCURY BARYCENTER", 
    "VENUS BARYCENTER", 
    "EARTH BARYCENTER", 
    "MARS BARYCENTER", 
    "JUPITER BARYCENTER", 
    "SATURN BARYCENTER", 
    "URANUS BARYCENTER", 
    "NEPTUNE BARYCENTER", 
    "PLUTO BARYCENTER", 
    "SUN", 
    "MERCURY", 
    "VENUS", 
    "MOON", 
    "EARTH"
  ], 
  "spk": "ephem/de430.bsp"
}
```

# Helpful Links
* <https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/MATLAB/index.html>
* <https://spiceypy.readthedocs.io/>
* <https://github.com/opentracing-contrib/python-flask/blob/master/Makefile>
