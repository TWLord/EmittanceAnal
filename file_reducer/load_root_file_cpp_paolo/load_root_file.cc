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


int main() {
    // char* mrd = getenv("MAUS_ROOT_DIR");

    // std::string filename = std::string("/data/mice/phumhf/MC/Testing/MAUSv3.3.2/09909v3/00001_sim.root");
    // std::string filename = std::string("/data/mice/phumhf/MC/MAUSv3.3.2/09909v3/00001_sim.root");
    // std::string filename = std::string("/data/mice/phumhf/MC/MAUSv3.3.2/09909v3/00004_sim.root");
    // std::string filename = std::string("/data/mice/phumhf/MC/MAUSv3.3.2/09909v3/00500_sim.root");
    // std::string filename = std::string("/data/mice/phumhf/MC/MAUSv3.3.2/09911v3/00500_sim.root");
    // std::string filename = std::string("/data/mice/phumhf/MC/MAUSv3.3.0/09886/mausoutput/0/09886_full_100Spills_2.0NPEDcut_4.0NPEcut_200.root");
    std::string filename = std::string("/data/mice/phumhf/analMC/09909_v27/1/maus_output.root");
    
    // std::string filename = std::string("/data/mice/phumhf/MC/MAUSv3.3.2/09885v3/00500_sim.root");

    // TRYING THING
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
  
      }
    }
}
