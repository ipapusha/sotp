import spiceypy as spice
import flask
from flask import jsonify

import datetime

# initialize
app = flask.Flask(__name__)

# load ephemerides
spk_file = 'ephem/de430.bsp'
lsk_file = 'ephem/naif0012.tls'
spice.furnsh([lsk_file, spk_file])


@app.route('/')
def sotp():
    return 'Hello'


@app.route('/planets')
def get_planets(spk=spk_file):
    ids = list(spice.spkobj(spk))
    names = [spice.bodc2n(i) for i in ids]
    return jsonify({'ids': ids, 'names': names, 'spk': spk})


@app.route('/now')
def current_time():
    """ returns the current time in UTC and J2000 systems """
    # determine UTC time in ISO 8601 format
    # outputs: 2019-12-14T00:35:35.119520+00:00
    now = datetime.datetime.now(datetime.timezone.utc)
    utc_time = now.isoformat()
    assert str(now.tzinfo) == 'UTC'
    assert utc_time.endswith('+00:00')
    assert utc_time.find('T') > 0

    # convert ISO 8601 format to a string SPICE can parse
    # outputs: 2019-12-14 00:35:35.119520 UTC
    date, time_pz = utc_time.split('T')
    time = time_pz[:-6]
    spice_time = date + ' ' + time + ' UTC'

    # convert SPICE time to seconds past J2000
    et = spice.str2et(spice_time)

    return jsonify({'time': spice_time, 'et': et})
