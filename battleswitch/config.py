BOARD_WIDTH = 12

# The interfaces list for each switch contains SNMP ifIndex values for all the ports that are used
# for playing Battleswitch

# Configuration example for 1 48 port HP switch per player
# SWITCHES = [
#     # Player 1
#     [
#         {
#             'address': '192.168.1.1',
#             'port': 161,
#             'community': 'public',
#             'interfaces': (
#                 list(range(1, 25, 2)) + list(range(2, 25, 2))
#                 + list(range(65, 89, 2)) + list(range(66, 89, 2))
#                 + list(range(129, 153, 2)) + list(range(130, 153, 2))
#             ),
#         },
#     ],
#     # Player 2
#     [
#         {
#             'address': '192.168.1.2',
#             'port': 161,
#             'community': 'public',
#             'interfaces': (
#                 list(range(1, 25, 2)) + list(range(2, 25, 2))
#                 + list(range(65, 89, 2)) + list(range(66, 89, 2))
#                 + list(range(129, 153, 2)) + list(range(130, 153, 2))
#             ),
#         },
#     ]
# ]

# Configuration example for a playing field per player consisting of three Cisco 3400 switches
# per player
SWITCHES = [
    [
        # Player 1
        {
            'address': '10.0.0.11',
            'port': 161,
            'community': 'ZEESLAG',
            # SNMP ifIndex list
            'interfaces': (
                    list(range(10001, 10025, 2)) + list(range(10002, 10025, 2))
            ),
        },
        {
            'address': '10.0.0.12',
            'port': 161,
            'community': 'ZEESLAG',
            # SNMP ifIndex list
            'interfaces': (
                    list(range(10001, 10025, 2)) + list(range(10002, 10025, 2))
            ),
        },
        {
            'address': '10.0.0.13',
            'port': 161,
            'community': 'ZEESLAG',
            # SNMP ifIndex list
            'interfaces': (
                    list(range(10001, 10025, 2)) + list(range(10002, 10025, 2))
            ),
        },
    ],
    # Player 2
    [
        {
            'address': '10.0.0.21',
            'port': 161,
            'community': 'ZEESLAG',
            # SNMP ifIndex list
            'interfaces': (
                    list(range(10001, 10025, 2)) + list(range(10002, 10025, 2))
            ),
        },
        {
            'address': '10.0.0.22',
            'port': 161,
            'community': 'ZEESLAG',
            # SNMP ifIndex list
            'interfaces': (
                    list(range(10001, 10025, 2)) + list(range(10002, 10025, 2))
            ),
        },
        {
            'address': '10.0.0.23',
            'port': 161,
            'community': 'ZEESLAG',
            # SNMP ifIndex list
            'interfaces': (
                    list(range(10001, 10025, 2)) + list(range(10002, 10025, 2))
            ),
        },
    ]
]

SHIPS = [5, 4, 4, 3],

SECRET_KEY = 'sty4eaT84tOll4Cb5uX6fLY8Ydwu75rAiunl'
