from .voice import SIDVoice
from math import sin
from time import time

class SIDEffect(SIDVoice):
    def __init__(self, parent):
        self.__dict__['_parent'] = parent
        self.__dict__['_patch'] = {}

    def __setattr__(self, name, value):
        ''' Sets an attribute on the child instance if it exists,
        falls back to setting on the parent class instance
        '''
        if name in self.__dict__:
            self.__dict__[name] = value
        elif hasattr(self, '_parent'):
            setattr(self._parent, name, value)

    def patch(self, name, value):
        self.__dict__['_patch'][name] = value

    def __getattr__(self, name):
        ''' Tries to retrieve an attribute from the parent class instance,
        falls back to retreiving from the child class instance.
        '''
        if name in self.__dict__['_patch']:
            return self.__dict__['_patch'][name]()

        if hasattr(self,'_parent') and hasattr(self._parent, name):
            return getattr(self.__dict__['_parent'],name)

        return self.__getattribute__(name)

    def set_effect_attr(self, name, value):
        ''' Sets an attribute local to the child effect class instance, 
        rather than setting it on _parent
        '''
        self.__dict__[name] = value


class Gate(SIDEffect):
    def __init__(self, parent, frequency=100, duty_cycle=0.5, delta=None):
        SIDEffect.__init__(self, parent)

        if delta is None: delta = time
        self.set_effect_attr('_time', time)
        self.set_effect_attr('_gate_frequency', frequency)

        self.patch('gate', self._get_gate)

    def _get_gate(self):
        gate_frequency = self._gate_frequency() if callable(self._gate_frequency) else self._gate_frequency
        delta = self._time() if callable(self._time) else self._time

        return (int((delta*gate_frequency) % 2) == 1) and self._parent.gate


class Vibrato(SIDEffect):
    def __init__(self, parent, frequency=10, depth=100, delta=None):
        SIDEffect.__init__(self, parent)

        if delta is None: delta = time
        self.set_effect_attr('_time', time)
        self.set_effect_attr('_vibrato_frequency', frequency)
        self.set_effect_attr('_vibrato_depth', depth)

    def _get_frequency(self):
        vibrato_frequency = self._vibrato_frequency() if callable(self._vibrato_frequency) else self._vibrato_frequency
        vibrato_depth = self._vibrato_depth() if callable(self._vibrato_depth) else self._vibrato_depth
        delta = self._time() if callable(self._time) else self._time

        vibrato = ((sin(delta * vibrato_frequency) + 1) / 2) * vibrato_depth

        return self._parent.frequency + vibrato

    def _set_frequency(self, value):
        self._parent.frequency = value

    frequency = property(_get_frequency, _set_frequency)

