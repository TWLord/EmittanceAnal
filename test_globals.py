import glob
import os
import sys
import json
import shutil
import importlib
import time

import math
import itertools
import bisect

import numpy
import ROOT
import math

import xboa.common
import Configuration
import maus_cpp.globals
import maus_cpp.field
import maus_cpp.polynomial_map
import libxml2

import xboa
from array import array

import utilities.utilities
import utilities.root_style
#from matplotlib import pyplot as plt

root_objects = []

class FileLoader(object):

    def __init__(self, config, config_anal):
        """
        Initialise empty data
        """
        self.config = config
        self.config_anal = config_anal
        self.maus_version = ""
        self.run_numbers = set([])
        self.file_name_list = []

        self.spill_count = 0
        self.suspect_spill_count = 0
        self.event_count = 0
        self.accepted_count = 0
        self.start_time = time.time()

        self.this_file_name = "a"
        self.this_file_number = -1
        self.this_root_file = None
        self.this_run = 0
        self.this_spill = 0
        self.this_event = 0
        self.this_daq_event = 0
        self.this_tree = None
        self.all_root_files = [None] # f@@@ing root deletes histograms randomly if I let files go out of scope

        #self.mc_loader = LoadMC(config, config_anal)
        #self.reco_loader = LoadReco(config, config_anal)

        self.events = []


    def get_file_list(self):
        """
        Store the list of files, based on glob of config_anal["reco_files"] and 
        do some pre-loading setup.
        """
        self.file_name_list = []
        for fname in self.config_anal["reco_files"]:
            self.file_name_list += glob.glob(fname)
        self.file_name_list = sorted(self.file_name_list)
        if len(self.file_name_list) == 0:
            raise RuntimeError("No files from "+str(self.config_anal["reco_files"]))
        print "Found", len(self.file_name_list), "files"
        print "    ", self.file_name_list[0:3], "...", self.file_name_list[-3:]
        self.next_file()
        self.this_daq_event = 0
        self.spill_count = 0


    def next_file(self):
        """
        Move on to the next file
        """
        try:
            self.this_file_name = self.file_name_list.pop(0)
            self.this_file_number += 1
            print "Loading ROOT file", self.this_file_name, self.this_file_number
        except IndexError:
            self.this_file_name = ""
            print "No more files to load"
        self.this_tree = None
        self.this_daq_event = 0


    def check_spill_count(self):
        """
        Helper function; check whether we have loaded the number of files 
        specified in config
        """
        return self.spill_count < self.config.number_of_spills or \
               self.config.number_of_spills == None


    def load_new_file(self):
        """
        Open a new file for reading
        """
        while self.this_tree == None and self.this_file_name != "":
            self.all_root_files[0] = self.this_root_file
            self.this_root_file = ROOT.TFile(self.this_file_name, "READ") # pylint: disable = E1101
            self.this_data = ROOT.MAUS.Data() # pylint: disable = E1101
            self.this_tree = self.this_root_file.Get("Spill")
            self.this_run = None
            try:
                self.this_tree.SetBranchAddress("data", self.this_data)
            except AttributeError:
                print "Failed to load 'Spill' tree for file", self.this_file_name, "maybe it isnt a MAUS output file?"
                self.this_tree = None
                self.next_file()
                continue


    def load_spills(self, number_of_daq_events):
        """
        Load a number of spills from the files
        - number_of_daq_events: number of daq events to load (daq events, not
                                physics_events)
        If we run out of spills from this file, try the next file. If the file
        won't load, keep on with the next one. Print status every 60 seconds or
        every file, whichever is shorter.

        Call "load_one_spill" subfunction to do the spill parsing.
        """
        load_spills_daq_event = 0 # number of daq events loaded during this call
                                  # to load_spills
        self.load_new_file()
        while load_spills_daq_event < number_of_daq_events and \
              self.this_file_name != "" and \
              self.this_tree != None and \
              self.check_spill_count():
            sys.stdout.flush()
            if self.this_file_name == "" or self.this_tree == None:
                break # ran out of files
            old_t = time.time()
            while self.this_daq_event < self.this_tree.GetEntries() and \
                  load_spills_daq_event < number_of_daq_events:
                new_t = time.time()
                if new_t - old_t > 60.:
                    print "Spill", self.this_daq_event, "Time", round(new_t - self.start_time, 2)
                    old_t = new_t
                    sys.stdout.flush()
                try:
                    self.this_tree.GetEntry(self.this_daq_event)
                except SystemError: # abort the file
                    sys.excepthook(*sys.exc_info())
                    print "Aborting file", self.this_file_name
                    self.this_daq_event = self.this_tree.GetEntries()
                    break
                spill = self.this_data.GetSpill()
                self.load_one_spill(spill)
                load_spills_daq_event += 1
                self.this_daq_event += 1
            if self.this_daq_event >= self.this_tree.GetEntries():
                self.next_file()
                self.load_new_file()
            print "  ...loaded", load_spills_daq_event, "'daq events'", \
                  self.spill_count, "'physics_event' spills, ", \
                  self.event_count,"events and", \
                  self.reco_loader.nan_count, "tracker nans"
            #self.mc_loader.print_virtual_detectors()
            if self.this_tree != None:
                print " at", self.this_daq_event, "/", self.this_tree.GetEntries(), "spills from file", self.this_file_name, self.this_run
            else:
                print
            sys.stdout.flush()
        self.this_root_file.Close()
        self.this_tree = None
        self.update_cuts()
        # return True if there are more events
        if True:
            #print "Doing weird load_mc virt_data if True statement"
            virt_data = [(numpy.mean(self.mc_loader.virtual_dict[key]),
                          numpy.std(self.mc_loader.virtual_dict[key]), key) 
                          for key in self.mc_loader.virtual_dict.keys()]
            for data in sorted(virt_data):
                print data[2].ljust(40), format(data[0], "10.6g"), format(data[1], "10.6g")
        return self.this_file_name != ""


    def clear_data(self):
        """Clear any ephemeral data"""
        self.events = []

    def load_one_spill(self, spill):
        """
        Load the contents of one spill. If physics_event, loop over reco_events
        and mc_events; get reco_loader mc_loader to load the respective event
        type. 
        """
        old_this_run = self.this_run
        try:
            self.this_run = max(spill.GetRunNumber(), self.this_file_number) # mc runs all have run number 0
        except ReferenceError:
            print "WARNING: Spill was NULL"
            self.suspect_spill_count += 1
            return
        self.run_numbers.add(self.this_run)
        self.this_spill = spill.GetSpillNumber()
        if old_this_run != None and old_this_run != self.this_run:
            # Nb: Durga figured out this issue was related to DAQ saturating
            # and failing to fill the "run number" int for some spills
            print "WARNING: run number changed from", old_this_run, "to", self.this_run,
            print "in file", self.this_file_name, "daq event", self.this_daq_event,
            print "spill", spill.GetSpillNumber(), "n recon events", spill.GetReconEvents().size(), "<------------WARNING"
            self.suspect_spill_count += 1
        if spill.GetDaqEventType() == "physics_event":
            self.spill_count += 1
            for ev_number, reco_event in enumerate(spill.GetReconEvents()):
                self.this_event = reco_event.GetPartEventNumber()
                event = {"data":[]}
                try:
                    self.load_reco(event, spill, ev_number)
                    if len(event["data"]) == 0: # missing TOF1 - not considered further
                        continue 
                    #self.mc_loader.load(event, spill, ev_number)
                except ValueError:
                    print "spill", spill.GetSpillNumber(), "particle_number", reco_event.GetPartEventNumber()
                    sys.excepthook(*sys.exc_info())
                except ZeroDivisionError:
                    pass
                event["run"] = self.this_run
                self.event_count += 1
                event["spill"] = spill.GetSpillNumber()
                self.events.append(event)
                event["event_number"] = ev_number
                for hit in event["data"]:
                    hit["hit"]["event_number"] = ev_number
                    hit["hit"]["spill"] = spill.GetSpillNumber()
                    hit["hit"]["particle_number"] = self.this_run
                event["data"] = sorted(event["data"], key = lambda hit: hit["hit"]["z"])


    def load_reco(self, event, spill, ev_number):
        reco_event = spill.GetReconEvents()[ev_number]
        spill_number = spill.GetSpillNumber()
        global_event = reco_event.GetGlobalEvent()
        print 'spill', spill_number
        for track in global_event.get_tracks():
            for track_point in track.GetTrackPoints():
                det_num = track_point.get_detector()
                pos = track_point.get_position()
                z_pos = pos.Z()
                if det_num != 1: # 1 is virtual
                    if det_num not in self.detectors.keys():
                        #print 'no id for det', det_num
                        continue
                    #print 'detector', self.detectors[track_point.get_detector()]
                det_list = self.config.virtual_detectors
                detector = bisect.bisect_left(det_list, (z_pos, None, ""))
                if detector == 0:
                    det_pos, dummy, det_name = det_list[detector]
                elif detector == len(det_list):
                    det_pos, dummy, det_name = det_list[-1]
                elif det_list[detector][0] - z_pos < z_pos - det_list[detector-1][0]:
                    det_pos, dummy, det_name = det_list[detector]
                else:
                    det_pos, dummy, det_name = det_list[detector-1]
                if det_name in self.absent_globals_list.keys():
                    print 'det_pos', det_pos, 'det_name', det_name
                    print 'x', pos.X(), 'y', pos.Y(), 'z', pos.Z()


    absent_globals_list = {
       "virtual_us_pry_us":[], 
       "virtual_us_pry_ds":[], 
       "virtual_tku_butterfly_us":[], 
       "virtual_tku_butterfly_ds":[], 
       "virtual_diffuser_shield":[], 
       "virtual_diffuser_us":[], 
       "virtual_diffuser_ds":[], 
       "virtual_ds_pry":[], 
    }
        
    detectors = {
        32:"_tof0",
        33:"_tof0",
        34:"_tof0",
        35:"_ckov",
        36:"_ckov",
        37:"_tof1",
        38:"_tof1",
        39:"_tof1",
        40:"_tku_tp",
        41:"_tku_tp",
        42:"_tku_2",
        43:"_tku_3",
        44:"_tku_4",
        45:"_tku_5",
        46:"_tkd_tp",
        47:"_tkd_tp",
        48:"_tkd_2",
        49:"_tkd_3",
        50:"_tkd_4",
        51:"_tkd_5",
        52:"_tof2",
        53:"_tof2",
        54:"_tof2",
        55:"_kl",
        56:"_emr",
    }


if __name__ == "__main__":


    """initialise the Analyser class"""
    config_mod = sys.argv[1].replace(".py", "")
    config_mod = config_mod.replace("scripts/", "")
    config_mod = config_mod.replace("/", ".")
    print "Using configuration module", config_mod
    config_file = importlib.import_module(config_mod)
    utilities.root_style.setup_gstyle()
    utilities.root_style.set_root_verbosity()
    ROOT.gROOT.SetBatch(True)
    config = config_file.Config()
    config_anal = config.analyses[0] 
    #print config.analyses
    #sys.exit()

    #maus_globals(self.config)
    #analysis_list = []
 
    fileloader = FileLoader(config, config_anal)
    fileloader.get_file_list()
    fileloader.load_spills(50)

