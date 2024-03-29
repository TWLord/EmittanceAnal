#!/usr/bin/env python

"""
load a ROOT file, keep some events in a spill and fill a new TTree
"""

import os
import subprocess
import time
import copy
import array


from xboa.hit import Hit
import xboa.common 

# basic PyROOT definitions
import ROOT 

# definitions of MAUS data structure for PyROOT
import libMausCpp #pylint: disable = W0611


def main():
    """
    Load some data  
    """
    my_file_name = "/data/mice/phumhf/MC/Testing/MAUSv3.3.2/09909v3/00001_sim.root"
    
    # now load the ROOT file
    print "Loading ROOT file", my_file_name
    root_file = ROOT.TFile(my_file_name, "READ") # pylint: disable = E1101

    # and set up the data tree to be filled by ROOT IO
    print "Setting up data tree"
    data = ROOT.MAUS.Data() # pylint: disable = E1101
    tree = root_file.Get("Spill")
    tree.SetBranchAddress("data", data)

    # Set up new file with cloned empty ttree structure
    new_file_name = "./new.root"
    new_root_file = ROOT.TFile(new_file_name, "recreate") # pylint: disable = E1101
    new_tree = tree.CloneTree(0)
    #new_tree.SetBranchAddress("data", data)

    # Filling without editing works fine
    """for i in range(tree.GetEntries()): 
        print "Entry", i
        tree.GetEntry(i)
        print "Old tree : "
        tree.Show()
        print "New tree before fill : "
        print new_tree.GetEntries()
        new_tree.Fill()
        print "New tree after fill : "
        print new_tree.GetEntries()
        new_tree.Show()
        #time.sleep(600)
    """
    new_root_file.cd()
    new_tree.Write()
    #new_root_file.Close()
    



    # We will try to load the data now into a analysable format and use it to
    # make a profile of the beam by plotting the number of digits (PMT pulses)
    # in the TOF. Don't ask which one is horizontal and which one is vertical...
    for i in range(tree.GetEntries()):
        tree.GetEntry(i)
        spill = data.GetSpill()
        # Print some basic information about the spill
        print "Found spill number", spill.GetSpillNumber(),
        print "in run number", spill.GetRunNumber(),
        # physics_events correspond to particle data. Everything else is DAQ
        # bureaucracy
        print "DAQ event type", spill.GetDaqEventType()
        rejected_list = []
        if spill.GetDaqEventType() == "physics_event":
            # note PyROOT gives a segmentation fault if we try to call the STL
            # vector directly
            print spill.GetReconEvents().size(), "Events"
            for j in range(spill.GetReconEvents().size()):
                tof_event = spill.GetReconEvents()[j].GetTOFEvent()
                scifi_event = spill.GetReconEvents()[j].GetSciFiEvent()
                if j % 2 :
                    continue
                rejected_list.append(j)
        recon_events = spill.GetReconEvents()
        mc_events = spill.GetMCEvents()

        print "Recon Events type is", type(spill.GetReconEvents())
        print "MC Events type is", type(spill.GetMCEvents())
        print "DAQ Data type is", type(spill.GetDAQData())
        print "EMR Spill Data type is", type(spill.GetEMRSpillData())
        print spill.GetReconEvents().size(), "recon events"
        print mc_events.size(), "mc events"
        #print daq_data.size(), "daq events"
        #print emr_data.size(), "emr events"
        rejected_list.sort( reverse=True )
        #recon_events_array = 

        new_recon_events = ROOT.std.vector('MAUS::ReconEvent*')()
        new_mc_events = ROOT.std.vector('MAUS::MCEvent*')()
        #new_recon_events = ROOT.std.vector('MAUS::ReconEvent')()
        #new_mc_events = ROOT.std.vector('MAUS::MCEvent')()

        #new_daq_data = ROOT.std.vector('MAUS::DAQData*')()
        #new_emr_data = ROOT.std.vector('MAUS::EMRSpillData*')()

        print "New Recon Events type is", type(new_recon_events)
        for ev_number in rejected_list:
            #new_recon_events.std.erase(ev_number)
            #recon_events.std.erase(ev_number)
            #spill.GetReconEvents().erase(spill.GetReconEvents().begin() + ev_number, spill.GetReconEvents().begin() + ev_number)
            #spill.GetReconEvents().remove(spill.GetReconEvents().begin() + ev_number, spill.GetReconEvents().begin() + ev_number)
            #_root.std.vector.remove.recon_events[ev_number]
            #del spill.GetReconEvents()[ev_number]
            new_recon_events.push_back(recon_events[ev_number])
            new_mc_events.push_back(mc_events[ev_number])
            #new_daq_data.push_back(daq_data[ev_number])
            #new_emr_data.push_back(emr_data[ev_number])
        print spill.GetReconEvents().size(), "recon events"
        print spill.GetMCEvents().size(), "mc events"
        spill.SetReconEvents(new_recon_events)
        spill.SetMCEvents(new_mc_events)
        print spill.GetReconEvents().size(), "recon events"
        print spill.GetMCEvents().size(), "mc events"
        print "DEBUG1"
        #ROOT.gDebug = 2
        #print ROOT.gDebug   
        new_tree.Fill()
        print "DEBUG2"
        new_root_file.cd()
        print "DEBUG3"
        new_tree.Write()
        print "DEBUG4"
        spill.SetReconEvents(recon_events)
        print "DEBUG5"
        #data.Clear() # ????
        print "DEBUG6"



    print "Closing root file"

    # A feature of ROOT is that closing the root file has weird effects like
    # deleting the histograms drawn above from memory - beware. Probably also
    # silently deallocates memory assigned to data. Probably does some other
    # sinister stuff.
    root_file.Close()

if __name__ == "__main__":
    main()

