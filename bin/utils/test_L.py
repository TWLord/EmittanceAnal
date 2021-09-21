import copy
import sys
import numpy
import ROOT
#import xboa.common

from itertools import izip
import utilities.utilities

#from analysis_base import AnalysisBase

# global constants
c = 299792458.0
e = 1.60218e-19

def get_L_nat(bz, var, x, y, px, py):
    x *= 1e-3 # mm to m
    y *= 1e-3 # mm to m
    #px *= e / c  # M * eV / c  to joules
    #py *= e / c # M * eV / c to joules
    bz *= 1e3 # Field values are scaled 1e-3 in MAUS - bc mm units?

    r = (x**2 + y**2)**0.5
    #q = -1*e # J
    q = 1 # eV

    # in MeV/c
    L_kin = (x*py) - (y*px) #/ (e * 1e6 / c)
    L_field = q*(r**2)*bz/2 / (1e6 / c) # 

    L_canon = L_kin + L_field 
    if var == "L_kin":
        return L_kin
    elif var == "L_field":
        return L_field
    elif var == "L_canon":
        return L_canon
    return 0 
    #return L_canon 

def get_L_SI(bz, var, x, y, px, py):
    x *= 1e-3 # mm to m
    y *= 1e-3 # mm to m
    px *= e * 1e6 / c  # M * eV / c  to joules
    py *= e * 1e6 / c # M * eV / c to joules
    bz *= 1e3 # Field values are scaled 1e-3 in MAUS - bc mm units?

    r = (x**2 + y**2)**0.5
    q = 1*e # J

    # In SI units
    L_kin = (x*py) - (y*px)
    L_field = q*(r**2)*bz/2

    L_canon = L_kin + L_field 
    if var == "L_kin":
        return L_kin
    elif var == "L_field":
        return L_field
    elif var == "L_canon":
        return L_canon
    return 0 
    #return L_canon 


def convert_to_nat(SI):
    # convert to natural units for angular mom
    nat = SI * 1e-6 / (e/c) # MeV/c momentum
    return nat


def test_L():
    x = 50.0 # mm
    y = 50.0 # mm
    px = 2.0 # MeV
    py = 4.0 # MeV

    bz = 3.2e-3

    print "x", x
    print 'y', y
    print 'px', px
    print 'py', py
    print 'bz', bz

    for var in ["L_kin", "L_field", "L_canon"]:
        print var
        test1 = get_L_SI(bz, var, x, y, px, py) 
        test1 = convert_to_nat(test1)
        test2 = get_L_nat(bz, var, x, y, px, py) 
        print "test1", test1
        print "test2", test2
        if abs(test1 - test2) > abs(1e-9*min(test1, test2)):
            print "SI val", test1, " not equal to nat val", test2
            print "difference:", str(test1-test2)

if __name__ == "__main__":    
    print "run tests"
    test_L()

