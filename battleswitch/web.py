from flask import current_app, redirect, request, session, url_for, jsonify
from werkzeug.exceptions import BadRequest, Unauthorized

from battleswitch import app, GameState, CellState, StateLock
from battleswitch.snmp import run_probe_loop

logger = app.logger


@app.route('/')
def get_root():
    return redirect(url_for('static', filename='start.html'), 303)


@app.route('/game')
def get_game():
    return redirect(url_for('static', filename='battleswitch.html'), 303)


@app.route('/config')
def get_config():
    width = current_app.config['BOARD_WIDTH']
    height = len(current_app.config['SWITCHES'][0]['interfaces']) / width
    return jsonify(config={
        'board': {
            'width': width,
            'height': height,
        },
        'ships': current_app.config['SHIPS'],
    })


@app.route('/player', methods=['POST'])
def set_player():
    player = request.form.get('player')
    if player not in ('0', '1'):
        raise BadRequest("Invalid player")
    session['player'] = int(player)
    return redirect('/game', 303)


def get_current_player():
    if 'player' not in session:
        raise Unauthorized()
    player = session['player']
    if player not in (0, 1):
        raise BadRequest("Invalid player")
    return player


@app.route('/toggle', methods=['POST'])
def toggle_cell():
    cell = request.form.get('cell')
    try:
        cell = int(cell)
    except (ValueError, TypeError):
        raise BadRequest()
    player = get_current_player()
    try:
        cell_state = current_app.cell_state[player][cell]
    except KeyError:
        raise BadRequest("Invalid cell")
    with StateLock:
        if current_app.game_state != GameState.PREPARING:
            raise BadRequest("Not in preparing state")
        current_app.ready_state[player] = False
        current_app.cell_state[player][cell] = CellState.EMPTY if cell_state is CellState.PRESENT else CellState.PRESENT
    return ''


@app.route('/reset', methods=['POST'])
def reset():
    setup_state()
    return redirect(url_for('static', filename='start.html'), 303)


@app.route('/state')
def get_state():
    player = get_current_player()
    other = [1, 0][player]
    if current_app.game_state == GameState.PREPARING and current_app.ready_state[player]:
        game_state = 'READY'
    else:
        game_state = current_app.game_state.name
    state = {
        'state': game_state,
        'own': [cell_state.value for cell_state in current_app.cell_state[player]],
        'enemy': [CellState.HIT.value if state is CellState.HIT.value else CellState.EMPTY.value for state in
                  current_app.cell_state[other]],
    }
    return jsonify(state=state)


@app.route('/ready', methods=['POST'])
def ready():
    player = get_current_player()
    with StateLock:
        if current_app.game_state != GameState.PREPARING:
            raise BadRequest("Not in PREPARING state")
        # TODO: Do some checks.
        current_app.ready_state[player] = True
        if all(current_app.ready_state):
            current_app.game_state = GameState.RUNNING
            app.probe_loop = run_probe_loop()


@app.before_first_request
def first_run():
    app.probe_loop = None
    setup_state()


def setup_state():
    with StateLock:
        switches = current_app.config['SWITCHES']
        current_app.game_state = GameState.PREPARING
        current_app.cell_state = [
            [CellState.EMPTY for _ in switch['interfaces']] for switch in switches
        ]
        current_app.ready_state = [False for _ in switches]
        if app.probe_loop is not None:
            if app.probe_loop.is_alive():
                app.probe_loop.stop.set()
                app.probe_loop.join()
            app.probe_loop = None
