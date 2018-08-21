#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 13:42:09 2018

@author: jacoblashner
"""


from ocs.Lakeshore.Curve import Curve


# ==============================================================================
# Lots of stuff to convert between integers that are read by the module 
# and what the integers actually stand for
# ==============================================================================

# To convert from int representation to string and back
sensors = {"Diode":1, "PlatRTC":2, "NTCRTC": 3}
# units = {"Kelvin": 1, "Celsius": 2, "Sensor": 3, "Fahrenheit": 4}
sensorStrings = ["None","Diode", "PlatRTC", "NTCRTC"]
unitStrings = ["None", "Kelvin", "Celsius", "Sensor", "Fahrenheit"]

# To convert from int representation to excitation or range
# use:   ranges[sensorType][range]
excitations = [[10e-6], [1e-3], [1e-3, 300e-6, 100e-6, 30e-6, 10e-6, 3e-6, 1e-6, 300e-9, 100e-9]]
ranges = [[7.5], [1e3], [10, 30, 100, 300, 1e3, 3e3, 10e3, 30e3, 100e3]] 

    
class Channel:
    """
        Object for each channel of the lakeshore module
        
        Properties
        --------------
        :channel_num: The number of the channel (1-8). This should not be changed once set
        :name: Specifies name of channel
        :sensor (int): 1 = Diode, 2 = PlatRTC, 3 = NTC RTD
        :auto_range: Specifies if channel should use autorange (1,0).
        :range: Specifies range if auto_range is false (0-8). Range is accoriding to Lakeshore docs.
        :current_reversal: Specifies if current reversal should be used (0, 1). Should be 0 for diode.
        :unit: 1 = K, 2 = C, 3 = Sensor, 4 = F
        :enabled: Sets whether channel is enabled. (1,0)
                
    """
    def __init__(self, ls, channel_num):
        self.ls = ls 
        self.channel_num = channel_num

        # Reads channel info from device
        response = self.ls.msg("INTYPE? {}".format(self.channel_num))
        data = response.split(',')

        self._sensor = int(data[0])
        self._auto_range = int(data[1])
        self._range = int(data[2])
        self._current_reversal = int(data[3])
        self._unit = int(data[4])
        self._enabled = int(data[5])

        response = self.ls.msg("INNAME? %d" % (self.channel_num))
        self._name = response

    def set_values(self, sensor=None, auto_range=None, range=None, current_reversal=None, unit=None, enabled=None, name=None):
        """
            A function to force set values to be valid, and to make sure class data corresponds to data that is actually sent to the module.
        """
        # Checks to see if values are valid
        if sensor is not None:
            if sensor in [1, 2]:
                self._sensor = sensor
                self._range = 0
            elif sensor == 3:
                self._sensor = sensor
            else:
                print("Sensor value must be 1,2, or 3.")

        if auto_range is not None:
            if auto_range in [0, 1]:
                self._auto_range = auto_range
            else:
                print("auto_range must be 0 or 1.")

        if range is not None:
            if self._sensor == 3 and range in [0, 1, 2, 3, 4, 5, 6, 7, 8]:
                self._range = range
            elif range == 0:
                self._range = range
            else:
                print("Range must be 0 for Diode or Plat RTD, or 0-8 for a NTC RTD")

        if current_reversal is not None:
            if current_reversal in [0, 1]:
                self._current_reversal = current_reversal
            else:
                print("current_reversal must be 0 or 1.")

        if unit is not None:
            if unit in [1, 2, 3, 4]:
                self._unit = unit
            else:
                print("unit must be 1, 2, 3, or 4")

        if enabled is not None:
            if enabled in [0, 1]:
                self._enabled = enabled
            else:
                print("enabled must be 0 or 1")

        if name is not None:
            self._name = name

        # Writes new values to module
        self.ls.msg("INNAME {!s}".format(self._name))

        input_type_message = "INTYPE "
        input_type_message += ",".join(["{}".format(c) for c in [ self.channel_num, self._sensor, self._auto_range,
                                                                    self._range, self._current_reversal, self._unit,
                                                                    int(self._enabled)]])
        self.ls.msg(input_type_message)

    def read_curve(self):
        resp = self.ls.msg("CRVHDR? {}".format(self.channel_num)).split(',')

        header = {
            "Name": resp[0],
            "SN": resp[1],
            "Format": int(resp[2]),
            "Limit": float(resp[3]),
            "Coeff": int(resp[4])
        }

        units = []
        temps = []
        for i in range(1, 201):
            resp = self.ls.msg("CRVPT? {},{}".format(self.channel_num, i)).split(',')
            units.append(float(resp[0]))
            temps.append(float(resp[1]))

        self.curve = Curve(header=header, units=units, temps=temps)




    def get_reading(self, unit = 0):
        u = self._unit if not unit else unit
        unit_char = "KCSF"[u-1]
        message = "{}RDG? {}".format(unit_char, self.channel_num)
        response = self.ls.msg(message)
        return float(response)

    def load_curve_point(self, n, x, y):
        """ Loads point n in the curve for specified channel"""
        message = "CRVPT "
        message += ",".join([str(c) for c in [self.channel_num, n, x, y]])
        self.ls.msg(message)
        
    def load_curve(self, filename):
        self.curve = Curve(filename=filename)

        units = self.curve.units
        temps = self.curve.temps

        assert len(units) == len(temps)
        assert len(units) < 200, "Curve must have less than 200 pts"

        print ("Loading Curve to {}".format(self.name))
        for i in range(200):
            if i < len(units):
                self.load_curve_point(i+1, units[i], temps[i])
            else:
                self.load_curve_point(i+1, 0, 0)
    
    def __str__(self):
        string = "-" * 40 + "\n"
        string += "Channel %d: %s\n"%(self.channel_num, self._name)
        string += "-"*40 + "\n"

        string += "{!s:<18} {!s:>13}\n".format("Enabled:", self._enabled)
        string += "{!s:<18} {!s:>13} ({})\n".format("Sensor:", self._sensor, sensorStrings[self._sensor])
        string += "{!s:<18} {!s:>13}\n".format("Auto Range:", self._auto_range)

        range_unit = "V" if self._sensor == 1 else "Ohm"
        string += "{!s:<18} {!s:>13} ({} {})\n".format("Range:", self._range, ranges[self._sensor-1][self._range], range_unit)
        string += "{!s:<18} {!s:>13}\n".format("Current Reversal:", self._current_reversal)
        string += "{!s:<18} {!s:>13} ({})\n".format("Units:", self._unit, unitStrings[self._unit])

        return string
        
    
if __name__ == "__main__":
    ch1 = Channel(None, 1)
    print(ch1)
    
