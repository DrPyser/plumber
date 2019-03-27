"""
This module implement the 'port' mechanism of plan 9 plumber.

Ports are file-like objects whereto plumb messages are copied, 
according to the plumbing rules. 
Other programs may then read from the ports they are interested in.

This implementation use unix domain sockets for ports.
"""
import trio

...
