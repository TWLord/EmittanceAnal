import sys
import glob
import time
import bisect
import copy

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

class ReduceFile(object):
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
        self.start_time = time.time()

        self.this_file_name = "a"
        self.this_file_number = -1
        self.this_root_file = None
        self.this_run = 0
        self.this_spill = 0
        self.this_daq_event = 0
        self.this_tree = None
        self.all_root_files = [None]

        self.reduced_file_name = "x.root"
        self.reduced_root_file = None
        self.reduced_tree = None

        self.first_root_file = None
        self.first_root_tree = None
        #self.first_data = ROOT.MAUS.Data() # pylint: disable = E1101
        self.first_run = 0

        self.mc_loader = LoadMC(config, config_anal)
        self.reco_loader = LoadReco(config, config_anal)

        self.events = []

        self.time_offsets = {"tof0":self.config.tof0_offset,
                            "tof1":self.config.tof1_offset,
                            "tof2":self.config.tof2_offset}  

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

        self.load_first_file()
        self.create_reduced_file()
        self.load_new_file()

        # NEED TO SET UP NEW ROOT FILE AND CLONE EMPTY TREE FROM OLD ROOT FILE TO NEW. THEN CAN POPULATE WITH ENTRIES
        # want to set new tree as clone as soon as possible

        # when self.this_tree changes, change branch address?
        #oldtree->SetBranchAddress("event",&event)
        # or ??
        #self.this_tree.SetBranchAddress("data", self.this_data)  
        # then need to remove events from tree # they use :
        #oldtree.GetEntry(i)
        #newtree.Fill()
        #event.Clear()

        # to load from old branch..?? 


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
                    print "DOING THIS EVENT : ", self.this_daq_event
                    self.this_tree.GetEntry(self.this_daq_event)
                    print "DONE"
                    #self.reduced_tree.Fill()
                    #self.reduced_tree.GetEntry(self.this_daq_event)
                except SystemError: # abort the file
                    sys.excepthook(*sys.exc_info())
                    print "Aborting file", self.this_file_name
                    self.this_daq_event = self.this_tree.GetEntries()
                    break
                # Either fill to reduced_tree then load and reduce 
                # OR
                # Load from full tree and reduce then save to reduced_tree
                #spill = self.reduced_data.GetSpill()
                spill = self.this_data.GetSpill() # original format
                ##### stopped doing dumb stuff
                self.load_one_spill(spill) # original 
                print "Filling reduced tree"
                self.reduced_tree.Fill()
                print "Filled reduced tree"
                print "reduced tree entries :", self.reduced_tree.GetEntries()

                self.reduced_root_file.cd()
                self.reduced_tree.Print()
                self.reduced_tree.Write()
                print "Setting up reduced data to get entry.."
                self.reduced_data = ROOT.MAUS.Data() # pylint: disable = E1101
                self.reduced_tree.SetBranchAddress("data", self.reduced_data)  
                print "Set up"

                #self.reduced_tree.GetEntry(1)
                self.reduced_tree.GetEntry(0)
                spill = self.this_data.GetSpill()
                for reco_event in spill.GetReconEvents():
                    print "PartEventNumber:", reco_event.GetPartEventNumber()

                #reco_events = spill.GetReconEvents()[0].GetPartEventNumber()
                print "reduced spill event type :", spill.GetDaqEventType()
                ##### more dumb stuff ^
                load_spills_daq_event += 1
                self.this_daq_event += 1
            if self.this_daq_event >= self.this_tree.GetEntries():
                print "LOADING NEXT FILE"
                self.next_file()
                self.load_new_file()
                print "...LOADED NEXT FILE"
            print "  ...loaded", load_spills_daq_event, "'daq events'", \
                  self.spill_count, "'physics_event' spills, ", \
                  self.event_count,"events and", \
                  self.accepted_count, "accepted event(s) "
                  #"good times for all"
                  #self.reco_loader.nan_count, "tracker nans"
            if self.this_tree != None:
                print " at", self.this_daq_event, "/", self.this_tree.GetEntries(), "spills from file", self.this_file_name, self.this_run
            else:
                print
            sys.stdout.flush()
        self.reduced_root_file.cd()
        self.reduced_tree.Print()
        self.reduced_tree.Write()
        #self.reduced_tree.AutoSave()
        self.reduced_root_file.Close()
        self.this_root_file.Close()
        self.this_tree = None
        #self.update_cuts()

        return self.this_file_name != ""

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

    def create_reduced_file(self):
        """
        Create file we will reduce contents into
        """
        #job_header_tree = self.first_root_file.Get("JobHeader")
        #run_header_tree = self.first_root_file.Get("RunHeader")
        tree_list = []
        tree_list.append(self.first_root_file.Get("JobHeader").Clone())
        tree_list.append(self.first_root_file.Get("RunHeader").Clone())

        print "Creating", self.reduced_file_name
        self.reduced_root_file = ROOT.TFile(self.reduced_file_name, "recreate") # pylint: disable = E1101
        self.reduced_root_file.cd()
        self.reduced_tree = self.first_tree.CloneTree(0)
        tree_list.append(self.reduced_tree)

        tree_list.append(self.first_root_file.Get("RunFooter").Clone())
        tree_list.append(self.first_root_file.Get("JobFooter").Clone())
        
        self.reduced_root_file.cd()
        for tree in tree_list:
        #    tree.Print()
            tree.Write()
        #self.reduced_data = ROOT.MAUS.Data() # pylint: disable = E1101

        #try:
        #    self.reduced_tree.SetBranchAddress("data", self.first_data)  
        #    self.reduced_tree.SetBranchAddress("data", self.this_data)
        #    self.reduced_tree.SetBranchAddress("data", self.reduced_data)  
        #except AttributeError:
        #    sys.excepthook(*sys.exc_info())
        #    print "Failed to load 'Spill' tree when creating reduced file", self.reduced_file_name

        #self.reduced_tree.Print()
        #self.reduced_tree.Write()

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
        print "EVENT TYPE : ", spill.GetDaqEventType()
        if old_this_run != None and old_this_run != self.this_run:
            # Nb: Durga figured out this issue was related to DAQ saturating
            # and failing to fill the "run number" int for some spills
            print "WARNING: run number changed from", old_this_run, "to", self.this_run,
            print "in file", self.this_file_name, "daq event", self.this_daq_event,
            print "spill", spill.GetSpillNumber(), "n recon events", spill.GetReconEvents().size(), "<------------WARNING"
            self.suspect_spill_count += 1
        if spill.GetDaqEventType() == "physics_event":
            self.spill_count += 1
            #accepted_events = []
            rejected_events = []
            for ev_number, reco_event in enumerate(spill.GetReconEvents()):
                self.this_event = reco_event.GetPartEventNumber()
                event = {"data":[]}
                #print "Event number(s) : ", ev_number, self.this_event

                # Doubt sets in here ---------
                try:
                    reco_event = spill.GetReconEvents()[ev_number]
                    spill_number = spill.GetSpillNumber()
                    tof_event = reco_event.GetTOFEvent()
                    scifi_event = reco_event.GetSciFiEvent()
                    tof_loaded = self.load_tof_event(tof_event) 
                    #tof_spacepoints = tof_event.GetTOFEventSpacePoint()
                except ValueError:
                    print "spill", spill.GetSpillNumber(), "particle_number", reco_event.GetPartEventNumber()
                    sys.excepthook(*sys.exc_info())
                except ZeroDivisionError:
                    print "Zero Division Error???"
                    pass
                event["run"] = self.this_run
                self.event_count += 1
                event["spill"] = spill.GetSpillNumber()
                self.events.append(event)
                event["event_number"] = ev_number
                #tof_loaded = tof_event. 
                #print tof_loaded
                tofs = [ev["detector"] for ev in tof_loaded[0]]
                if tof_loaded[1]["tof_1_sp"]:
                    rejected_events.append(ev_number)
                    #print "spill.GetReconEvents", spill.GetReconEvents()
                    #print "has type", type(spill.GetReconEvents())
                    continue
                #print reco_event

                self.accepted_count += 1
            #print rejected_events
            recon_events = spill.GetReconEvents()
            #new_spill = copy.deepcopy(spill)
            #recon_events = new_spill.GetReconEvents()
            print recon_events
            print "recon_events type : ", type(recon_events)
            print "recon_event type : ", type(recon_events[0])
            new_recon_events = ROOT.std.vector('MAUS::ReconEvent*')()
            #new_recon_events = ROOT.vector('MAUS::ReconEventPArray')()
            #new_recon_events = ROOT.std.vector()
            print "new_recon_events type : ", type(new_recon_events)
            #rejected_events.sort(reverse = True)
            if True:
              for ev_number in rejected_events:
                  #print ev_number
                  #recon_events.erase(recon_events.begin()+ev_number)
                  #spill.GetReconEvents().erase(spill.GetReconEvents().begin() + ev_number)
                  new_recon_events.push_back(recon_events[ev_number])
                  #time.sleep(600)
              #new_spill.SetReconEvents(new_recon_events)
              spill.SetReconEvents(new_recon_events)
              print "Events Set"
              print spill
              print spill.GetReconEvents()
              print "ReconEvents :", spill.GetReconEvents().size()
              #print spill.GetReconEvents[2].GetSciFiEvent().scifitracks()
                  
  
                  #time.sleep(600)
                  #print "Spill_number", spill_number
                  #event, spill, ev_number
            """try:
                    self.reco_loader.load(event, spill, ev_number)
                    if len(event["data"]) == 0: # missing TOF1 - not considered further
                        continue 
                    self.mc_loader.load(event, spill, ev_number)
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
                event["data"] = sorted(event["data"], key = lambda hit: hit["hit"]["z"])"""


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
             tof01 = tof_sp_list[detectors.index("tof1")]["hit"]["t"] - tof_sp_list[detectors.index("tof0")]["hit"    ]["t"]
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
