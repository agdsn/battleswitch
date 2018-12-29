import itertools
import logging
import threading

from flask import current_app, Flask
from pyasn1.type.univ import Null
from pysnmp.hlapi import (
    CommunityData, ContextData, Integer32, ObjectIdentity, ObjectType, SnmpEngine,
    UdpTransportTarget, getCmd, setCmd,
)

from battleswitch import CellState, StateLock, ifAdminStatus, ifOperStatus, GameState

logger = logging.getLogger(__name__)


def keyfunc(interfaces):
    index_map = {if_index: pos for pos, if_index in enumerate(interfaces)}
    return index_map.__getitem__


def chunked(iterable, n):
    it = iter(iterable)
    chunk = tuple(itertools.islice(it, n))
    while chunk:
        yield chunk
        if len(chunk) < n:
            break
        chunk = tuple(itertools.islice(it, n))


def probe_oper_status(player):
    switch = current_app.config['SWITCHES'][player]
    address = switch['address']
    port = switch['port']
    logger.info("Probing status for player %d on switch %s:%d", player, address)
    engine = SnmpEngine()
    auth_data = CommunityData(switch['community'], mpModel=1)
    transport = UdpTransportTarget((address, port))
    interfaces = switch['interfaces']
    oper_states = []
    for chunk in chunked((ObjectType(ObjectIdentity(ifOperStatus.oid + (index,)), Null()) for index in interfaces), 24):
        cmd = getCmd(
            engine, auth_data, transport, ContextData(),
            *chunk
        )
        errorIndication, errorStatus, errorIndex, varBinds = next(cmd)
        if errorIndication is not None:
            raise Exception("SNMP error returned")
        oper_states.extend(ifOperStatus(int(value)) for identity, value in varBinds)
    with StateLock:
        for cell_state, (index, oper_state) in zip(current_app.cell_state[player], enumerate(oper_states)):
            if oper_state != ifOperStatus.up or cell_state == CellState.EMPTY:
                continue
            current_app.cell_state[player][index] = CellState.HIT
        if not any(cell_state == CellState.PRESENT for cell_state in current_app.cell_state[player]):
            current_app.game_state = GameState.OVER
            return True
    return False


def set_admin_status(player: int):
    switch = current_app.config['SWITCHES'][player]
    engine = SnmpEngine()
    auth_data = CommunityData(switch['community'], mpModel=1)
    transport = UdpTransportTarget((switch['address'], switch['port']))
    with StateLock:
        desired_state = list(zip(switch['interfaces'], current_app.cell_state[player]))
    for chunk in chunked((ObjectType(ObjectIdentity(ifAdminStatus.oid + (if_index,)), Integer32(cell_state.admin_status.value)) for if_index, cell_state in desired_state), 24):
        cmd = setCmd(engine, auth_data, transport, ContextData(), *chunk)
        errorIndication, errorStatus, errorIndex, varBinds = next(cmd)
        if errorIndication is not None:
            raise Exception("SNMP error returned")


class ProbeLoop(threading.Thread):
    def __init__(self, app: Flask) -> None:
        super().__init__(group=None, name="Probe Loop", daemon=True)
        self.app = app
        self.stop = threading.Event()

    def run(self) -> None:
        with self.app.app_context():
            switches = current_app.config['SWITCHES']
            while not self.stop.wait(1):
                for player, switch in enumerate(switches):
                    try:
                        over = probe_oper_status(player)
                    except (KeyboardInterrupt, SystemExit):
                        raise
                    except:
                        logger.exception("An error occurred")
                    if over:
                        self.stop.set()


def run_probe_loop(app: Flask):
    thread = ProbeLoop(app)
    thread.start()
    return thread
