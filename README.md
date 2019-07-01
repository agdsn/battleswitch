# Battleswitch

Battsleswitch is the switch-based version of the Seabattle game.

## Installation
Get the code from Github and put it on a machine that has Python 3. Install the required 
Python packages using pip.
```
pip install -r requirements.txt
```

## Hardware and software configuration
Battleswitch requires Managed switches that support SNMP. By default the width of the playing filed (board) is set to 12 (see
`config.py`). The height of the board is inferred by the number of rows of ports in the switches configured in the
configuration file.

The interfaces are polled using SNMP which means that the configuration file contains the SNMP ifIndex values in the switch
configuration. It is useful to keep this persistent and thus reproducable after each power cycle. Each switch brand has their 
own polcies here, so try this before organising a Battleswitch party.

Both players require monitor and mouse each to control the software while playing. The software needs to run on at most one
computer and both players need to have a browser connect to the computer running this software. The software needs to be able
to connect (via IP) to all switches that make up both players' playing fields. Configuring (and building) this network is
left as an exercise for the reader.

In order to detect when a patch has been made that is on one of the ships of the opposition, each player also requires a
switch that generates a line signal for each patch. The minimum number of patches a player needs is equal to the total number
of positions all the ships each player has. The default (and minimum) is 16 patch cables. It is up to you to determine  
what your rules are and whether you need more.

## Starting battleswitch
```
python3 -m battleswitch
```

## Playing battleswitch

- Player 1 patches on the switches configured for player 2.
- You can play turn-by-turn, but you can also speedplay where both players patch as fast as possible until one of them has
  won.
