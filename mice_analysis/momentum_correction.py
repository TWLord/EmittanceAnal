import copy
import sys
import numpy
import math
import ROOT
import xboa.common
import os

from itertools import izip
import utilities.utilities

from analysis_base import AnalysisBase
import Configuration  # MAUS configuration (datacards) module
import maus_cpp.globals as maus_globals # MAUS C++ calls
import maus_cpp.field as field # MAUS field map calls

# global constants
c = 299792458.0
e = 1.60218e-19

class MomentumCorrection(AnalysisBase):
    def __init__(self, config, config_anal, data_loader):
        super(MomentumCorrection, self).__init__(config, config_anal, data_loader)
        self.data_loader = data_loader
        if len(self.data_loader.events) == 0:
            return
        self.reco_list = ["tku_tp","tku_2","tku_3","tku_4","tku_5","tkd_tp","tkd_2","tkd_3","tkd_4","tkd_5"]
        self.load_trackfit_fields()
        #self.correct_tracker_momentum_old()
        if "momentum_correction_recalc" in config_anal and config_anal["momentum_correction_recalc"]:
            self.correct_tracker_momentum(1)
        elif "momentum_correction_scale" in config_anal and config_anal["momentum_correction_scale"]:
            self.correct_tracker_momentum(2)
        else:
            self.correct_tracker_momentum(0)
        # Field map 
        #maus_globals.death()

    def initialise_maus(self): # Not called, instead happens in bin/run_one_analysis
        configuration = Configuration.Configuration().\
                                      getConfigJSON(command_line_args=True)
        maus_globals.birth(configuration)

    # maybe this works slower, needs to be manually set
    def correct_tracker_momentum_old(self):
        #scifi_points, tracker_fields
        events = self.data_loader.events
        for event in events: 
            #self.correct_momentum(event)
            #continue
            for detector_hit in event["data"]:
                detector = detector_hit["detector"]
                if detector not in self.reco_list:
                    #print 'skipping', detector
                    continue
                hit = detector_hit["hit"]
                #print 'doing', detector
                hit = self.correct_momentum_4(hit, detector)

    def correct_tracker_momentum(self, option):
        if option == 1:
            # recalculated correction
            self.correct_tracks_1()
        elif option == 2:
            # rescaled correction
            self.correct_tracks_2()
        elif option == 0:
            print "[ERROR]: No correction type selected. Require momentum_correction_recalc or momentum_correction_scale = True"
            print "Exiting..."
            sys.exit()
        else:
            print "[ERROR]: Momentum Correction option not recognised. Exiting..."
            sys.exit()

    def correct_tracks_1(self):
        #scifi_points, tracker_fields
        events = self.data_loader.events
        for event in events: 
            self.correct_momentum(event)
            continue

    def correct_tracks_2(self):
        #scifi_points, tracker_fields
        events = self.data_loader.events
        for event in events: 
            for detector_hit in event["data"]:
                detector = detector_hit["detector"]
                if detector not in self.reco_list:
                    #print 'skipping', detector
                    continue
                hit = detector_hit["hit"]
                #print 'doing', detector
                hit = self.correct_momentum_4(hit, detector)

    def load_trackfit_fields(self):
        self.trackfit_fields = {
            'mean_field_us':self.data_loader.events[0]["tracker_fields"]["mean_field_up"],
            'mean_field_ds':self.data_loader.events[0]["tracker_fields"]["mean_field_down"],
            'range_field_us':self.data_loader.events[0]["tracker_fields"]["range_field_up"],
            'range_field_ds':self.data_loader.events[0]["tracker_fields"]["range_field_down"],
            'var_field_us':self.data_loader.events[0]["tracker_fields"]["var_field_up"],
            'var_field_ds':self.data_loader.events[0]["tracker_fields"]["var_field_down"],
        }
        for key in self.trackfit_fields.keys():
            print key, ':', self.trackfit_fields[key]

    #def get_var_list(self):
    #    self.clear_var_out()
    #    top_detector_list = set(self.var_out.keys())
    #    for event in self.data_loader.events:
    #        detector_list = copy.deepcopy(top_detector_list)
    #        for detector_hit in event["data"]:
    #            detector = detector_hit["detector"]
    #            if detector not in detector_list:
    #                continue
    #            detector_list.remove(detector) # only add once for each detector
    #            cuts = self.var_out[detector].keys()
    #            hit = detector_hit["hit"]
    #            this_var_list = [hit[var] for var in self.ellipse_variables]
    #            #print 'var_list:', this_var_list
    #            this_var_list.append(self.get_field(hit))
    #            this_var_list.append(self.get_L_tracker(hit, 'dummy', "L_kin")*1e3) # 1e3 factor to account for units in mm vs m
    #            this_var_list.append(self.get_L_tracker(hit, 'dummy', "L_field")*1e3) # 1e3 factor to account for units in mm vs m
    #            this_var_list.append(self.get_L_tracker(hit, 'dummy', "L_canon")*1e3) # 1e3 factor to account for units in mm vs m
    #            this_var_list.append(hit["pz"])
    #            this_var_list = self.correct_momentum_4(this_var_list, detector)
    #            if "all" in cuts and not self.will_cut_us(event):
    #                self.var_out[detector]["all"].append(this_var_list)
    #            if "us" in cuts and not self.will_cut_ds(event):
    #                self.var_out[detector]["us"].append(this_var_list)
    #            if "ds" in cuts and not self.will_cut_ds(event):
    #                self.var_out[detector]["ds"].append(this_var_list)

    #    for det in "tku_tp", "tku_2", "tku_3", "tku_4", "tku_5":
    #        print det, len(self.var_out[det]["ds"]), 'events'
    #    for det in "tkd_tp", "tkd_2", "tkd_3", "tkd_4", "tkd_5":
    #        print det, len(self.var_out[det]["ds"]), 'events'
    #    #self.correct_momentum("ds")
    #    #self.correct_momentum_2("ds")
    #    #self.correct_momentum_3("ds")

    def correct_momentum(self, event):
        # Recalc px,py using new Bz with x,x',y,y' const
        for detector_pair in ("tku_tp","tku_2"), ("tku_2","tku_3"), ("tku_3","tku_4"), ("tku_4","tku_5"),\
                             ("tkd_tp","tkd_2"), ("tkd_2","tkd_3"), ("tkd_3","tkd_4"), ("tkd_4","tkd_5"):
            self.recalc_momentum(event, detector_pair, 1.0)
        for detector_pair in ("tku_5","tku_4"), ("tkd_5","tkd_4"):
            self.recalc_momentum(event, detector_pair, -1.0)

    def recalc_momentum(self, event, detector_pair, sign_modifier):
          detector   = detector_pair[0]
          detector_2 = detector_pair[1]

          hit_1, hit_2 = None, None
          for detector_hit in event["data"]:
              det = detector_hit["detector"]
              if det == detector:
                  hit_1 = detector_hit["hit"]
              elif det == detector_2:
                  hit_2 = detector_hit["hit"]
              continue

          if hit_1 == None or hit_2 == None:
              #print "[CORRECTION ERROR]: missing hit or hits:", detector, ',', detector_2
              return
              #continue

          if "tku_" in detector:
              old_bz = self.trackfit_fields["mean_field_us"]*1e3*-1.
          elif "tkd_" in detector:
              old_bz = self.trackfit_fields["mean_field_ds"]*1e3
          else:
              print "no match for detector", detector
              return
          bz_sign = 1. if "tkd_" in detector else -1.

          bz_sign *= sign_modifier

          #var_list_1 = self.var_out[detector][cut][i]
          #var_list_2 = self.var_out[detector_2][cut][i]
          #print var_list_1 
          print '\n\n ----- \n\n'
          #print var_list_2

          x  = hit_1["x"]
          px = hit_1["px"]
          y  = hit_1["y"]
          py = hit_1["py"]
          p  = hit_1["p"]
          z  = hit_1["z"]
          #bz = hit_1["bz"]*1e3
          bz = self.get_field(hit_1)*1e3 # normal
          pz = hit_1["pz"]

          x2 = hit_2["x"]
          y2 = hit_2["y"]
          z2 = hit_2["z"]
          delta_z = abs(z-z2)/1e3 # mm to m
          #delta_z = (z-z2)/1e3 # mm to m
          A = (x-x2)/1e3 # mm to m
          B = (y-y2)/1e3 # mm to m
          #A = (x2-x)/1e3 # mm to m
          #B = (y2-y)/1e3 # mm to m

          if bz == 0.0:
              return

          q = e
          # old theta
          #theta = c*old_bz*bz_sign*delta_z/(pz*1e6)*-1.
          # new theta
          theta = c*bz*bz_sign*delta_z/(pz*1e6)*-1.

          # old theta after flipping A, B
          #theta = c*old_bz*bz_sign*delta_z/(pz*1e6)
          # new theta after flipping A, B
          #theta = c*bz*bz_sign*delta_z/(pz*1e6)

          # need to clarify sign of bz vs old_bz 
          print detector_pair[0], detector_pair[1]
          print 'x', x, 'y', y, 'z', z
          print 'x2', x2, 'y2', y2, 'z2', z2
          print 'A', A, 'B', B
          print 'old_bz', old_bz, 'bz', bz
          print 'pz', pz
          print 'theta', theta
          print 'A', A, 'B', B, 'delta_z', delta_z
          print 'old: px', px, 'py', py

          new_px = (bz/2)*( (A*math.sin(theta)/(1-math.cos(theta))) + B) *c/1e6 # units to MeV/c
          new_py = (bz/2)*( (B*math.sin(theta)/(1-math.cos(theta))) - A) *c/1e6 # units to MeV/c
          new_pz = pz
          new_p = (new_px**2 + new_py**2 + new_pz**2)**0.5
    
          print 'new: px', new_px, 'py', new_py
          print 'new: pz', new_pz, 'p', new_p
          hit_1["px"] = new_px
          hit_1["py"] = new_py
          hit_1["pz"] = new_pz
          hit_1["p"] = new_p
          
    def correct_momentum_2(self, cut):
        # Scale px,py using old Bz, new Bz
        for detector_pair in ("tku_tp","tku_2"), ("tku_2","tku_3"), ("tku_3","tku_4"), ("tku_4","tku_5"),\
                             ("tkd_tp","tkd_2"), ("tkd_2","tkd_3"), ("tkd_3","tkd_4"), ("tkd_4","tkd_5"):
          detector   = detector_pair[0]
          detector_2 = detector_pair[1]
          for i in range(len(self.var_out[detector][cut])):

            if "tku_" in detector:
                old_bz = self.trackfit_fields["mean_field_us"]*1e3*-1.
            elif "tkd_" in detector:
                old_bz = self.trackfit_fields["mean_field_ds"]*1e3
            else:
                print "no match for detector", detector
                return
            bz_sign = 1. if "tkd_" in detector else -1.

            var_list_1 = self.var_out[detector][cut][i]
            var_list_2 = self.var_out[detector_2][cut][i]
    
            x  = var_list_1[0]
            px = var_list_1[1]
            y  = var_list_1[2]
            py = var_list_1[3]
            p  = var_list_1[4]
            z  = var_list_1[5]
            bz = var_list_1[6]*1e3
            pz = var_list_1[10]

            z2 = var_list_2[5]
            delta_z = abs(z-z2)/1e3

            q = e

            # need to clarify sign of bz vs old_bz 
            print detector_pair[0], detector_pair[1]
            print 'old bz', old_bz, 'bz', bz
            old_theta = c*old_bz*bz_sign*delta_z/(pz*1e6)
            new_theta = c*bz*bz_sign*delta_z/(pz*1e6)
            print 'old_theta', old_theta
            print 'new_theta', new_theta
            print 'old: px', px, 'py', py
    
            px *= (bz/old_bz) * math.sin(old_theta)/math.sin(new_theta)
            py *= (bz/old_bz) * (1-math.cos(old_theta))/(1-math.cos(new_theta))
            print 'new: px', px, 'py', py


    def correct_momentum_3(self, cut):
        self.corr_out = {}
        for detector in  "tku_tp", "tku_2", "tku_3", "tku_4", "tku_5",\
                         "tkd_tp", "tkd_2", "tkd_3", "tkd_4", "tkd_5":
            self.corr_out[detector] = {cut:[],}

            if "tku_" in detector:
                old_bz = self.trackfit_fields["mean_field_us"]*1e3*-1.
            elif "tkd_" in detector:
                old_bz = self.trackfit_fields["mean_field_ds"]*1e3
            for i in range(len(self.var_out[detector][cut])):

                bz_sign = 1. if "tkd_" in detector else -1.

                var_list_1 = self.var_out[detector][cut][i]
                this_var_list = copy.deepcopy(var_list_1)

                x  = var_list_1[0]
                px = var_list_1[1]
                y  = var_list_1[2]
                py = var_list_1[3]
                p  = var_list_1[4]
                z  = var_list_1[5]
                bz = var_list_1[6]*1e3
                pz = var_list_1[10]

                print detector
                print 'old_bz', old_bz, 'bz', bz
                print 'old: px', px, 'py', py
                print 'pz', pz
                px *= (bz/old_bz)
                py *= (bz/old_bz)
                pz *= (bz/old_bz)
                p = math.sqrt(px*px+py*py+pz*pz)
                print 'new: px', px, 'py', py
                print 'pz', pz, 'p', p
                this_var_list[1] = px
                this_var_list[3] = py
                this_var_list[4] = p
                this_var_list[10] = pz

                self.corr_out[detector][cut].append(this_var_list)


    def correct_momentum_4(self, hit, detector):
        if "mc_virtual_" in detector:
            print 'found', detector,'passed to correction'
            return hit 
        if "tku_" in detector:
            old_bz = self.trackfit_fields["mean_field_us"]*-1.
        elif "tkd_" in detector:
            old_bz = self.trackfit_fields["mean_field_ds"]
        else:
            return hit 

        bz_sign = 1. if "tkd_" in detector else -1.

        x  = hit["x"]
        px = hit["px"]
        y  = hit["y"]
        py = hit["py"]
        z  = hit["z"]
        pz = hit["pz"]
        p  = hit["p"]

        bz = self.get_field(hit)

        #print detector
        #print 'old_bz', old_bz, 'bz', bz
        #print 'old: px', px, 'py', py
        #print 'pz', pz
        px *= (bz/old_bz)
        py *= (bz/old_bz)
        #pz *= (bz/old_bz)
        p = math.sqrt(px*px+py*py+pz*pz)
        #print 'new: px', px, 'py', py
        #print 'pz', pz, 'p', p

        hit["x"] = x
        hit["y"] = y
        hit["px"] = px
        hit["py"] = py

        return hit

    def get_field(self, hit, component = None):
        (bx, by, bz, ex, ey, ez) = \
                field.get_field_value(hit['x'], hit['y'], hit['z'], 0.)
        if component != None:
            return {"Bx_map":bx, "By_map":by, "Bz_map":bz}[component]
        else:
            return bz

