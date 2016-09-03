#!/usr/bin/env python

# The MIT License (MIT)
# Copyright (c) 2016 Steven "Drakia" Scott
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

#
# afkdeaf.py
# This module allows you to specify a channel that will deafen users upon entering,
# and restore their previous deaf/mute state upon leaving
#

from mumo_module import (MumoModule,
                         commaSeperatedIntegers,
                         logModFu)

class afkdeaf(MumoModule):
    default_config = {'afkdeaf': (
        ('servers', commaSeperatedIntegers, []),
        ('afkchannel', int, 0)
    )}

    def __init__(self, name, manager, configuration = None):
        MumoModule.__init__(self, name, manager, configuration)
        self.murmur = manager.getMurmurModule()
        self.afkchannel = self.cfg().afkdeaf.afkchannel
        self.data = {}

    def connected(self):
        manager = self.manager()
        log = self.log()
        log.debug("Register for server callbacks")

        servers = self.cfg().afkdeaf.servers
        if not servers:
            servers = manager.SERVERS_ALL

        manager.subscribeServerCallbacks(self, servers)

    def userStateChanged(self, server, state, context = None):
        log = self.log()
        
        # The user's channel is AFK
        if (state.channel == self.afkchannel):
            # Make sure we haven't already stored their data
            if (not state.session in self.data):
                # Store previous deaf/mute state
                self.data[state.session] = {
                    'deaf': state.deaf,
                    'mute': state.mute
                }
                # Set to deaf (Implies mute)
                state.deaf = True
                server.setState(state)
            return

        # If we aren't tracking the user already (Not in AFK) just return
        if (not state.session in self.data):
            return

        # This is a user who was in AFK, and just moved out, set their state back
        state.deaf = self.data[state.session]['deaf']
        state.mute = self.data[state.session]['mute']
        server.setState(state)

        # Remove this users entry from the data set
        del self.data[state.session]

    def disconnected(self): pass

    def userTextMessage(self, server, user, message, current = None): pass

    def userConnected(self, server, state, context = None): pass
    def userDisconnected(self, server, state, context = None): pass
    
    def channelCreated(self, server, state, context = None): pass
    def channelRemoved(self, server, state, context = None): pass
    def channelStateChanged(self, server, state, context = None): pass
