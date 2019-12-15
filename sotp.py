import flask
from flask import jsonify
import numpy as np
import spiceypy as spice
from spiceypy.utils.support_types import SpiceyError


import datetime

# initialize
app = flask.Flask(__name__)

# load ephemerides
spk_file = 'ephem/de430.bsp'
lsk_file = 'ephem/naif0012.tls'
pck_files = ['ephem/pck00010.tpc', 'ephem/gm_de431.tpc']
spice.furnsh([lsk_file, spk_file])
spice.furnsh(pck_files)

# determine available naif_ids
naif_ids = list(spice.spkobj(spk_file))
naif_names = [spice.bodc2n(i) for i in naif_ids]

# default time picture
pictur = 'YYYY-MM-DD HR:MN:SC.###### UTC ::RND ::UTC'


def current_et():
    """ returns the current time in TDB """
    # determine UTC time in ISO 8601 format
    # outputs: 2019-12-14T00:35:35.119520+00:00
    now = datetime.datetime.now(datetime.timezone.utc)
    utc_time = now.isoformat()
    assert utc_time.endswith('+00:00')
    assert utc_time.find('T') > 0

    # convert ISO 8601 format to a string SPICE can parse
    # outputs: 2019-12-14 00:35:35.119520 UTC
    date, time_pz = utc_time.split('T')
    time = time_pz[:-6]
    spice_time = date + ' ' + time + ' UTC'

    # convert SPICE time to seconds past J2000
    et = spice.str2et(spice_time)
    return et


def target_state(naif_id, et=None):
    """ returns planet state/information in a dictionary """
    # current state
    if et is None:
        et = current_et()
    spice_time = spice.timout(et, pictur)
    targ = spice.bodc2n(naif_id)
    ref = 'J2000'
    abcorr = 'NONE'
    obs = 'SOLAR SYSTEM BARYCENTER'
    state, lt = spice.spkezr(targ, et, ref, abcorr, obs)
    dist = np.linalg.norm(state[0:3])
    speed = np.linalg.norm(state[3:6])
    state = list(state)

    # information about the body geometry
    try:
        _, radii = spice.bodvrd(targ, 'RADII', 3)
        radii = list(radii)
    except SpiceyError:
        radii = None

    return {
        'naif_id': naif_id,
        'targ': targ,
        'et': et,
        'time': spice_time,
        'ref': ref,
        'abcorr': abcorr,
        'obs': obs,
        'state': state,
        'dist': dist,
        'speed': speed,
        'lt': lt,
        'radii': radii
    }


@app.route('/')
def get_root():
    return str(app.url_map) + '\n'


@app.route('/planets')
def get_planets():
    return jsonify({
        'naif_ids': naif_ids,
        'naif_names': naif_names,
        'spk': spk_file
    })


@app.route('/state/<int:naif_id>', defaults={'et': None})
@app.route('/state/<int:naif_id>/<int:et>')
@app.route('/state/<int:naif_id>/<float:et>')
def get_state(naif_id, et):
    try:
        state = target_state(naif_id, et=et)
    except SpiceyError as e:
        flask.abort(400, str(e))

    return jsonify(state)


@app.route('/now')
def get_now():
    """ returns the current time in UTC and J2000 systems """
    et = current_et()
    spice_time = spice.timout(et, pictur)

    return jsonify({'time': spice_time, 'pictur': pictur, 'et': et})
