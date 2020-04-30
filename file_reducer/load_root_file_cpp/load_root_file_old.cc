/* This file is part of MAUS: http://micewww.pp.rl.ac.uk/projects/maus
 *
 * MAUS is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * MAUS is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MAUS.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

#include <stdlib.h>

#include <string>
#include <iostream>
#include <vector>

#include "TROOT.h"
#include "TCanvas.h"
#include "TH1D.h"
#include "TFile.h"
#include "TTree.h"

#include "src/common_cpp/JsonCppStreamer/IRStream.hh"
#include "src/common_cpp/DataStructure/Spill.hh"
#include "src/common_cpp/DataStructure/Data.hh"
#include "src/common_cpp/DataStructure/ReconEvent.hh"
#include "src/common_cpp/DataStructure/TOFEvent.hh"
#include "src/common_cpp/DataStructure/SciFiEvent.hh"
#include "src/common_cpp/DataStructure/SciFiSpacePoint.hh"
#include "src/common_cpp/DataStructure/ThreeVector.hh"


/** Perform a toy analysis using ROOT
 *
 *  Plot digits for TOF1 plane 0 and plane 1. See documentation in
 *  maus_user_guide "Accessing Data"
 */
int main() {
    // char* mrd = getenv("MAUS_ROOT_DIR");
    // std::string filename = mrd+std::string("/tmp/example_load_root_file.root");
    //
    // std::string filename = std::string("/data/mice/phumhf/MC/Testing/MAUSv3.3.2/09909v3/00001_sim.root");
    // std::string filename = std::string("/data/mice/phumhf/MC/MAUSv3.3.2/09909v3/00001_sim.root");
    // std::string filename = std::string("/data/mice/phumhf/MC/MAUSv3.3.2/09909v3/00004_sim.root");
    // std::string filename = std::string("/data/mice/phumhf/MC/MAUSv3.3.2/09909v3/00500_sim.root");
    // std::string filename = std::string("/data/mice/phumhf/MC/MAUSv3.3.2/09911v3/00500_sim.root");
    // std::string filename = std::string("/data/mice/phumhf/MC/MAUSv3.3.0/09886/mausoutput/0/09886_full_100Spills_2.0NPEDcut_4.0NPEcut_200.root");
    // std::string filename = std::string("/data/mice/phumhf/analMC/09909_v27/1/maus_output.root");
    std::string filename = std::string("/data/mice/phumhf/MC/MAUSv3.3.2/09885v3/00500_sim.root");


    // Seems to work ok
    // std::string filename = std::string("/data/mice/phumhf/ReconData/run_09903/09903_recon.root");

    // ROOT::TFile * old_root_file = ROOT::TFile(filename, "READ");
    //TFile * old_root_file = TFile::Open(filename.c_str(), "READ");
    TFile * old_root_file = new TFile(filename.c_str(), "READ");
    
    //ROOT::TTree * tree = old_root_file->Get("Spill");
    TTree * tree = (TTree*) old_root_file->Get("Spill");
    // MAUS::Data data;
    MAUS::Data *data_ptr = new MAUS::Data();
    std::cout << tree->GetEntries()  << " TTree->GetEntries()" << std::endl;
    /*for (size_t i = 0; i < tree->GetEntries(); i++) {
        MAUS::Spill* spill = data_ptr->GetSpill();
        std::cout << "Entry " << i << std::endl;
        std::cout << spill->GetSpillNumber() << std::endl;
        // std::cout << spill->GetDaqEventType() << std::endl;

    }*/

    // TRYING NEW THING
    MAUS::Data data;
    MAUS::Spill* spill;

    std::vector<MAUS::ReconEvent*>* revts;

    MAUS::TOFEvent* tof_events;
    MAUS::TOFEventSpacePoint tof_space_points;
    MAUS::TOFSpacePoint tof0_space_points, tof1_space_points;

    MAUS::SciFiEvent* scifi_events;
    std::vector<MAUS::SciFiTrack*> scifi_tracks;
    //  std::vector<MAUS::SciFiSpacePoint*> scifi_space_points;
    std::vector<MAUS::SciFiTrackPoint*> trackpoints;

    MAUS::CkovEvent* ckov_events;
    MAUS::CkovA ckovA;
    MAUS::CkovB ckovB;

    std::cout << std::endl << "Processing file: " << filename << std::endl;
    irstream infile(filename.c_str(), "Spill");

    Double_t dt01, m, P;
    Int_t nspill = 0;
    Int_t spills = 5000;

    // Loop over all spills 
    while ( (infile >> readEvent != NULL) ) {

      infile >> branchName("data") >> data;
      spill = data.GetSpill();

      if (spill == NULL) std::cout << " ----- SPILL NULL ----- " << std::endl;

      if (spill == NULL || !(spill->GetDaqEventType() == "physics_event")) {
	std::cout << " --- SPILL NULL --- " << std::endl;
        continue;
      }

      nspill++;
      std::cout << "Doing nspill : " << nspill << std::endl;
      if (nspill>spills) break;
      std::cout << "\b\b\b\b\b" << nspill;
      
      revts = spill->GetReconEvents();
  
      // Loop over recon events in spill  
      for ( size_t j = 0; j < revts->size(); ++j ) {
        if ( !revts->at(j) ) continue;
  
        //// TOF
        tof_events = revts->at(j)->GetTOFEvent(); // Pull out TOF event
        tof_space_points = tof_events->GetTOFEventSpacePoint();  // Pull out space points
  
        // CUT: select reco events with only one space point in TOF0 and one in TOF1
        if (tof_space_points.GetTOF0SpacePointArray().size() != 1) continue;
        if (tof_space_points.GetTOF1SpacePointArray().size() != 1) continue;
  
        tof0_space_points = tof_space_points.GetTOF0SpacePointArray()[0];
        tof1_space_points = tof_space_points.GetTOF1SpacePointArray()[0];
        
        // tof01                                                                                                                                       
        dt01 = tof1_space_points.GetTime()-tof0_space_points.GetTime();
        
        //// Tracker
        scifi_events = revts->at(j)->GetSciFiEvent(); // Pull out scifi event
        scifi_tracks = scifi_events->scifitracks(); // Pull out tracks  
  
	std::cout << scifi_tracks.size() << " scifi_tracks" << std::endl;
	/*
        //// CKov
        ckov_events = revts->at(j)->GetCkovEvent(); // Pull out ckovs event
        ckovA = ckov_events->GetCkovDigitArrayElement(0).GetCkovA();
        ckovB = ckov_events->GetCkovDigitArrayElement(0).GetCkovB();
        */
  
  
      }
    }
    
    /*std::string new_filename = std::string("./newnewcpp.root");
    TFile * new_root_file = new TFile(new_filename.c_str(), "recreate");
    TTree * new_tree = (TTree*) tree->CloneTree(0);*/
    // std::cout << new_tree->Show() << std::endl;


    // Use MAUS internal routines to generate a ROOT streamer. We are here
    // accessing the Spill tree which contains DAQ output data
    // Other trees are e.g. JobHeader (contains Job information), RunHeader, etc
    /*irstream infile(filename.c_str(), "Spill");
    // Iterate over all events
    while (infile >> readEvent != NULL) {

        infile >> branchName("data") >> data_ptr;
        MAUS::Spill* spill = data_ptr->GetSpill();
        std::vector<MAUS::ReconEvent*>* revts;

        MAUS::TOFEvent* tof_events;
        MAUS::TOFEventSpacePoint tof_space_points;
        MAUS::TOFSpacePoint tof0_space_points, tof1_space_points;

        MAUS::SciFiEvent* scifi_events;
        std::vector<MAUS::SciFiTrack*> scifi_tracks;
        //  std::vector<MAUS::SciFiSpacePoint*> scifi_space_points;
        std::vector<MAUS::SciFiTrackPoint*> trackpoints;

        Int_t nspill = 0;
	Int_t spills = 5000;
        unsigned int track;




        std::cout << "Doing spill stuff" << std::endl;
        if (spill != NULL) {
          std::cout << " Event Type : " << spill->GetDaqEventType() << std::endl;
        } else {
	  std::cout << " - - - SPILL IS NULL - - - " << std::endl;
	}
        // Iterate over all events; top level event in the "Spill" tree
        // corresponds to a daq_event; e.g. "start_of_burst" (spill start
        //  signal) or "physics_event" (spill data)
    
        // if (spill == NULL || !(spill->GetDaqEventType() == "physics_event")) continue;
        if (spill != NULL && spill->GetDaqEventType() == "physics_event") {
            // Each recon event corresponds to a particle trigger; data in the
            // recon event should all have the same trigger

            nspill++;
            if (nspill>spills) break;
            std::cout << "\b\b\b\b\b" << nspill;

	    revts = spill->GetReconEvents();
            for (size_t i = 0;  i < spill->GetReconEvents()->size(); ++i) {

                std::cout << "Getting event.. : " << i << std::endl;
                if ( i%2 != 0 ) {
                    std::cout << "Event: " << i << std::endl;
                }


            }
        }
    }

    // Now plot the histograms
    */
}
