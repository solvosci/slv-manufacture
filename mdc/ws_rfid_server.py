import requests
from requests.exceptions import Timeout
import sys
from websocket import create_connection


def get_session_data(env, simul=False):

    # TODO comment this for testing purposes
    if simul:
        return {
            'simul': True,
            'session_id': 'fake',
            'wsapi_url': 'fake'
        }

    IrConfigParameter = env['ir.config_parameter'].sudo()

    login_url = '%s/api/login' % IrConfigParameter.get_param('mdc.rfid_server_url')
    start_events_url = '%s/api/events/start' % IrConfigParameter.get_param('mdc.rfid_server_url')
    wsapi_url = '%s/wsapi' % IrConfigParameter.get_param('mdc.rfid_ws_server_url')
    login_data = {
        'User': {
            'login_id': IrConfigParameter.get_param('mdc.rfid_server_user'),
            'password': IrConfigParameter.get_param('mdc.rfid_server_password')
        }
    }

    try:
        r = requests.post(login_url, json=login_data, timeout=5)
    except Timeout as te:
        raise(Exception('Connection timeout with RFID server. Complete error message: %s' % te))


    print('Status: %s' % r.status_code, file=sys.stderr)
    print('Text: %s' % r.text, file=sys.stderr)

    res = r.json()

    print('Response: %s - %s' % (res['Response']['code'], res['Response']['message']), file=sys.stderr)
    if res['Response']['code'] != '0':
        raise Exception('Error authenticating on RFID server. Complete error message: %s' % res['Response']['message'])
    print('Session id.: %s  ' % r.headers['bs-session-id'], file=sys.stderr)

    ws = create_connection(wsapi_url)
    ws.send('bs-session-id=%s' % r.headers['bs-session-id'])
    result = ws.recv()
    print("Received '%s'" % result, file=sys.stderr)
    # ws.close()

    r2 = requests.post(
        start_events_url,
        json={},
        headers={'bs-session-id': r.headers['bs-session-id']})

    print('Status: %s' % r2.status_code, file=sys.stderr)
    print('Text: %s' % r2.text, file=sys.stderr)

    session_data = {
        'simul': False,
        'session_id': r.headers['bs-session-id'],
        'wsapi_url': wsapi_url
    }

    return session_data
