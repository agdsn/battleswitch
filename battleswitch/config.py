BOARD_WIDTH = 12

SWITCHES = [
    {
        'address': '192.168.1.1',
        'port': 161,
        'community': 'public',
        # SNMP ifIndex list
        'interfaces': (
            list(range(1, 25, 2)) + list(range(2, 25, 2))
            + list(range(65, 89, 2)) + list(range(66, 89, 2))
            + list(range(129, 153, 2)) + list(range(130, 153, 2))
        ),
    },
    {
        'address': '192.168.1.2',
        'port': 161,
        'community': 'public',
        'interfaces': (
            list(range(1, 25, 2)) + list(range(2, 25, 2))
            + list(range(65, 89, 2)) + list(range(66, 89, 2))
            + list(range(129, 153, 2)) + list(range(130, 153, 2))
        ),
    },
]

SHIPS = [5, 4, 4, 3],

SECRET_KEY = 'sty4eaT84tOll4Cb5uX6fLY8Ydwu75rAiunl'
