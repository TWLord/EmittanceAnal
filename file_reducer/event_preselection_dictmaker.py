import os
import sys
import glob
import time
import bisect
import copy
import pickle

import ROOT
import libMausCpp
import numpy
import xboa.common
from xboa.hit import Hit

import utilities.utilities

import data_loader
import data_loader.load_all
from data_loader.load_mc import LoadMC
from data_loader.load_reco import LoadReco
#from load_mc import LoadMC
#from load_reco import LoadReco

class EventPreSelection(object):
    """
    Uses data loader object to reduce filesizes by running a pre-analysis step.
    May have to rewrite loader code
    TTrees in .root file to hand over :
    * JobHeader
    * RunHeader
    * -------- Copy spill? Or create new spill 
    * RunFooter
    * JobFooter
    *

    Data loading in normal format occurs with (in order) :
     data_loader.load_all.LoadAll(self.config, self.config_anal)
     self.data_loader.get_file_list()
     self.data_loader.load_spills(self.config.preanalysis_number_of_spills)
     self.data_loader.clear_data()
     while self.data_loader.load_spills(self.config.analysis_number_of_spills) and \
           self.data_loader.check_spill_count():
         for analysis:
             do thing
         self.data_loader.clear_data()
         if now - time.time() > 1800: # 30 mins
             self.print_phase()
    to finalise.. :
     self.data_loader = None


    """
    def __init__(self, config, config_anal):
        """
        Initialise new .root file and empty data
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
        self.rejected_count = 0
        self.start_time = time.time()

        self.this_file_name = "a"
        self.this_file_number = -1
        self.this_root_file = None
        self.this_run = 0
        self.this_spill = 0
        self.this_daq_event = 0
        self.this_tree = None
        self.all_root_files = [None]

        #self.reduced_file_name = "x.root"
        #self.reduced_root_file = None
        #self.reduced_tree = None

        self.reduced_events_dict = {} # format is below
        #self.reduced_events_dict = {"spill":{"event":{}}}

        #self.reduced_events_dict = {
        #    "spill":{
        #        "event":{}
        #    }
        #}

        self.mc_loader = LoadMC(config, config_anal)
        self.reco_loader = LoadReco(config, config_anal)

        self.events = []

        self.time_offsets = {"tof0":self.config.tof0_offset,
                            "tof1":self.config.tof1_offset,
                            "tof2":self.config.tof2_offset}  

        self.fast_preanalysis = False
        if hasattr(self.config, "fast_preanalysis"):
            self.fast_preanalysis = self.config.fast_preanalysis

    def reduce_spills(self, number_of_daq_events):
        """
        Load a number of spills from the files
        - number_of_daq_events: number of daq events to load (daq events, not
                                physics_events)
        If we run out of spills from this file, try the next file. If the file 
        won't load, keep on with the next one. Print status every 60 seconds or
        every file, whichever is shorter.

        Call "load_one_spill" subfunction to do the spill parsing.
        """

        load_spills_daq_event = 0
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
                spill = self.this_data.GetSpill() # original format
                self.load_one_spill(spill) # original 
                load_spills_daq_event += 1
                self.this_daq_event += 1
            if self.this_daq_event >= self.this_tree.GetEntries():
                self.do_pickling()
                self.next_file()
                self.load_new_file()
            print "  ...loaded", load_spills_daq_event, "'daq events'", \
                  self.spill_count, "'physics_event' spills, ", \
                  self.event_count,"events and", \
                  self.accepted_count, "accepted event(s) with", \
                  self.rejected_count, "rejected event(s) "
                  #self.reco_loader.nan_count, "tracker nans"
            if self.this_tree != None:
                print " at", self.this_daq_event, "/", self.this_tree.GetEntries(), "spills from file", self.this_file_name, self.this_run
            else:
                print
            sys.stdout.flush()
        self.this_root_file.Close()
        self.this_tree = None
        #self.update_cuts()

        return self.this_file_name != ""

    def do_pickling(self):
        #print "this file name:", self.this_file_name
        self.reduced_file_name = self.this_file_name.split("/")[-1].split(".root")[0] + ".p"
        self.reduced_file_name = os.path.join(self.config_anal["plot_dir"], self.reduced_file_name)
        if True:
            pickle.dump( self.reduced_events_dict, open( self.reduced_file_name, "wb" ) ) 
        else:
            print "skipping dumping"
        #print "Resetting dict"
        self.reduced_events_dict = {}
        #self.reduced_events_dict = {"spill":{"event":{}}}


    def clear_data(self):
        """Clear any ephemeral data"""
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
        #print "Loading new file :", self.this_file_name
        while self.this_tree == None and self.this_file_name != "":
            self.all_root_files[0] = self.this_root_file
            self.this_root_file = ROOT.TFile(self.this_file_name, "READ") # pylint: disable = E1101
            self.this_data = ROOT.MAUS.Data() # pylint: disable = E1101
            self.this_tree = self.this_root_file.Get("Spill")
            self.this_run = None
            try:
                self.this_tree.SetBranchAddress("data", self.this_data)  
                self.this_tree.SetBranchStatus("*", 1)  
            except AttributeError:
                print "Failed to load 'Spill' tree for file", self.this_file_name, "maybe it isnt a MAUS output file?"
                self.this_tree = None
                self.next_file()
                continue

    def load_first_file(self):
        """
        Open first file and hold on to for clonetree permanence
        """
        print "Loading first file :", self.this_file_name
        self.first_root_file = ROOT.TFile(self.this_file_name, "READ") # pylint: disable = E1101.
        self.first_data = ROOT.MAUS.Data() # pylint: disable = E1101
        self.first_tree = self.first_root_file.Get("Spill")
        self.first_run = None
        try:
            self.first_tree.SetBranchAddress("data", self.first_data)  
        except AttributeError:
            print "Failed to load 'Spill' tree for file", self.this_file_name, "maybe it isnt a MAUS output file?"

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
        self.reduced_events_dict[self.this_spill] = {}
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
                #print "Event number(s) : ", ev_number, self.this_event
                try:
                    if self.fast_preanalysis:
                        self.load_internal(event, spill, ev_number)
                    else:
                        self.load_external(event, spill, ev_number)
                except ValueError:
                    print "spill", spill.GetSpillNumber(), "particle_number", reco_event.GetPartEventNumber()
                    sys.excepthook(*sys.exc_info())
                except ZeroDivisionError:
                    print "Zero Division Error???"
                    pass


    def load_internal(self, event, spill, ev_number):
                reco_event = spill.GetReconEvents()[ev_number]
                spill_number = spill.GetSpillNumber()
                tof_event = reco_event.GetTOFEvent()
                scifi_event = reco_event.GetSciFiEvent()
                tof_loaded = self.load_tof_event(tof_event) 
                scifi_loaded = self.load_scifi_event(scifi_event)
                #tof_spacepoints = tof_event.GetTOFEventSpacePoint()

                event["run"] = self.this_run
                self.event_count += 1
                event["spill"] = spill.GetSpillNumber()
                #self.events.append(event) # We don't need the data 
                event["event_number"] = ev_number
                tofs = [ev["detector"] for ev in tof_loaded[0]]

                if self.this_event != ev_number:
                    print "PartEventNumber:", self.this_event
                    print "ev_number:", ev_number
                    print "PartEventNumber not equal to ev_number! Go fix your code"
                    sys.exit()

                if tof_loaded[1]["tof_1_sp"] or tof_loaded[1]["tof01"] or scifi_loaded[1]["scifi_tracks_us"]:
                    #self.reduced_events_dict["spill"]["event"][self.this_event] = False
                    self.reduced_events_dict[self.this_spill][self.this_event] = False
                    self.rejected_count += 1
                    return
                    #continue

                self.accepted_count += 1
                #self.reduced_events_dict["spill"]["event"][self.this_event] = True
                self.reduced_events_dict[self.this_spill][self.this_event] = True

    def load_external(self, event, spill, ev_number):
                """try:
                    self.reco_loader.load(event, spill, ev_number)
                    if len(event["data"]) == 0: # missing TOF1 - not considered further
                        continue 
                except ValueError:
                    print "spill", spill.GetSpillNumber(), "particle_number", reco_event.GetPartEventNumber()
                    sys.excepthook(*sys.exc_info())
                except ZeroDivisionError:
                    pass"""

                self.reco_loader.load(event, spill, ev_number)
                if len(event["data"]) == 0  : # missing TOF1 - not considered further
                    self.reduced_events_dict[self.this_spill][self.this_event] = False
                    self.rejected_count += 1
                    return

                event["run"] = self.this_run
                self.event_count += 1
                event["spill"] = spill.GetSpillNumber()
                #self.events.append(event) # We don't need the data
                event["event_number"] = ev_number
                for hit in event["data"]:
                    hit["hit"]["event_number"] = ev_number
                    hit["hit"]["spill"] = spill.GetSpillNumber()
                    hit["hit"]["particle_number"] = self.this_run
                event["data"] = sorted(event["data"], key = lambda hit: hit["hit"]["z"])

                # Sorting out cut definitions
                event["upstream_cut"] = False
                #event["upstream_preanalysis_cut"] = False
                event["data_recorder_cut"] = False
                for key, value in event["will_cut"].iteritems():
                    if value and self.config.upstream_cuts[key]:
                        event["upstream_cut"] = True

                if event["upstream_cut"] :
                    self.reduced_events_dict[self.this_spill][self.this_event] = False
                    self.rejected_count += 1
                    return

                    #continue 
                #self.mc_loader.load(event, spill, ev_number)

                self.accepted_count += 1
                self.reduced_events_dict[self.this_spill][self.this_event] = True


    def load_tof_sp(self, tof_sp, station):
        xerr = tof_sp.GetGlobalPosXErr()
        yerr = tof_sp.GetGlobalPosYErr()
        cov = [
            [0.0025, 0.,     0., 0., 0., 0.],
            [0.,     xerr,   0., 0., 0., 0.],
            [0.,     0.,   yerr, 0., 0., 0.],
            [0.,     0., 0., 0., 0., 0.],
            [0.,     0., 0., 0., 0., 0.],
            [0.,     0., 0., 0., 0., 0.],
        ]
        sp_dict = {
            "x":tof_sp.GetGlobalPosX(),
            "y":tof_sp.GetGlobalPosY(),
            "z":tof_sp.GetGlobalPosZ(),
            "t":tof_sp.GetTime()+self.time_offsets[station],
        }
        loaded_sp = {
            "hit":Hit.new_from_dict(sp_dict),
            "detector":station,
            "covariance":cov,
            "dt":tof_sp.GetDt(),
            "charge_product":tof_sp.GetChargeProduct(),
            "charge":tof_sp.GetCharge(),
        }
        return loaded_sp

    def load_tof_event(self, tof_event):
         space_points = tof_event.GetTOFEventSpacePoint()
         tof_sp_list = []
         #if len(space_points.GetTOF2SpacePointArray()) > 0:
         #    print len(space_points.GetTOF0SpacePointArray()), len(space_points.GetTOF1SpacePointArray()), len(sp    ace_points.GetTOF2SpacePointArray())
         for tof_sp in space_points.GetTOF0SpacePointArray():
             tof_sp_list.append(self.load_tof_sp(tof_sp, "tof0"))
         for tof_sp in space_points.GetTOF1SpacePointArray():
             tof_sp_list.append(self.load_tof_sp(tof_sp, "tof1"))
         for tof_sp in space_points.GetTOF2SpacePointArray():
             tof_sp_list.append(self.load_tof_sp(tof_sp, "tof2"))
         detectors = [x["detector"] for x in tof_sp_list]

         tof01_cut = False
         if "tof1" in detectors and "tof0" in detectors:
             tof01 = tof_sp_list[detectors.index("tof1")]["hit"]["t"] - tof_sp_list[detectors.index("tof0")]["hit"]["t"]
             if tof01 > self.config_anal["tof01_cut_high"] or \
                tof01 < self.config_anal["tof01_cut_low"]:
                 tof01_cut = True

         tof12_cut = False
         if "tof2" in detectors and "tof1" in detectors:
             tof12 = tof_sp_list[detectors.index("tof2")]["hit"]["t"] - tof_sp_list[detectors.index("tof1")]["hit"    ]["t"]
             if tof12 > self.config_anal["tof12_cut_high"] or \
                tof12 < self.config_anal["tof12_cut_low"]:
                 tof12_cut = True

         return (tof_sp_list, {
             "tof_0_sp":space_points.GetTOF0SpacePointArray().size() != self.config_anal["tof0_n_sp"],
             "tof_1_sp":space_points.GetTOF1SpacePointArray().size() != self.config_anal["tof1_n_sp"],
             "tof_2_sp":len([det for det in detectors if det == "tof2"]) != 1,
             "tof01":tof01_cut,
             "tof12":tof12_cut,
           })

    def load_scifi_event(self, scifi_event): 
        n_tracks = self.get_n_tracks(scifi_event)
        n_tracks = [i != 1 for i in n_tracks]
        return [
            "not_loaded", {
                "scifi_tracks_us":n_tracks[0],
                "scifi_tracks_ds":n_tracks[1],
            }
        ]

    def get_n_tracks(self, scifi_event):
        n_tracks = [0, 0]
        for track in scifi_event.scifitracks():
            n_tracks[track.tracker()] += 1
        return n_tracks
