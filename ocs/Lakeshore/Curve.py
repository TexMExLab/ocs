#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 21:05:48 2018

@author: jacoblashner
"""

import numpy as np
class Curve:
    """
    Header for calibration curve
    ----------------
    :Name:      Name of curve
    :SN:        Serial Number
    :Format:    2 = V:K, 3 = Ohms:K, 4 = log(Ohms):K
    :Limit:     Temperature Limit (in K)
    :Coeff:     1 = negative, 2 = positive
    
    """
    def __init__(self, filename=None, header=None, units=None, temps=None):

        if filename is not None:
            self.load_from_file(filename)
        else:
            self.header = header
            self.units = units
            self.temps = temps

    def load_from_file(self, filename):
        with open(filename, 'r') as file:
            # Reads Header
            line_num = 0
            while True:
                line_num += 1
                line = file.readline().strip()
                if line == "[DATA]":
                    break
                
                if ':' in line:
                    key = line.split(':')[0].strip()
                    val = line.split(':')[1].strip()
                    self.header[key] = val
                
            _, self.units, self.temps = np.loadtxt(filename, skiprows=line_num, unpack=True)


    def write_to_file(self, filename):
        with open(filename, 'w') as file:
            file.write("[HEADER]\n")
            for key in ["Name", "SN", "Format", "Limit", "Coeff"]:
                file.write("{}:\t{}\n".format(key, self.header[key]))
            file.write("\n[DATA]\n")
            file.write("# No.\tUnits\tTemp(K)\n\n")

            for i in range(len(self.units)):
                file.write("{}\t{}\t{}\n".format(i+1, self.units[i], self.temps[i]))

    def __str__(self):
        string = ""
        for k in self.header.keys():
            string += "%-15s: %s\n"%(k, self.header[k])
        return string
    
    
if __name__ == "__main__":
    filename = "curves/defaults/SimSensorNTC.txt"
    curve = Curve(filename=filename)
    
    
            
            
    
    