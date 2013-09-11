# -*- coding: utf-8 -*-
# Copyright (C) 2010-2013 Tobias Weber <tobi-weber@gmx.de>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections import deque


class Signal(object):
    
    def __init__(self):
        self.receivers = deque()
        
    def connect(self, receiver, sender=None):
        lookup_key = self._lookup_key(receiver, sender)
        for r in self.receivers:
            if r.lookup_key == lookup_key:
                break
        else:
            receiver = Receiver(receiver, sender, lookup_key)
            self.receivers.append(receiver)
            
    def disconnect(self, receiver, sender=None):
        lookup_key = self._lookup_key(receiver, sender)
        for receiver in self.receivers:
            if receiver.lookup_key == lookup_key:
                self.receivers.remove(receiver)
                break

    def send(self, sender, *args, **kwargs):
        for receiver in self.receivers:
            receiver(sender, *args, **kwargs)
    
    def _lookup_key(self, receiver, sender):
        return ( id(receiver), id(sender) )
        
    
class Receiver(object):
    
    def __init__(self, receiver,
                       sender,
                       lookup_key):
        self.receiver = receiver
        self.sender = sender
        self.lookup_key = lookup_key
        
    def __call__(self, sender, *args, **kwargs):
        if (self.sender is None) or (self.sender == sender):
            self.receiver(*args, **kwargs)
        
        
def receiver(signal, **kwargs):
    """
    A decorator for connecting receivers to signals. Used by passing in the
    signal and keyword arguments to connect::

        @receiver(signal_object, sender=sender)
        def signal_receiver(sender, **kwargs):
            ...

    """
    def _decorator(func):
        signal.connect(func, **kwargs)
        return func
    return _decorator

