import flask
from flask import jsonify, Response

import spiceypy as spice
from spiceypy.utils.support_types import SpiceyError
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

import datetime
import io

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


def inner(naif_id):
    """ returns true if inner planet or the sun"""
    return (naif_id in [0, 1, 2, 3, 4, 10, 199, 299, 399, 499])


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


# ======================
# Data-generating routes
# ======================


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


# ======================
# Figure-creating routes
# ======================

@app.route('/inner_planets.png', defaults={'et': None})
@app.route('/inner_planets.png/<int:et>')
@app.route('/inner_planets.png/<float:et>')
def inner_planets_png(et):
    fig = planets_fig(draw_inner=True, et=et)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@app.route('/outer_planets.png', defaults={'et': None})
@app.route('/outer_planets.png/<int:et>')
@app.route('/outer_planets.png/<float:et>')
def outer_planets_png(et):
    # TODO: add ephemeris time
    fig = planets_fig(draw_inner=False, et=et)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


def planets_fig(draw_inner=True, et=None):
    # plot position
    if et is None:
        et = current_et()
    ets = np.linspace(et, et + 365.25 * 12.0 / 12.0 * spice.spd(), 365)
    naif_ids_inner = [10, 199, 299, 399, 4]
    naif_ids_outer = [10, 199, 299, 399, 4, 5, 6, 7, 8, 9]
    mfac_inner = {10: 20, 199: 1.5, 299: 1.2, 399: 1.2, 4: 1.1}
    mfac_outer = {
        10: 1.1,
        199: 1.1,
        299: 1.1,
        399: 1.1,
        4: 2.0,
        5: 1.1,
        6: 1.07,
        7: 1.045,
        8: 0.975,
        9: 1.02
    }

    # set up figure size
    if draw_inner:
        fig = Figure(figsize=(1.0 * 8.0, 1.0 * 8.0))
    else:
        fig = Figure(figsize=(1.5 * 6.0, 2 * 6.0))
    #fig.patch.set_fill(False)
    ax = fig.add_subplot(1, 1, 1)

    if draw_inner:
        # draw the inner planets only
        for naif_id in naif_ids_inner:
            # determine state over a bit of time
            targ = spice.bodc2n(naif_id)
            obs = 'SOLAR SYSTEM BARYCENTER'
            state, lt = spice.spkezr(targ, ets, 'J2000', 'NONE', obs)
            state = np.vstack(state)
            avg_speed = np.linalg.norm(state[:, 3:], axis=1).mean()

            # plot the position over time
            ax.plot(state[:, 0], state[:, 1], zorder=1)

            # label everything
            if inner(naif_id):
                ax.scatter(state[0, 0], state[0, 1], label=targ, zorder=2)
                ax.text(mfac_inner[naif_id] * state[0, 0],
                        mfac_inner[naif_id] * state[0, 1],
                        '{}'.format(targ),
                        verticalalignment='top')
    else:
        # draw inner and outer planets
        for naif_id in naif_ids_outer:
            # determine state over a bit of time
            targ = spice.bodc2n(naif_id)
            obs = 'SOLAR SYSTEM BARYCENTER'
            state, lt = spice.spkezr(targ, ets, 'J2000', 'NONE', obs)
            state = np.vstack(state)
            avg_speed = np.linalg.norm(state[:, 3:], axis=1).mean()

            # plot the position over time
            ax.plot(state[:, 0], state[:, 1], zorder=1)

            # draw all planets, but label only the outer planets
            if inner(naif_id):
                ax.scatter(state[0, 0], state[0, 1], label=targ, zorder=2)
            else:
                horizontalalignment = 'right' if 'NEPTUNE' in targ else 'left'
                ax.scatter(state[0, 0], state[0, 1], zorder=2)
                ax.text(mfac_outer[naif_id] * state[0, 0],
                        mfac_outer[naif_id] * state[0, 1],
                        '{}\n{:.2f} km/s'.format(targ, avg_speed),
                        verticalalignment='top',
                        horizontalalignment=horizontalalignment)

    # set plot options
    ax.set_aspect('equal', 'box')
    ax.set_xlabel('x [km]')
    ax.set_ylabel('y [km]')
    if draw_inner:
        ax.set_title('State of the Inner Planets')
    else:
        ax.set_title('State of the Outer Planets')
    #ax.grid(linestyle=':', linewidth=0.5)

    # description
    ax.text(0.0 + 0.02,
            1.0 - 0.02,
            '\n'.join([
                'Solid line is {0:.2f} Earth days'.format(
                    (ets[-1] - ets[0]) / spice.spd()),
                'Source: DE430 ephemeris', 'Frame: J2000',
                'Date: ' + spice.timout(ets[0], 'YYYY-MM-DD')
            ]),
            fontsize=12,
            horizontalalignment='left',
            verticalalignment='top',
            transform=ax.transAxes)

    return fig
