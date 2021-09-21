import copy
import sys
import numpy
import math
import ROOT
import xboa.common
import os
import json

from itertools import izip
import utilities.utilities

from analysis_base import AnalysisBase
import Configuration  # MAUS configuration (datacards) module
import maus_cpp.globals as maus_globals # MAUS C++ calls
import maus_cpp.field as field # MAUS field map calls

# global constants
c = 299792458.0
e = 1.60218e-19

class AngMomFields(AnalysisBase):
    def __init__(self, config, config_anal, data_loader):
        super(AngMomFields, self).__init__(config, config_anal, data_loader)
        self.data_loader = data_loader
        self.ellipse_dict = {}
        self.reco_list = ["tku_tp","tku_2","tku_3","tku_4","tku_5","tkd_tp","tkd_2","tkd_3","tkd_4","tkd_5"]
        self.var_out = {
            "tku_tp":{"ds":[],},
            "tku_2":{"ds":[],},
            "tku_3":{"ds":[],},
            "tku_4":{"ds":[],},
            "tku_5":{"ds":[],},
            "tkd_tp":{"ds":[],},
            "tkd_2":{"ds":[],},
            "tkd_3":{"ds":[],},
            "tkd_4":{"ds":[],},
            "tkd_5":{"ds":[],},
        }
        self.min_z_us = 13800. # from tku
        self.max_z_ds = 20000. # to tkd
        #self.min_z_ds = 18800. #  
        #self.min_z_us = 12900. # from tof1 
        #self.min_z_ds = 18800. # from tkd
        self.do_ang_mc = self.config_anal["do_ang_mom_mc"]
        if self.do_ang_mc is not None:
            more_mc_planes = False
            if more_mc_planes:
                for z, dummy, station in self.config.virtual_detectors:
                    if z > self.min_z_us and z < self.max_z_ds:
                        self.var_out["mc_"+station] = {"ds":[]}
                #print self.var_out
            else:
                for station in self.var_out.keys():
                    self.var_out["mc_virtual_"+station] = {"ds":[]}
                self.var_out["mc_virtual_diffuser_us"] = {"ds":[]}
                self.var_out["mc_virtual_diffuser_ds"] = {"ds":[]}

        self.refaffed_ellipse_dict = {}
        # individual plots
        self.process_args = {}
        self.mc_stations = {}
        self.failed_pids = {}
        self.calculate_corrections = self.config_anal["ang_mom_corrections"] == None
        self.do_corrections = False # True

        self.sys_errors = {}
        if "ang_mom_systematics" in self.config_anal:
            self.save_systematic = self.config_anal["ang_mom_systematics"] == None
            self.load_systematics = self.config_anal["ang_mom_systematics"] != None
            print "Saving Ang Mom systematic" if self.save_systematic else "Loading Ang Mom systematics"
        else:
            self.save_systematic = False
            self.load_systematics = False


    def initialise_maus(self): # Not called, instead happens in bin/run_one_analysis
        configuration = Configuration.Configuration().\
                                      getConfigJSON(command_line_args=True)
        maus_globals.birth(configuration)

    def load_trackfit_fields(self):
        self.trackfit_fields = {
            'mean_field_us':self.data_loader.events[0]["tracker_fields"]["mean_field_up"],
            'mean_field_ds':self.data_loader.events[0]["tracker_fields"]["mean_field_down"],
            'range_field_us':self.data_loader.events[0]["tracker_fields"]["range_field_up"],
            'range_field_ds':self.data_loader.events[0]["tracker_fields"]["range_field_down"],
            'var_field_us':self.data_loader.events[0]["tracker_fields"]["var_field_up"],
            'var_field_ds':self.data_loader.events[0]["tracker_fields"]["var_field_down"],
        }
        #for key in self.trackfit_fields.keys():
        #    print key, ':', self.trackfit_fields[key]


    def birth(self):
        self.set_plot_dir("ang_mom")
        self.load_trackfit_fields()
        self.get_var_list()
        for detector in self.var_out:
            for cut in self.var_out[detector]:
                self.birth_ellipse(detector, cut)
                self.process_ellipse(detector, cut)
        # Individual plots
        self.mc_stations = self.config.mc_plots["mc_stations"]
        # includes other stations
        self.reco_stations = ["tku_tp", "tkd_tp"]
        for i in range(2,6):
            self.reco_stations.append("tku_"+str(i))
            self.reco_stations.append("tkd_"+str(i))
        #for i in range(2,6):
        #    self.mc_stations["tku_"+str(i)] = ["mc_virtual_tku_"+str(i)]
        #    self.mc_stations["tkd_"+str(i)] = ["mc_virtual_tkd_"+str(i)]
        #print self.mc_stations

        #self.mc_stations["global_through_virtual_diffuser_us"] = ["mc_virtual_diffuser_us"]
        #self.mc_stations["global_through_virtual_diffuser_us"] = ["mc_virtual_diffuser_ds"]

        self.birth_L_res()
        if self.do_ang_mc is not None:
            self.birth_data_detector_residuals()
            for detector, virt_station_list in self.mc_stations.iteritems(): 
                #if "tku" not in detector and "tkd" not in detector:
                if "tku" not in detector and "tkd" not in detector and "diffuser" not in detector:
                    continue
                for virt_station in virt_station_list:
                    # loop through all mc truth stations for field plots
                    self.birth_var_one_d("Bz_truth_at_"+virt_station+"_us_cut", virt_station, "pid", "bz", cuts = "us cut")
                    self.birth_var_two_d_hist("r_vs_Bz_truth_at_"+virt_station+"_us_cut", virt_station, "r", "bz", cuts = "upstream_cut", wild_x_axis=True, wild_y_axis=True)

                virt_station = virt_station_list[0]

                for L in ["L_canon", "L_kin", "L_field"]:
                    #self.birth_var_one_d(L+"_at_"+virt_station+'_all', virt_station, "pid", L)
                    #self.birth_var_one_d(L+"_at_"+virt_station+'_ds_cut', virt_station, "pid", L, cuts = "ds cut", wild_x_axis=True)
                    self.birth_var_one_d(L+"_at_"+virt_station+'_ds_cut', virt_station, "pid", L, cuts = "ds cut", xmin=-5., xmax=5.)


        for detector in self.reco_stations: 
            # loop through all reco stations
            for L in ["L_canon", "L_kin", "L_field"]:
                #self.birth_var_one_d(L+"_at_"+detector+'_all', detector, "pid", L, wild_x_axis=True)
                #self.birth_var_one_d(L+"_at_"+detector+'_ds_cut', detector, "pid", L, cuts = "ds cut", wild_x_axis=True)
                self.birth_var_one_d(L+"_at_"+detector+'_all', detector, "pid", L, xmin=-5., xmax=5.)
                self.birth_var_one_d(L+"_at_"+detector+'_ds_cut', detector, "pid", L, cuts = "ds cut", xmin=-5., xmax=5.)


                #self.birth_var_two_d_hist("r_vs_"+L+"_at_"+detector+"_us_cut", detector, "r", L, cuts = "upstream_cut")
                #self.birth_var_two_d_hist("r_vs_"+L+"_at_"+detector+"_ds_cut", detector, "r", L, cuts = "downstream_cut")
                self.birth_var_two_d_hist("r_vs_"+L+"_at_"+detector+"_us_cut", detector, "r", L, cuts = "upstream_cut", xmin=0., xmax=150., ymin=-5., ymax=5.)
                self.birth_var_two_d_hist("r_vs_"+L+"_at_"+detector+"_ds_cut", detector, "r", L, cuts = "downstream_cut", xmin=0., xmax=150., ymin=-5., ymax=5.)

                #self.birth_var_three_d_hist("px_vs_py_vs_"+L+"_at_"+detector+"_all", detector, "px", "py", L)
                #self.birth_var_three_d_hist("px_vs_py_vs_"+L+"_at_"+detector+"_us_cut", detector, "px", "py", L, cuts = "upstream_cut")
                self.birth_var_three_d_hist("px_vs_py_vs_"+L+"_at_"+detector+"_ds_cut", detector, "px", "py", L, cuts = "downstream_cut")

                self.birth_var_three_d_hist("x_vs_y_vs_"+L+"_at_"+detector+"_all", detector, "x", "y", L)
                self.birth_var_three_d_hist("x_vs_y_vs_"+L+"_at_"+detector+"_us_cut", detector, "x", "y", L, cuts = "upstream_cut")
                self.birth_var_three_d_hist("x_vs_y_vs_"+L+"_at_"+detector+"_ds_cut", detector, "x", "y", L, cuts = "downstream_cut")

            self.birth_var_two_d_hist("L_kin_vs_L_field_at_"+detector+"_us_cut", detector, "L_kin", "L_field", cuts = "upstream_cut")

            self.birth_var_two_d_hist("r_vs_Bz_map_at_"+detector+"_us_cut", detector, "r", "Bz_map", cuts = "upstream_cut", xmin=0., xmax=150., wild_y_axis=True)
            self.birth_var_two_d_hist("r_vs_Bz_map_at_"+detector+"_ds_cut", detector, "r", "Bz_map", cuts = "downstream_cut", xmin=0., xmax=150., wild_y_axis=True)
            self.birth_var_two_d_hist("x_vs_Bz_map_at_"+detector+"_ds_cut", detector, "x", "Bz_map", cuts = "downstream_cut", xmin=0., xmax=150., wild_y_axis=True)
            self.birth_var_two_d_hist("y_vs_Bz_map_at_"+detector+"_ds_cut", detector, "y", "Bz_map", cuts = "downstream_cut", xmin=0., xmax=150., wild_y_axis=True)
            self.birth_var_three_d_hist("x_vs_y_vs_Bx_map_at_"+detector+"_ds_cut", detector, "x", "y", "Bx_map", cuts = "downstream_cut", wild_z_axis=True)
            self.birth_var_three_d_hist("x_vs_y_vs_By_map_at_"+detector+"_ds_cut", detector, "x", "y", "By_map", cuts = "downstream_cut", wild_z_axis=True)
            self.birth_var_three_d_hist("x_vs_y_vs_Bz_map_at_"+detector+"_ds_cut", detector, "x", "y", "Bz_map", cuts = "downstream_cut", wild_z_axis=True)


    def process(self):
        # Individual plots
        for name in sorted(self.process_args.keys()):
            process_function = self.process_args[name][0]
            process_args = self.process_args[name][1]
            process_function(name, *process_args)
        self.process_L_res()
        if self.do_ang_mc is not None:
            self.process_data_detector_residuals()
        # Ellipse plots
        self.get_var_list()
        for detector in self.var_out:
            for cut in self.var_out[detector]:
                self.process_ellipse(detector, cut)
        print self.ellipse_dict['tkd_tp']['ds']["nevents"], 'events in ang mom ds sample'

    def death(self):
        # Field map 
        maus_globals.death()
        # Individual plots
        self.death_three_d_hist()
        ## Added early plot print & close
        self.base_death()
        self.print_plots()
        self.del_plots()
        ##

        # Ellipse plots
        self.corrections_list = [("L_kin", None), ("L_field", None), ("L_canon", None)]
        for var, sub_var in self.corrections_list:
            if self.calculate_corrections and self.do_corrections:
                self.corrections_calc(var, sub_var)
            if self.do_corrections:
                self.corrections_and_reco_errors(var, sub_var)
        if self.save_systematic:
            self.print_data()
        if self.load_systematics:
            self.load_systematic_errors()
            self.combine_sys_errors()
            self.combine_stat_sys_errors()

        ds_lambda = lambda detector_name: "mc_virtual" not in detector_name
        #virtual_lambda = lambda detector_name: "mc_virtual_tk" in detector_name
        virtual_lambda = lambda detector_name: "mc_virtual" in detector_name

        lambda_list = [("source_tkd", ds_lambda, ROOT.kRed)]
        if self.do_ang_mc is not None:
            lambda_list.append(("source_mc_tkd", virtual_lambda, ROOT.kViolet))

        for prefix, detector_lambda, color in lambda_list:
            self.refaff_ellipse_dict(detector_lambda) # rotate the data structure view
            for var, sub_var, errors in [
                            ("mean", 0, None),
                            ("mean", 1, None),
                            ("mean", 2, None),
                            ("mean", 3, None),
                            ("mean", 4, None),
                            ("mean", 5, None),
                            #("mean", 6, None),
                            ("beta_4d", None, None),
                            ("beta_x", None, None),
                            ("beta_y", None, None),
                            ("emit_4d", None, None),
                            ("l_kin", None, None),
                            ("l_centre", None, None),
                            ("l_field", None, None),
                            ("l_canon", None, None),
                            ("l_canon_plus_mean", None, None),
                            ("l_twiddle_1", None, None), # Calculated L_canon/(2.*emit*mu_mass)
                            ("l_twiddle_x", None, None), # from beta_x
                            ("l_twiddle_y", None, None), # from beta_y
                            ("l_twiddle_2", None, None), # (l_twiddle_x**2 + l_twiddle_y**2)**0.5
                            ("l_twiddle_3", None, None), # from l_kin - beta_perp*kappa
                            ("L_kin", None, "SE_L_kin"),
                            ("L_field", None, "SE_L_field"),
                            ("L_canon", None, "SE_L_canon"),
                            ("mean_r2", None, None),
                            ("mean_Bz", None, None),
                            ("nevents", None, None),
                            ("sigma", 0, None),
                            ("sigma", 2, None),
                        ]:
                try:
                    self.plot("ds", var, sub_var, color, prefix, errors) # mean z
                except Exception:
                    sys.excepthook(*sys.exc_info())
            if self.load_systematics: 
                # Plot Sys errors only plots
                for var, sub_var, errors in [
                            ("L_kin", None, "Sys_Error_L_kin"),
                            ("L_field", None, "Sys_Error_L_field"),
                            ("L_canon", None, "Sys_Error_L_canon"),
                        ]:
                    try:
                        self.plot("ds", var, sub_var, color, prefix, errors, "sys") # mean z
                    except Exception:
                        sys.excepthook(*sys.exc_info())
                # Plot combined stat+sys error plots
                for var, sub_var, errors in [
                            ("L_kin", None, "Total_Error_L_kin"),
                            ("L_field", None, "Total_Error_L_field"),
                            ("L_canon", None, "Total_Error_L_canon"),
                        ]:
                    try:
                        self.plot("ds", var, sub_var, color, prefix, errors, "stat_sys_error") # mean z
                    except Exception:
                        sys.excepthook(*sys.exc_info())
        if self.do_corrections:
            self.plot_corrections(ds_lambda)
        if self.do_ang_mc is not None:
            self.plot_residuals()
        # what it sounds like - truncate L from 1d plots 
        #self.death_truncated_L()
        self.base_death()
        self.print_plots()

    def will_cut_us(self, event):
        return event["upstream_cut"]

    def will_cut_ds(self, event):
        return event["downstream_cut"]

    def will_cut_ex(self, event):
        return event["extrapolation_cut"]

    def get_ellipse(self, detector, cut):
        return self.ellipse_dict[detector][cut]

    def clear_var_out(self):
        for det in self.var_out:
            for cut in self.var_out[det]:
                self.var_out[det][cut] = []

    def get_var_list(self):
        self.clear_var_out()
        top_detector_list = set(self.var_out.keys())
        for event in self.data_loader.events:
            detector_list = copy.deepcopy(top_detector_list)
            for detector_hit in event["data"]:
                detector = detector_hit["detector"]
                if detector not in detector_list:
                    continue
                detector_list.remove(detector) # only add once for each detector
                cuts = self.var_out[detector].keys()
                hit = detector_hit["hit"]
                this_var_list = [hit[var] for var in self.ellipse_variables]
                #print 'var_list:', this_var_list
                this_var_list.append(self.get_field(hit))
                this_var_list.append(self.get_L_tracker(hit, 'dummy', "L_kin")*1e3) # 1e3 factor to account for units in mm vs m
                this_var_list.append(self.get_L_tracker(hit, 'dummy', "L_field")*1e3) # 1e3 factor to account for units in mm vs m
                this_var_list.append(self.get_L_tracker(hit, 'dummy', "L_canon")*1e3) # 1e3 factor to account for units in mm vs m
                this_var_list.append(hit["pz"])
                #this_var_list = self.correct_momentum_4(this_var_list, detector)
                if "all" in cuts and not self.will_cut_us(event):
                    self.var_out[detector]["all"].append(this_var_list)
                if "us" in cuts and not self.will_cut_ds(event):
                    self.var_out[detector]["us"].append(this_var_list)
                if "ds" in cuts and not self.will_cut_ds(event):
                    self.var_out[detector]["ds"].append(this_var_list)

        for det in "tku_tp", "tku_2", "tku_3", "tku_4", "tku_5":
            print det, len(self.var_out[det]["ds"]), 'events'
        for det in "tkd_tp", "tkd_2", "tkd_3", "tkd_4", "tkd_5":
            print det, len(self.var_out[det]["ds"]), 'events'
        #self.correct_momentum("ds")
        #self.correct_momentum_2("ds")
        #self.correct_momentum_3("ds")


    def correct_momentum(self, cut):
        # Recalc px,py using new Bz with x,x',y,y' const
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
            print var_list_1 
            print '\n\n\n\n ----- \n\n\n\n'
            print var_list_2
    
            x  = var_list_1[0]
            px = var_list_1[1]
            y  = var_list_1[2]
            py = var_list_1[3]
            p  = var_list_1[4]
            z  = var_list_1[5]
            bz = var_list_1[6]*1e3
            pz = var_list_1[10]

            x2 = var_list_2[0]
            y2 = var_list_2[2]
            z2 = var_list_2[5]
            delta_z = abs(z-z2)/1e3 # mm to m
            A = (x-x2)/1e3 # mm to m
            B = (y-y2)/1e3 # mm to m

            q = e
            # old theta
            theta = c*old_bz*bz_sign*delta_z/(pz*1e6)
            #theta = c*bz*bz_sign*delta_z/(pz*1e6)

            # need to clarify sign of bz vs old_bz 
            print detector_pair[0], detector_pair[1]
            print 'x', x, 'y', y, 'z', z
            print 'x2', x2, 'y2', y2, 'z2', z2
            print 'old bz', old_bz, 'bz', bz
            print 'old: px', px, 'py', py
            print 'pz', pz
            print 'theta', theta
            print 'A', A, 'B', B, 'delta_z', delta_z

            new_px = (bz/2)*( (A*math.sin(theta)/(1-math.cos(theta))) + B) *c/1e6 # units to MeV/c
            new_py = (bz/2)*( (B*math.sin(theta)/(1-math.cos(theta))) - A) *c/1e6 # units to MeV/c
    
            print 'new: px', new_px, 'py', new_py

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


    def correct_momentum_4(self, this_var_list, detector):
        if "mc_virtual_" in detector:
            return this_var_list
        if "tku_" in detector:
            old_bz = self.trackfit_fields["mean_field_us"]*-1.
        elif "tkd_" in detector:
            old_bz = self.trackfit_fields["mean_field_ds"]
        else:
            return this_var_list

        bz_sign = 1. if "tkd_" in detector else -1.

        new_var_list = copy.deepcopy(this_var_list)

        x  = this_var_list[0]
        px = this_var_list[1]
        y  = this_var_list[2]
        py = this_var_list[3]
        p  = this_var_list[4]
        z  = this_var_list[5]
        bz = this_var_list[6]
        pz = this_var_list[10]

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
        new_var_list[1] = px
        new_var_list[3] = py
        new_var_list[4] = p
        new_var_list[10] = pz

        hit = {"x":x,
               "y":y,
               "px":px,
               "py":py,
              }

        #print 'old L_kin', this_var_list[7]
        #print 'old L_field', this_var_list[8]
        #print 'old L_canon', this_var_list[9]
        new_var_list[7] = self.get_L(hit, bz, 'L_kin')*1e3
        new_var_list[8] = self.get_L(hit, bz, 'L_field')*1e3
        new_var_list[9] = self.get_L(hit, bz, 'L_canon')*1e3
        #print 'L_kin', this_var_list[7]
        #print 'L_field', this_var_list[8]
        #print 'L_canon', this_var_list[9]


        return new_var_list


    def birth_ellipse(self, detector, cut):
        n_var = len(self.ellipse_variables)
        ellipse = {
        }
        ellipse["covariance"] = [[0. for j in range(n_var)] for i in range(n_var)]  
        ellipse["mean"] = [0. for i in range(n_var)]
        ellipse["sigma"] = [0. for i in range(n_var)]
        ellipse["nevents"] = 0.
        ellipse["emit_4d"] = 0.
        ellipse["beta_4d"] = 0.
        ellipse["alpha_4d"] = 0.
        ellipse["l_kin"] = 0.
        ellipse["l_centre"] = 0.
        ellipse["l_field"] = 0.
        ellipse["l_canon"] = 0.
        ellipse["l_canon_plus_mean"] = 0.
        ellipse["l_twiddle_1"] = 0.
        ellipse["l_twiddle_2"] = 0.
        ellipse["l_twiddle_3"] = 0.
        ellipse["l_twiddle_x"] = 0.
        ellipse["l_twiddle_y"] = 0.
        ellipse["mean_r2"] = 0.
        ellipse["mean_Bz"] = 0.
        ellipse["mean_xPy"] = 0.
        ellipse["mean_yPx"] = 0.
        ellipse["xPy2"] = 0. # new auto
        ellipse["yPx2"] = 0. # new auto
        ellipse["x"] = 0. # for testing
        ellipse["sigma_xPy"] = 0.
        ellipse["sigma_yPx"] = 0.
        ellipse["sigma_xPy2"] = 0. # new auto sigma
        ellipse["sigma_yPx2"] = 0. # new auto sigma
        ellipse["sigma_x"] = 0. # for testing
        ellipse["sigma_xPyminusyPx"] = 0.
        ellipse["sigma_xPy-yPx"] = 0.
        ellipse["L_kin"] = 0.
        ellipse["L_field"] = 0.
        ellipse["L_canon"] = 0.
        ellipse["sigma_L_kin"] = 0.
        ellipse["sigma_L_field"] = 0.
        ellipse["sigma_L_canon"] = 0.
        ellipse["z"] = 0.
        for axis in ["x", "y"]:
            ellipse["emit_"+axis] = 0.
            ellipse["beta_"+axis] = 0.
            ellipse["alpha_"+axis] = 0.
        if detector not in self.ellipse_dict:
            self.ellipse_dict[detector] = {}
        self.ellipse_dict[detector][cut] = ellipse

    @classmethod
    def print_ellipse(cls, ellipse):
        for row in ellipse:
          for cell in row:
            print str(round(cell)).rjust(8),
          print

    def process_ellipse(self, detector, cut):
        ellipse = self.get_ellipse(detector, cut)
        mean = ellipse["mean"]
        rms_ellipse = ellipse["covariance"]
        n_events = ellipse["nevents"]
        n_var = len(self.ellipse_variables)
        m_events = 0
        this_matrix = [[0. for j in range(n_var)] for i in range(n_var)]       
        this_mean = [0. for i in range(n_var)]
        all_data = self.var_out[detector][cut]
        #if detector in self.corr_out.keys(): 
        #    all_data = self.corr_out[detector][cut]
        #    print 'using corrected data for', detector
        #else:
        #    all_data = self.var_out[detector][cut]
        for data in all_data:
            m_events += 1
            for i in range(n_var):
                this_mean[i] += data[i]
                for j in range(i, n_var):
                    this_matrix[i][j] += data[i]*data[j]
        if m_events+n_events == 0:
            return

        if m_events == 0: # for now
            return # for now

        # sum r2 and Bz, update ellipse
        this_r2 = 0.
        this_Bz = 0.
        this_xPy = 0.
        this_yPx = 0.
        this_sigma_xPy = 0.
        this_sigma_yPx = 0.
        this_sigma_xPyminusyPx = 0.
        this_sigma_L_kin = 0.
        this_sigma_L_field = 0.
        this_sigma_L_canon = 0.
        sigma_error_keys = ['x', 'xPy2', 'yPx2', 'L_kin', 'L_field', 'L_canon']
        sigma_error_dict = {}
        for key in sigma_error_keys:
            sigma_error_dict["sigma_"+key] = ellipse["sigma_"+key]
            sigma_error_dict['mean_'+key] = ellipse[key]
        for key in sigma_error_keys:
            sigma_error_dict['this_sigma_'+key] = 0.
            sigma_error_dict['this_mean_'+key] = 0.

        for data in all_data:
            this_r2 += (data[0]**2 + data[2]**2)
            this_Bz += field.get_field_value(data[0], data[2], data[5], 0.)[2]*1e3
            this_xPy += data[0]*data[3]
            this_yPx += data[2]*data[1]
            this_sigma_xPy += (data[0]*data[3])**2
            this_sigma_yPx += (data[1]*data[2])**2
            this_sigma_xPyminusyPx += (data[0]*data[3] - data[1]*data[2])**2
            this_sigma_L_kin += data[7]**2
            this_sigma_L_field += data[8]**2
            this_sigma_L_canon += data[9]**2
            sigma_error_dict['this_mean_x'] += data[0]
            sigma_error_dict['this_sigma_x'] += data[0]**2
            sigma_error_dict['this_mean_xPy2'] += data[0]*data[3]
            sigma_error_dict['this_sigma_xPy2'] += (data[0]*data[3])**2
            sigma_error_dict['this_mean_yPx2'] += data[1]*data[2]
            sigma_error_dict['this_sigma_yPx2'] += (data[1]*data[2])**2
            #sigma_error_dict['this_xPy-yPx'] += (data[0]*data[3] - data[1]*data[2])**2
            sigma_error_dict['this_mean_L_kin'] += data[7]
            sigma_error_dict['this_sigma_L_kin'] += data[7]**2
            sigma_error_dict['this_mean_L_field'] += data[8]
            sigma_error_dict['this_sigma_L_field'] += data[8]**2
            sigma_error_dict['this_mean_L_canon'] += data[9]
            sigma_error_dict['this_sigma_L_canon'] += data[9]**2
        #print [str(x)+', '+str(sigma_error_dict[x]) for x in sigma_error_dict.keys() if "this_" in x]

        r2 = ellipse["mean_r2"]
        r2 = r2*n_events/(n_events+m_events) + \
                  this_r2/(n_events+m_events)
        Bz = ellipse["mean_Bz"]
        Bz = Bz*n_events/(n_events+m_events) + \
                  this_Bz/(n_events+m_events)
        mean_xPy = ellipse['mean_xPy']
        mean_yPx = ellipse['mean_yPx']
        #sigma_L_kin = ellipse['sigma_l_kin']
        #sigma_L_field = ellipse['sigma_l_kin']
        #sigma_L_canon = ellipse['sigma_l_kin']


        #Bz = field.get_field_value(data[0], data[2], data[5], 0.)
        #Bz = data[6] # appended to output data but not used in 
        ellipse["mean_r2"] = r2
        ellipse["mean_Bz"] = Bz

        # get sigma_xPy pt 1 - add back in old mean
        sigma_xPy = (ellipse["sigma_xPy"]**2+ellipse["mean_xPy"]**2)*n_events/(n_events+m_events) + \
                                this_sigma_xPy/(n_events+m_events)
        sigma_yPx = (ellipse["sigma_yPx"]**2+ellipse["mean_yPx"]**2)*n_events/(n_events+m_events) + \
                                this_sigma_yPx/(n_events+m_events)
        sigma_xPyminusyPx = (ellipse["sigma_xPyminusyPx"]**2+(ellipse["mean_xPy"]-ellipse["mean_yPx"])**2)*n_events/(n_events+m_events) + \
                                this_sigma_xPyminusyPx/(n_events+m_events)
        # uodate means
        mean_xPy = mean_xPy*n_events/(n_events+m_events) + \
                  this_xPy/(n_events+m_events)
        mean_yPx = mean_yPx*n_events/(n_events+m_events) + \
                  this_yPx/(n_events+m_events)
        ellipse["mean_xPy"] = mean_xPy
        ellipse["mean_yPx"] = mean_yPx


        # update the main ellipse
        for i in range(n_var):
            for j in range(i, n_var):
                rms_ellipse[i][j] += mean[i]*mean[j]
 
        for i in range(n_var):
            mean[i] = mean[i]*n_events/(n_events+m_events) + \
                      this_mean[i]/(n_events+m_events)
            for j in range(i, n_var):
                rms_ellipse[i][j] = rms_ellipse[i][j]*n_events/(n_events+m_events) + \
                                this_matrix[i][j]/(n_events+m_events)
                rms_ellipse[i][j] -= mean[i]*mean[j]
                rms_ellipse[j][i] = rms_ellipse[i][j]

        # get sigma_xPy pt 2 - subtract means & sqrt
        sigma_xPy -= ellipse["mean_xPy"]**2
        sigma_xPy = abs(sigma_xPy)**0.5
        sigma_yPx -= ellipse["mean_yPx"]**2
        sigma_yPx = abs(sigma_yPx)**0.5
        sigma_xPyminusyPx -= (ellipse["mean_xPy"]-ellipse["mean_yPx"])**2
        sigma_xPyminusyPx = abs(sigma_xPyminusyPx)**0.5
        ellipse["sigma_xPy"] = sigma_xPy
        ellipse["sigma_yPx"] = sigma_yPx
        ellipse["sigma_xPyminusyPx"] = sigma_xPyminusyPx

        ellipse["mean"] = mean
        ellipse["sigma"] = [abs(rms_ellipse[i][i])**0.5 for i in range(n_var)] # abs(sigma) as sigma_z == 0 causes nan error
        ellipse["covariance"] = rms_ellipse
        ellipse["nevents"] += m_events
        matrix = numpy.array(rms_ellipse)[0:4, 0:4]
        det = numpy.linalg.det(matrix)
        if det < 1e-9:
            # right at the back, near EMR, beam becomes very upright and det < 0
            return
        mu_mass = xboa.common.pdg_pid_to_mass[13]
        emit = det**0.25/mu_mass
        """if abs(emit) > 1e-9:
            beta = (matrix[0][0]+matrix[2][2])*mean[4]/2./mu_mass/emit
            alpha = (matrix[0][1]+matrix[2][3])/2./mu_mass/emit
            ellipse["beta_4d"] = beta
            ellipse["alpha_4d"] = alpha"""
        beta = (matrix[0][0]+matrix[2][2])*mean[4]/2./mu_mass/emit
        alpha = (matrix[0][1]+matrix[2][3])/2./mu_mass/emit
        ellipse["beta_4d"] = beta
        ellipse["alpha_4d"] = alpha

        # ang_mom in mm units 
        l_kin = (matrix[0][3]-matrix[1][2]) # MeV/c mm 
        #Bz = self.get_field(detector)*1e3 # conv to Tesla # Does not use exact field for MC virtual planes
        #ellipse["Bz"] = Bz
        beta_m = beta # beta in mm!
        kappa = (Bz/2./mean[4]) / (1e3*1e6/c) # convert Bz to MeV/c to J/m^2/A? - 1e-3 for mm
        ellipse["l_twiddle_x"] = matrix[0][3] # <xPy> for now
        ellipse["l_twiddle_y"] = matrix[1][2] # <yPx> for now

        l_field = (1*r2*Bz/2)  / (1e3*1e6/c) # q/q # conv from J mm /s (q/q) -> eV mm /s (sq) -> to MeV/c mm. r^2 -> 1/(1e3*1e3/1e3)
        ellipse["l_kin"] = l_kin # L_average - L_beamcentre
        ellipse["l_centre"] = (mean[0]*mean[3] - mean[1]*mean[2]) # conv from MeV/c mm to MeV/c m
        ellipse["l_field"] = l_field #
        ellipse["l_canon"] = l_kin + l_field # matches particle by particle plots 
        ellipse["l_canon_plus_mean"] = l_kin + l_field + ellipse["l_centre"] # add back in mean 
        ellipse["l_twiddle_1"] = ellipse["l_canon"]/2./mu_mass/(emit) 
        ellipse["l_twiddle_1_plus_mean"] = ellipse["l_canon_plus_mean"]/2./mu_mass/(emit) # no messing with mean
        ellipse["l_twiddle_3"] = (l_kin/2./mu_mass/(emit)) + beta*kappa # should maybe be without messing with means
        ellipse["emit_4d"] = emit

        # Update means for xPy2, yPx2
        #for key in ["x", "xPy2", "yPx2"]:
        for key in sigma_error_keys: 
            ellipse[key] = sigma_error_dict['mean_'+key]*n_events/(n_events+m_events) + \
                      sigma_error_dict['this_mean_'+key]/(n_events+m_events)

        # Update canonical ang mom sigma for errors
        for key in sigma_error_keys:
            # Sq std devs, add back in means and calculate new val sq'd
            sigma_error_dict["sigma_"+key] = (sigma_error_dict["sigma_"+key]**2 + sigma_error_dict['mean_'+key]**2)*n_events/(n_events+m_events) + \
                                sigma_error_dict["this_sigma_"+key]/(n_events+m_events)
            # updated means elsewhere
            # subtract means & sqrt
            sigma_error_dict["sigma_"+key] -= ellipse[key]**2
            sigma_error_dict["sigma_"+key] = abs(sigma_error_dict["sigma_"+key])**0.5
            # update stores values in ellipse{}
            ellipse['sigma_'+key] = sigma_error_dict['sigma_'+key]
            ellipse["SE_"+key] = ellipse["sigma_"+key]/(ellipse["nevents"])**0.5

        # live diagnostics
        """print '\n ---- '
        print 'n_events', n_events
        print 'm_events', m_events
        print 'Detector :', detector
        print 'Bz', Bz
        #print 'beta', beta
        #print 'kappa', kappa
        #print 'beta*kappa', beta*kappa
        print 'l_field, qr^2Bz/2', l_field
        print 'l_kin, <xPy - yPx>', l_kin
        print 'l_canon,', ellipse['l_canon']
        print '<xPy> - <yPx>', ellipse['mean_xPy'] - ellipse['mean_yPx'] 
        print '<x><Py> - <y><Px>', ellipse['mean'][0]*ellipse['mean'][3] - ellipse['mean'][2]*ellipse['mean'][1]
        print '<xPy - yPx>/2*m*c*epsilon = l_twiddle - beta_perp*kappa = ', l_kin/2./mu_mass/(emit)
        #print 'l_twiddle from <l_canon> with mean subtracted', ellipse["l_twiddle_1"]
        #print 'l_twiddle from <l_canon> with mean added back in', ellipse["l_twiddle_1_plus_mean"]
        #print 'l_twiddle from <l_kin>/2*m*c*epsilon + beta*kappa ', ellipse["l_twiddle_3"]
        print 'nevents', ellipse["nevents"]
        print 'sigma_x/sqrt(N)', ellipse["sigma"][0]/math.sqrt(ellipse["nevents"])
        print 'sigma_Py/sqrt(N)', ellipse["sigma"][3]/math.sqrt(ellipse["nevents"])
        print 'sigma_y/sqrt(N)', ellipse["sigma"][2]/math.sqrt(ellipse["nevents"])
        print 'sigma_Px/sqrt(N)', ellipse["sigma"][1]/math.sqrt(ellipse["nevents"])
        print 'sigma_xPy/sqrt(N)', ellipse["covariance"][0][3]/math.sqrt(ellipse["nevents"])
        print 'calculated sigma_xPy', ellipse["sigma_xPy"]
        print 'calculated sigma_yPx', ellipse["sigma_yPx"]
        print 'calculated sigma_xPyminusyPx', ellipse["sigma_xPyminusyPx"]
        print 'calculated sigma_xPy/nevents', ellipse["sigma_xPy"]/math.sqrt(ellipse["nevents"])
        print 'calculated sigma_yPx/nevents', ellipse["sigma_yPx"]/math.sqrt(ellipse["nevents"])
        print 'calculated sigma_xPyminusyPx/nevents', ellipse["sigma_xPyminusyPx"]/math.sqrt(ellipse["nevents"])
        print 'ellipse[sigma] x', ellipse['sigma'][0]
        print 'ellipse[mean] mean x', ellipse['mean'][0]
        print '<x>', ellipse['x']
        print '<xPy>', ellipse["mean_xPy"]
        print '<yPx>', ellipse["mean_yPx"]
        print 'cov_xPy', ellipse["covariance"][0][3]
        print 'cov_yPx', ellipse["covariance"][1][2]
        print '<xPy>*sqrt[ (s_x/x)^2+(s_py/py)^2+2(s_xpy/x*py) ]', \
                abs(ellipse["mean_xPy"])*math.sqrt( \
                (ellipse['sigma'][0]/ellipse['mean'][0])**2 +\
                (ellipse['sigma'][3]/ellipse['mean'][3])**2 +\
                2*ellipse["covariance"][0][3]/ellipse["mean_xPy"] ) 
        print "\nsigma_error_dict:"
        for key in sigma_error_keys:
            #print 'the old mean, mean_'+key, '=', sigma_error_dict['mean_'+key]
            print 'updated mean, ellipse['+key+']', '=', ellipse[key]
        for key in sigma_error_keys:
            print 'sigma_'+key, '=', sigma_error_dict['sigma_'+key]
            print 'SE_'+key, '=', ellipse["SE_"+key]
            #print 'this_mean_'+key, '=', sigma_error_dict['this_mean_'+key]
            #print 'this_sigma_'+key, '=', sigma_error_dict['this_sigma_'+key]
        """
        #print '<xPy>*sqrt[ (s_x/nevents/x)^2+(s_py/nevents/py)^2+2(s_xpy/x*py) ]', \
        #        ellipse["mean_xPy"]*math.sqrt( \
        #        (ellipse['sigma'][0]/ellipse['nevents']/ellipse['mean'][0])**2 +\
        #        (ellipse['sigma'][3]/ellipse['nevents']/ellipse['mean'][3])**2 +\
        #        2*ellipse["covariance"][0][3]/ellipse['nevents']/ellipse["mean"][0]/ellipse["mean"][3] ) 

        for axis, index in [("x", 0), ("y", 2)]:
            matrix = numpy.array(rms_ellipse)[index:index+2, index:index+2]
            det = numpy.linalg.det(matrix)
            if det < 1e-9:
                # right at the back, near EMR, beam becomes very upright and det < 0
                continue
            emit = det**0.5/mu_mass
            beta = (matrix[0][0])*mean[4]/mu_mass/emit
            alpha = (matrix[0][1])/mu_mass/emit
            ellipse["beta_"+axis] = beta
            ellipse["alpha_"+axis] = alpha
            ellipse["emit_"+axis] = emit

        # Cheeky - this might not be allowed
        ellipse["l_twiddle_x"] = (ellipse["l_twiddle_x"]/mu_mass/(ellipse["emit_x"])) + (ellipse["beta_x"]*kappa)
        ellipse["l_twiddle_y"] = (ellipse["l_twiddle_y"]/-1./mu_mass/(ellipse["emit_y"])) + (ellipse["beta_y"]*kappa)
        ellipse["l_twiddle_2"] = (ellipse["l_twiddle_x"]**2 + ellipse["l_twiddle_x"]**2)**0.5

    def death_ellipse(self, tracker, cut, print_to_screen):
        return

    def refaff_ellipse_dict(self, detector_lambda):
        """
        detector_lambda: lambda function that returns true if detector name is okay
        """
        self.refaffed_ellipse_dict = {
            "all":[],
            "ex":[],
            "us":[],
            "ds":[]
        }
        for detector in self.ellipse_dict:
            if not detector_lambda(detector):
                continue
            for cut in self.ellipse_dict[detector]:
                ellipse = self.ellipse_dict[detector][cut]
                self.refaffed_ellipse_dict[cut].append(ellipse)
        for cut in self.refaffed_ellipse_dict:
            z_var = self.ellipse_variables.index("z")
            refaff = sorted(self.refaffed_ellipse_dict[cut],
                            key = lambda ellipse: ellipse["mean"][z_var])
            self.refaffed_ellipse_dict[cut] = refaff

    #@classmethod
    #def name_lookup(cls, var, sub_var, cut):
    def name_lookup(self, var, sub_var, cut):
        if sub_var == None:
            name = var+"_"+cut
            axis = var+" ("+cut+")"
        else:
            # numeric
            #name = str(var)+"_"+str(sub_var)+"_"+cut
            #axis = str(var)+" "+str(sub_var)+" ("+cut+")"
            # name from self.ellipse_variables
            #self.ellipse_variables[sub_var]
            if type(sub_var) == str:
                name = str(var)+"_"+sub_var+"_"+cut
                axis = str(var)+" "+sub_var+" ("+cut+")"
            else:
                if sub_var < len(self.ellipse_variables):
                    name = str(var)+"_"+self.ellipse_variables[sub_var]+"_"+cut
                    axis = str(var)+" "+self.ellipse_variables[sub_var]+" ("+cut+")"
                else:
                    name = str(var)+"_"+str(sub_var)+"_"+cut
                    axis = str(var)+" "+str(sub_var)+" ("+cut+")"
        return name, axis

    def get_field(self, hit, component = None):
        (bx, by, bz, ex, ey, ez) = \
                field.get_field_value(hit['x'], hit['y'], hit['z'], 0.)
        if component != None:
            return {"Bx_map":bx, "By_map":by, "Bz_map":bz}[component]
        else:
            return bz
        #return bx, by, bz

        """for key in self.bz.keys():
            if key in detector: 
                bz = self.bz[key]
                return bz
        return 0."""

        """if "tku" in detector:
            bz = self.bz["tku"]
        elif "tkd" in detector:
            bz = self.bz["tkd"]
        else: 
            bz = 0.
        return bz"""

    def get_L_hit(self, detector_hit, var): # takes detector_hit as inp
        hit = detector_hit["hit"]
        bz = self.get_field(hit)
        if "mc_virtual_tk" in detector_hit["detector"]: # use true field - maybe remove, disentangle
            bz = detector_hit["hit"]["bz"]
        L = self.get_L(hit, bz, var)
        return L

    def get_L_tracker(self, hit, tracker, var): # takes event[tracker] as inp
        bz = self.get_field(hit)
        L = self.get_L(hit, bz, var)
        return L

    def get_L(self, hit, bz, var):
        x = hit["x"] * 1e-3 # mm to m
        y = hit["y"] * 1e-3 # mm to m
        z = hit["z"] * 1e-3 # mm to m
        px = hit["px"] # MeV
        py = hit["py"] # MeV
        bz *= 1e3 # Field values are scaled 1e-3 in MAUS - bc mm units?

        r = (x**2 + y**2)**0.5
        #q = 1.60218e-19 # J
        q = 1 # eV

        # in MeV/c
        L_kin = (x*py) - (y*px)
        L_field = q*(r**2)*bz/2 / (1e6 / c) 

        ## Higher order terms
        #L_field_higher = -q*(r**4)*self.get_bzprimeprime(hit)/16. / (1e6 / c) # units
        #L_field += L_field_higher
        #if abs(L_field_higher) > 1e1:
        #    print "Higher order L field term:\n", L_field_higher

        L_canon = L_kin + L_field 
        if var == "L_kin":
            return L_kin
        elif var == "L_field":
            return L_field
        elif var == "L_canon":
            return L_canon
        return 0 

    def get_bzprimeprime(self, hit):
        h = 0.01 # step size
        f2 = []
        for step in range(-2, 3):
            z_shift = h*step
            f = []
            for i in range(-2, 3):
                pos = {'x':hit['x'], 'y':hit['y'], 'z':hit['z']+(h*i)+z_shift}
                f.append( self.get_field( pos )*1e3 ) # units to T
            f2.append( self.deriv(f, h*1e-3) ) # units from mm to m
        return self.deriv(f2, h*1e-3) # units from mm to m

    # 5 point method for first derivative, ( -f[x+2h] +8*f[x+h] -8*f[x-h] +f[x-2h] ) /(12*h)
    def deriv(self, f, h):
        if len(f) != 5:
            return float("NaN")
        prime = ( -f[4] + 8*f[3] - 8*f[1] + f[0] )/(12*h)
        return prime

    def get_L_SI(self, bz, var, x, y, px, py):
        x = hit["x"] * 1e-3 # mm to m
        y = hit["y"] * 1e-3 # mm to m
        px = hit["px"] * e * 1e6 / c # M * eV / c to joules
        py = hit["py"] * e * 1e6 / c # M * eV / c to joules
        bz *= 1e3 # Field values are scaled 1e-3 in MAUS - bc mm Tesla units?
    
        r = (x**2 + y**2)**0.5
        q = 1*e # J
    
        # In SI units
        L_kin = (x*py) - (y*px)
        L_field = q*(r**2)*bz/2.
    
        L_canon = L_kin + L_field 
        if var == "L_kin":
            return L_kin
        elif var == "L_field":
            return L_field
        elif var == "L_canon":
            return L_canon
        return 0 


    def get_L_old(self, hit, bz, var):
        x = hit["x"] * 1e-3 # mm to m
        y = hit["y"] * 1e-3 # mm to m
        px = hit["px"] * 1.60218e-19 * 1e6 / c  # M * eV / c  to joules
        py = hit["py"] * 1.60218e-19 * 1e6 / c # M * eV / c to joules
        bz *= 1e3 # Field values are scaled 1e-3 in MAUS - bc mm units?

        r = (x**2 + y**2)**0.5
        q = 1.60218e-19 # J

        # in MeV/c
        L_kin = ((x*py) - (y*px)) / (1.60218e-19 * 1e6 / c)
        L_field = q*(r**2)*bz/2 / (1.60218e-19 * 1e6 / c)

        L_canon = L_kin + L_field 
        if var == "L_kin":
            return L_kin
        elif var == "L_field":
            return L_field
        elif var == "L_canon":
            return L_canon
        return 0 

    def has_both_trackers(self, event):
        return event["tku"] != None and event["tkd"] != None

    def plot(self, cut, var, sub_var, color, prefix, errors = None, suffix = None):
        ellipse_list = self.refaffed_ellipse_dict[cut]
        z_var = self.ellipse_variables.index("z")
        pred =  lambda ellipse: ellipse["mean"][z_var] >= self.min_z_us
        z_list = [ellipse["mean"][z_var]*1e-3 for ellipse in ellipse_list if pred(ellipse)]
        #print "Ellipse list"
        #for ellipse in ellipse_list:
        #    print ellipse
        units = 1.
        if "beta" in var:
            units = 1.e-3
        if sub_var == None:
            var_list = [ellipse[var] for ellipse in ellipse_list if pred(ellipse)]
        else:
            #var_list = [ellipse[var][sub_var]*units for ellipse in ellipse_list if pred(ellipse)]
            try:
                var_list = [ellipse[var][sub_var]*units for ellipse in ellipse_list if pred(ellipse)]
            except:
                print "ERROR", var, sub_var, ellipse
                raise
        name, axis = self.name_lookup(var, sub_var, cut)
        if suffix != None: 
            name = name+"_"+suffix
        hist, graph = self.make_root_graph(name, name+"_"+prefix,
                      z_list, "z [m]", var_list, axis, True,
                      None, None, None, None)
        if len(self.get_plot(name)["histograms"]) == 1:
            hist.Draw()
        if errors != None:
            print "plotting errors for", name
            my_plot = self.get_plot(name)
            if type(errors) != str and type(errors) != int:
                err_list = [ellipse[errors[0]][errors[1]]*units for ellipse in ellipse_list if pred(ellipse)]
            else:
                err_list = [ellipse[errors]*units for ellipse in ellipse_list if pred(ellipse)]
            """err_list = [0. for i in range(len(z_list))]
            for error in errors:
                updating_err_list = [ellipse[error]*units for ellipse in ellipse_list if pred(ellipse)]
                print error
                print updating_err_list
                err_list = [(a**2 + b**2)**0.5 for a, b in zip(err_list, updating_err_list)]
            print err_list"""
            #err_list = [ellipse[errors]*units for ellipse in ellipse_list if pred(ellipse)]

            egraph = self.get_asymm_error_graph(z_list, var_list, err_list, norm = 1., style=24, color=ROOT.kGreen, fill=color, name=name)
            egraph.Draw("same p 3")
            my_plot["graphs"][name+"_"+prefix+"_errors"] = egraph
        graph.SetMarkerStyle(20)
        graph.SetMarkerColor(color)
        graph.Draw("p l same")
        """if errors != None:
            print "plotting errors for", name
            err_list = [ellipse[errors]*units for ellipse in ellipse_list if pred(ellipse)]
            #egraph = self.get_asymm_error_graph(z_list, var_list, err_list, norm = 1., style=24, color=ROOT.kGreen, fill=ROOT.kGreen, name=name+"_errors")
            egraph = self.get_asymm_error_graph(z_list, var_list, err_list, norm = 1., style=24, color=ROOT.kGreen, fill=ROOT.kGreen, name=name)
            egraph.Draw("l a3 same")"""
        #det_list = self.config.detectors
        det_list = [det for det in self.config.detectors if det[0]>self.min_z_us and det[0]<self.max_z_ds] # only use detectors in range
        det_list += [virt for virt in self.config.virtual_detectors if virt[2] == "virtual_absorber_centre"]
        #for z_det, dummy, detector in self.config.detectors:
        for z_det, dummy, detector in det_list:
            var_min, var_max = min(var_list), max(var_list)
            #delta = var_max-var_min+1
            delta = (var_max-var_min+1)*20
            var_max += delta
            var_min -= delta
            hist, graph = self.make_root_graph(name, name+"_"+detector,
                      [z_det*1e-3, z_det*1e-3], "z [m]", [var_min, var_max], axis, True,
                      None, None, None, None)
            if "tku" in detector or "tkd" in detector:
                line_color = ROOT.kBlue
            elif "tof" in detector or "cal" in detector:
                line_color = ROOT.kRed
            else:
                line_color = ROOT.kGreen
            graph.SetLineColor(line_color)
            graph.SetLineStyle(2)
            graph.Draw("same l")

    def plot_corrections(self, detector_lambda):
        if self.do_corrections == None:
            return
        self.refaff_ellipse_dict(detector_lambda) # rotate the data structure view
        color = ROOT.kGreen
        for var, sub_var in self.corrections_list:
            for prefix, errors in [
                            ("frac", (var+"_corr", "frac_bias")),
                            ("frac", (var+"_corr", "frac+stat")),
                            ("abs", (var+"_corr", "abs_bias")),
                            ("abs", (var+"_corr", "abs+stat")),
                            ]:
                #errors = [var+"_corr", "frac_bias"]
                #corr_dict = reco_ellipse[var+"_corr"]["frac_corrected"]
                try:
                    self.plot("ds", var+"_corr", prefix+'_corrected', color, prefix, errors) # mean z
                except Exception:
                    sys.excepthook(*sys.exc_info())


    def plot_residuals(self):
        plot_list = [
                    ("L_kin", None, None),
                    ("L_field", None, None),
                    ("L_canon", None, None),
                    ("mean", 0, None),
                    ("mean", 1, None),
                    ("mean", 2, None),
                    ("mean", 3, None),
                    ("mean", 4, None),
                    ("mean", 5, None),
                    #("mean", 6, None),
                    ("mean_r2", None, None),
                    ("mean_Bz", None, None),
                    ("x", None, None),
                    ("xPy2", None, None),
                    ("yPx2", None, None),
                    ]
        for var, sub_var, errors in plot_list:
            self.calc_residual(var, sub_var)

        ds_lambda = lambda detector_name: "mc_virtual" not in detector_name
        lambda_list = [("source_tkd", ds_lambda, ROOT.kBlue)]

        for prefix, detector_lambda, color in lambda_list:
            self.refaff_ellipse_dict(detector_lambda) # rotate the data structure view
            for var, sub_var, errors in plot_list:
                if sub_var != None: 
                    if type(sub_var) == int and sub_var < len(self.ellipse_variables):
                        var = var+"_"+self.ellipse_variables[sub_var]
                    else:
                        var = var+"_"+str(sub_var)
                    #var = var+"_"+str(sub_var)
                try:
                    self.plot("ds", var+"_residual", None, color, prefix, errors) # mean z
                except Exception:
                    sys.excepthook(*sys.exc_info())

            
    def calc_residual(self, var, sub_var):
        for detector in self.reco_list: 
            for cut in self.ellipse_dict[detector].keys():
                reco_ellipse = self.get_ellipse(detector, cut)
                mc_ellipse = self.get_ellipse("mc_virtual_"+detector, cut)
                if sub_var != None:
                    reco_var = reco_ellipse[var][sub_var]
                    mc_var = mc_ellipse[var][sub_var]
                    #name = var+"_"+str(sub_var)+"_residual"
                    if type(sub_var) == int and sub_var < len(self.ellipse_variables):
                        name = var+"_"+self.ellipse_variables[sub_var]+"_residual"
                    else:
                        name = var+"_"+str(sub_var)+"_residual"
                else:
                    reco_var = reco_ellipse[var]
                    mc_var = mc_ellipse[var]
                    name = var+"_residual"
                residual_var = reco_var - mc_var
                reco_ellipse[name] = residual_var 



    def get_asymm_error_graph(self, z_list, points, errors=None, norm=1., style=None, color=None, fill=None, name="Graph", centred = True):
        graph = ROOT.TGraphAsymmErrors(len(points)-1)
        #for i, low_edge in enumerate(self.amp.bin_edge_list[:-1]):
        #    high_edge = self.amp.bin_edge_list[i+1]
        #    if centred:
        #        centre = (low_edge+high_edge)/2.
        #    else:
        #        centre = high_edge
        for i, centre in enumerate(z_list):
            graph.SetPoint(i, centre, points[i]/norm)
            if errors != None:
                #ex = centre-low_edge, high_edge-centre
                ex = 0.
                graph.SetPointError(i, 0., 0., errors[i]/norm, errors[i]/norm)
        if style != None:
            graph.SetMarkerStyle(style)
        if color != None:
            graph.SetMarkerColor(color)
        if fill != None:
            #graph.SetFillColor(fill)
            graph.SetFillColorAlpha(fill, 0.5)
            graph.SetFillStyle(3001);
        graph.SetName(name+"_errors")
        #self.root_objects.append(graph)
        return graph

    def corrections_calc(self, var, sub_var):
        print "Calculating corrections for", var
        for detector in self.reco_list: 
            for cut in self.ellipse_dict[detector].keys():
                reco_ellipse = self.get_ellipse(detector, cut)
                mc_ellipse = self.get_ellipse("mc_virtual_"+detector, cut)
                if sub_var != None:
                    reco_var = reco_ellipse[var][sub_var]
                    mc_var = mc_ellipse[var][sub_var]
                else:
                    reco_var = reco_ellipse[var]
                    mc_var = mc_ellipse[var]
                if reco_var == 0:
                    frac_weight = 1.
                else:
                    frac_weight = mc_var/reco_var
                abs_weight = mc_var - reco_var 
                #reco_frac_corr = reco_var * frac_weight
                #reco_abs_corr = reco_var + abs_weight

                if var+"_corr" not in reco_ellipse:
                    reco_ellipse[var+"_corr"] = {}
                if sub_var != None:
                    if sub_var not in reco_ellipse[var+"_corr"]:
                        reco_ellipse[var+"_corr"][sub_var] = {}
                    #reco_ellipse[var+"_corr"][sub_var]["frac_corrected"] = reco_frac_corr
                    #reco_ellipse[var+"_corr"][sub_var]["abs_corrected"] = reco_abs_corr
                    reco_ellipse[var+"_corr"][sub_var]["frac_weight"] = frac_weight
                    reco_ellipse[var+"_corr"][sub_var]["abs_weight"] = abs_weight
                else:
                    #reco_ellipse[var+"_corr"]["frac_corrected"] = reco_frac_corr
                    #reco_ellipse[var+"_corr"]["abs_corrected"] = reco_abs_corr
                    reco_ellipse[var+"_corr"]["frac_weight"] = frac_weight
                    reco_ellipse[var+"_corr"]["abs_weight"] = abs_weight
                #print 'detector', detector, ':', var, '=', reco_var, 'mc:', mc_var


    def corrections_and_reco_errors(self, var, sub_var):
        """
        Correct error in distributions based on means. 
        Not yet used, needs reworking if activated.
        Probably should also remove the corr+stat (SE) error here and do elsewhere
        """
        print "Doing corrections for", var
        for detector in self.reco_list: 
            for cut in self.ellipse_dict[detector].keys():
                reco_ellipse = self.get_ellipse(detector, cut)
                if sub_var != None:
                    corr_dict = reco_ellipse[var+"_corr"][sub_var]
                    reco_var = reco_ellipse[var][sub_var]
                else:
                    corr_dict = reco_ellipse[var+"_corr"]
                    reco_var = reco_ellipse[var]

                frac_bias = reco_var*(corr_dict["frac_weight"] - 1) #  reco_var*(corr_dict - 1)
                abs_bias = corr_dict["abs_weight"]
                corr_dict["frac_bias"] = frac_bias
                corr_dict["abs_bias"] = abs_bias

                reco_frac_corr = reco_var * corr_dict["frac_weight"]
                reco_abs_corr = reco_var + corr_dict["abs_weight"]

                corr_dict["frac_corrected"] = reco_frac_corr
                corr_dict["abs_corrected"] = reco_abs_corr

                corr_dict["frac+stat"] = (frac_bias**2 + reco_ellipse["SE_"+var]**2)**0.5
                corr_dict["abs+stat"] = (abs_bias**2 + reco_ellipse["SE_"+var]**2)**0.5

                #print 'detector', detector, 
                #print 'frac weight', corr_dict["frac_weight"], 'abs weight', corr_dict["abs_weight"]
                #print 'frac bias', corr_dict["frac_bias"], 'abs bias', corr_dict["abs_bias"]
                #print 'stat error', reco_ellipse["SE_"+var]
                #print 'frac+stat error', corr_dict["frac+stat"]
                #print 'abs+stat error', corr_dict["abs+stat"]


    ellipse_variables = ["x", "px", "y", "py", "p", "z"]

    # new bits vvvvv

    def get_wild_axis(self, a_list):
       xmi, xma = min(a_list), max(a_list)
       #xmin = xmi - (xma - xmi)/1.
       #xmax = xma + (xma - xmi)/1.
       xmin = xmi - (xma - xmi)/6.
       xmax = xma + (xma - xmi)/6.
       return xmin, xmax

    def get_data_var_one_d(self, detector, slice_variable, plot_variable, cuts, hit_predicate):
        track_final = {}
        cut_lambda = {
            "all":lambda event: False,
            "us cut":lambda event: event["upstream_cut"],
            "ds cut":lambda event: event["downstream_cut"],
        }[cuts]
        for event in self.data_loader.events:
            if cut_lambda(event):
                continue
            for detector_hit in event["data"]:
                if detector_hit["detector"] != detector:
                    continue
                if hit_predicate != None and not hit_predicate(detector_hit):
                    continue
                if plot_variable == "accumulated_e_dep":
                    if slice_variable != "pid":
                        raise RuntimeError("NO NO NO NO BADGER ATTACK")
                    self.get_accumulated_e_dep(event, detector, hit_predicate, track_final)
                    break
                else:
                    slice_var = detector_hit["hit"][slice_variable]
                    if plot_variable == "L_kin" or plot_variable == "L_canon" or plot_variable == "L_field":
                        plot_var = self.get_L_hit(detector_hit, plot_variable)
                    elif plot_variable == "Bx_map" or plot_variable == "By_map" or plot_variable == "Bz_map":
                        plot_var = self.get_field(detector_hit["hit"], plot_variable)
                    else:
                        plot_var = detector_hit["hit"][plot_variable]
                    if slice_var not in track_final:
                        track_final[slice_var] = []
                    track_final[slice_var].append(plot_var)
                    break
        all_list = []
        for value in track_final.values():
            all_list += value
        return (all_list, track_final)

    def process_var_one_d(self, name, detector, slice_variable, plot_variable, cuts, hit_predicate):
        all_list, track_final = self.get_data_var_one_d(detector, slice_variable, plot_variable, cuts, hit_predicate)
        try:
            for item in all_list:
                self.plots[name]["histograms"]["all"].Fill(item)
        except TypeError:
            print "Process var one d in mc_plotter failed to Fill with type error"
            print name, detector, slice_variable, plot_variable, cuts
            print item
            sys.excepthook(*sys.exc_info())
        for i, key in enumerate(sorted(track_final.keys())):
            hist_dict = self.plots[name]["histograms"]
            plot_name = str(slice_variable)+" = "+str(key)
            if plot_name not in hist_dict:
                if key not in self.failed_pids:
                    self.failed_pids[key] = 0
                self.failed_pids[key] += 1
                continue
            for item in track_final[key]:
                hist_dict[plot_name].Fill(item)

    def birth_var_one_d(self, canvas_name, detector, slice_variable, plot_variable, cuts = "all", xmin = None, xmax = None, wild_x_axis=False, hit_predicate = None, options = {}):
        all_list, track_final = self.get_data_var_one_d(detector, slice_variable, plot_variable, cuts, hit_predicate)
        if wild_x_axis:
            xmin, xmax = self.get_wild_axis(all_list)
        hist = self.make_root_histogram(canvas_name, "all", all_list, plot_variable+" at "+detector, 100, [], '', 0, [], xmin, xmax)
        hist.SetMarkerStyle(26)
        hist.Draw("P")
        hist.SetStats(True)
        for i, key in enumerate(sorted(track_final.keys())):
            if wild_x_axis:
                xmin, xmax = self.get_wild_axis(track_final[key])
            var_list = track_final[key]
            name = slice_variable+" = "+str(key)
            label = plot_variable+" at "+detector+" ["+utilities.utilities.default_units(plot_variable)+"]"
            hist = self.make_root_histogram(canvas_name, name, var_list, label, 100, [], '', 0, [], xmin, xmax)
            hist.SetMarkerStyle(24)
            hist.Draw("SAMEP")
        self.plots[canvas_name]["canvas"].SetLogy()
        #self.plots[canvas_name]["canvas"].BuildLegend()
        self.process_args[canvas_name] = [self.process_var_one_d, (detector, slice_variable, plot_variable, cuts, hit_predicate)]
        for key in options.keys():
            if key not in self.get_plot(canvas_name)["config"]:
                raise KeyError("Did not recignise plot option "+str(key))
            self.get_plot(canvas_name)["config"][key] = options[key]


    def get_data_var_two_d_hist(self, name, *args):
        track_final = ([], [])
        for event in self.data_loader.events:
            if args[3] and event[args[3]]:
                continue
            for detector_hit in event["data"]:
                if detector_hit["detector"] != args[0]:
                    continue
                #
                val_list = []
                for var in [args[1], args[2]]:
                    if var == "L_kin" or var == "L_canon" or var == "L_field":
                        val = self.get_L_hit(detector_hit, var)
                    elif var == "Bx_map" or var == "By_map" or var == "Bz_map":
                        val = self.get_field(detector_hit["hit"], var)
                    else: 
                        val = detector_hit["hit"][var]
                    val_list.append(val)

                track_final[0].append(val_list[0])
                track_final[1].append(val_list[1])

                #x = detector_hit["hit"][args[1]]
                #y = detector_hit["hit"][args[2]]
                #track_final[0].append(x)
                #track_final[1].append(y)
        return track_final

    def process_var_two_d_hist(self, name, *args):
        track_final = self.get_data_var_two_d_hist(name, *args)
        hist_dict = self.plots[name]["histograms"]
        plot_name = name 
        if plot_name not in hist_dict:
            print "You're not filling hist " + plot_name + " into self.plots!"
            sys.exit()
        hist = hist_dict[plot_name]
        for x, y in izip(*track_final):
                hist.Fill(x, y)

    def birth_var_two_d_hist(self, canvas_name, detector, plot_variable_1, plot_variable_2, cuts=False, xmin = None, xmax = None, ymin = None, ymax = None, wild_x_axis=False, wild_y_axis=False):
        track_final = self.get_data_var_two_d_hist(canvas_name, detector, plot_variable_1, plot_variable_2, cuts)
        if len(track_final) == 0:
            print "No tracks for", detector
            return
        x_list = track_final[0]
        y_list = track_final[1]

        if xmin is None or ymin is None or xmax is None or ymax is None:
            xmin, xmax, ymin, ymax = 0., 0., 0., 0.
            xmin = min([xmin]+x_list)
            xmax = max([xmax]+x_list)
            ymin = min([ymin]+y_list)
            ymax = max([ymax]+y_list)
        if wild_x_axis:
            xmin, xmax = self.get_wild_axis(x_list)
            #xmi, xma, = min(x_list), max(x_list)
            #xmin = xmi - (xma - xmi)/6
            #xmax = xma + (xma - xmi)/6
        if wild_y_axis:
            ymin, ymax = self.get_wild_axis(y_list)
            #ymi, yma = min(y_list), max(y_list) 
            #ymin = ymi - (yma - ymi)/6
            #ymax = yma + (yma - ymi)/6

        name = canvas_name
        label_1 = plot_variable_1+" ["+utilities.utilities.default_units(plot_variable_1)+"]"
        label_2 = plot_variable_2+" ["+utilities.utilities.default_units(plot_variable_2)+"]"
        hist = self.make_root_histogram(canvas_name, name,
          x_list, label_1, 50, y_list, label_2, 50, [],
          xmin, xmax, ymin, ymax)
        #hist = self.make_root_histogram(canvas_name, name,
        #  [-1000], label_1, 100, [-1000], label_2, 100, [],
        #  xmin, xmax, ymin, ymax)
        hist.Draw("COLZ")
        self.process_args[canvas_name] = [self.process_var_two_d_hist, (detector, plot_variable_1, plot_variable_2, cuts)]


    def get_data_var_three_d_hist(self, name, *args):
        track_final = ([], [], [])
        for event in self.data_loader.events:
            if args[4] and event[args[4]]:
                continue
            for detector_hit in event["data"]:
                if detector_hit["detector"] != args[0]:
                    continue
                val_list = []
                for var in [args[1], args[2], args[3]]:
                    #print var
                    if var == "L_kin" or var == "L_canon" or var == "L_field":
                        val = self.get_L_hit(detector_hit, var)
                    elif var == "Bx_map" or var == "By_map" or var == "Bz_map":
                        val = self.get_field(detector_hit["hit"], var)
                    else: 
                        val = detector_hit["hit"][var]
                    val_list.append(val)

                track_final[0].append(val_list[0])
                track_final[1].append(val_list[1])
                track_final[2].append(val_list[2])
                    
                """x = detector_hit["hit"][args[1]]
                y = detector_hit["hit"][args[2]]
                z = detector_hit["hit"][args[3]]

                track_final[0].append(x)
                track_final[1].append(y)
                track_final[2].append(z)"""
                break # next event please
        return track_final

    def process_var_three_d_hist(self, name, *args):
        track_final = self.get_data_var_three_d_hist(name, *args)
        hist_dict = self.plots[name]["histograms"]
        plot_name = name 
        if plot_name not in hist_dict:
            print "You're not filling hist " + plot_name + " into self.plots!"
            sys.exit()
        hist = hist_dict[plot_name]
        for x, y, z in izip(*track_final):
                hist.Fill(x, y, z)

    def birth_var_three_d_hist(self, name, detector, plot_variable_1, plot_variable_2, plot_variable_3, cuts=False, wild_x_axis=False, wild_y_axis=False, wild_z_axis=False):
        track_final = self.get_data_var_three_d_hist(name, detector, plot_variable_1, plot_variable_2, plot_variable_3, cuts)
        if len(track_final) == 0:
            print "No tracks for", detector
            return
        xmin, xmax, ymin, ymax = -125., 125., -125., 125.
        zmin, zmax = -0., 0. # New
        x_list = track_final[0]
        y_list = track_final[1]
        z_list = track_final[2] # New
        xmin = min([xmin]+x_list)
        xmax = max([xmax]+x_list)
        ymin = min([ymin]+y_list)
        ymax = max([ymax]+y_list)
        zmin = min([zmin]+z_list) # New
        zmax = max([zmax]+z_list) # New
        if wild_x_axis:
            xmin, xmax = self.get_wild_axis(x_list)
        if wild_y_axis:
            ymin, ymax = self.get_wild_axis(y_list)
        if wild_z_axis:
            zmin, zmax = self.get_wild_axis(z_list)

        name = "three_d_h_"+name
        canvas_name = name

        label_1 = plot_variable_1+" ["+utilities.utilities.default_units(plot_variable_1)+"]"
        label_2 = plot_variable_2+" ["+utilities.utilities.default_units(plot_variable_2)+"]"
        label_3 = plot_variable_3+" ["+utilities.utilities.default_units(plot_variable_3)+"]"

        #hist = self.make_root_histogram_3d(canvas_name, name,
        #  x_list, label_1, 100, y_list, label_2, 100, z_list, label_3, 100, [],
        #  xmin, xmax, ymin, ymax, zmin, zmax) # New
        hist = self.make_root_histogram_3d(canvas_name, name,
          x_list, label_1, 50, y_list, label_2, 50, z_list, label_3, 100, [],
          xmin, xmax, ymin, ymax, zmin, zmax) # New

        hist.Draw()
        projhist = self.project_root_histogram_3d(canvas_name, name, "yx")
        projhist.Draw("COLZ")
        self.process_args[canvas_name] = [self.process_var_three_d_hist, (detector, plot_variable_1, plot_variable_2, plot_variable_3, cuts)]



    def death_three_d_hist(self):
        for name in self.plots:
            if "three_d_h_" not in name:
                continue
            elif "_profile_" in name:
                continue
            for hist_name in self.plots[name]["histograms"]:
                projhist = self.project_root_histogram_3d(name, hist_name, "yx")


    ############# If do ang_mom MC, get residual of ang mom vars
    def get_data_detector_residuals(self, det_name, virt_name):
        if det_name in ["tof01", "tof12", "tof0", "tof1", "tof2"]:
            return {}, {}, {}
        if "tku_" in det_name or "tkd_" in det_name:
            residual_dict = {"L_kin":[], "L_field":[], "L_canon":[],} # TomL
            #residual_dict = {"x":[], "y":[], "z":[], "px":[], "py":[], "pz":[]}
        elif "global" in det_name:
            residual_dict = {"L_kin":[], "L_field":[], "L_canon":[],} # TomL
            #residual_dict = {"x":[], "y":[], "z":[], "px":[], "py":[], "pz":[]}
        mc_dict = copy.deepcopy(residual_dict)
        det_dict = copy.deepcopy(residual_dict)
            
        if det_name in ["tku_tp", "tof0", "tof1"] or "global_through" in det_name:
            cut = "upstream_cut"
        else:
            cut = "downstream_cut"
        for event in self.data_loader.events:
            if event[cut]:
                continue
            vhit, thit = None, None
            # setting to detector_hit, not detector_hit["hit"] only works for L_'s
            for detector_hit in event["data"]:
                if detector_hit["detector"] == virt_name:
                    vhit = detector_hit
                elif detector_hit["detector"] == det_name:
                    thit = detector_hit
                else:
                    continue
                if vhit != None and thit != None:
                    for key in residual_dict.keys():
                        tvar = self.get_L_hit(thit, key)
                        vvar = self.get_L_hit(vhit, key)
                        residual_dict[key].append(tvar - vvar)
                        mc_dict[key].append(vvar)
                        det_dict[key].append(tvar)
                    break # next event please
        return residual_dict, mc_dict, det_dict

    def process_data_detector_residuals(self):
        for detector, virtual_station_list in self.mc_stations.iteritems():
            virtual_station = virtual_station_list[0]
            residual_dict, mc_dict, det_dict = \
                     self.get_data_detector_residuals(detector, virtual_station)
            for var in sorted(residual_dict.keys()):
                canvas_name = "mc_residual_"+detector+"_"+var
                data = residual_dict[var]
                hist = self.plots[canvas_name]["histograms"][var]
                for item in data:
                    hist.Fill(item)

                canvas_name = "mc_compare_"+detector+"_"+var

                mc_data = mc_dict[var]
                hist = self.plots[canvas_name]["histograms"]["mc_"+var]
                #for item in mc_data:
                #    hist.Fill(item)
                try: # TomL
                    for item in mc_data: # TomL
                        hist.Fill(item) # TomL
                except TypeError: # TomL
                    print "Process data detector residuals in mc_plotter failed to Fill with type error" # TomL
                    print canvas_name, detector, var, virtual_station # TomL
                    print item # TomL
                    sys.excepthook(*sys.exc_info()) # TomL

                det_data = det_dict[var]
                hist = self.plots[canvas_name]["histograms"]["det_"+var]
                for item in det_data:
                    hist.Fill(item)

    def get_x_min_max(self, var):
        #utilities.utilities.fractional_axis_range(data, 0.95)
        keys = {
            "L_kin":(-0.75, 0.75),
            "L_field":(-0.75, 0.75),
            "L_canon":(-0.75, 0.75),
        }
        return keys[var]

    def get_x_min_max_compare(self, var):
        #utilities.utilities.fractional_axis_range(data, 0.95)
        keys = {
            "L_kin":(-7., 0.),
            "L_field":(0., 7.),
            "L_canon":(-3.5, 3.5),
        }
        return keys[var]

    axis_labels = {"L_kin":"L_{kin}(meas) - L_{kin}(true) [MeV/c m]",
                   "L_field":"L_{field}(meas) - L_{field}(true) [MeV/c m]",
                   "L_canon":"L_{canon}(meas) - L_{canon}(true) [MeV/c m]",}

    cmp_axis_labels = {"L_kin":"L_{kin} [MeV/c m]",
                       "L_field":"L_{field} [MeV/c m]",
                       "L_canon":"L_{canon} [MeV/c m]",}


    def birth_data_detector_residuals(self):
        dummy_canvas = xboa.common.make_root_canvas("dummy")
        for detector, virtual_station_list in self.mc_stations.iteritems():
            #print "Birth residuals", detector, virtual_station_list
            virtual_station = virtual_station_list[0]
            residual_dict, mc_dict, det_dict = \
                     self.get_data_detector_residuals(detector, virtual_station)
            for var in sorted(residual_dict.keys()):
                # residual distributions
                canvas_name = "mc_residual_"+detector+"_"+var
                data = residual_dict[var]
                xmin, xmax = self.get_x_min_max(var)
                if len(data) == 0:
                    print "WARNING - Failed to find residual data for "+var+" "+detector+" "+virtual_station
                    data = [xmax+(xmax-xmin)*100.]
                dummy_canvas.cd() # make sure we don't accidentally overwrite "current" canvas
                hist = self.make_root_histogram(canvas_name, var, data, self.axis_labels[var], 100, [], '', 0, [], xmin, xmax)
                hist.Draw()

                # superimpose mc over recon mc
                canvas_name = "mc_compare_"+detector+"_"+var
                xmin, xmax = self.get_x_min_max_compare(var)
                if len(data) == 0:
                    data = [xmax+(xmax-xmin)*100.]
                dummy_canvas.cd() # make sure we don't accidentally overwrite "current" canvas

                mc_data = mc_dict[var]
                hist = self.make_root_histogram(canvas_name, "mc_"+var, mc_data, self.cmp_axis_labels[var], 100, [], '', 0, [], xmin, xmax)
                hist.SetFillColor(ROOT.kOrange-2)
                hist.Draw()

                det_data = det_dict[var]
                hist = self.make_root_histogram(canvas_name, "det_"+var, det_data, self.cmp_axis_labels[var], 100, [], '', 0, [], xmin, xmax)
                hist.SetMarkerStyle(20)
                hist.Draw("P E1 PLC SAME")
                dummy_canvas.cd() # make sure we don't accidentally overwrite "current" canvas

    # Plot change in ang mom across absorber
    def birth_L_res(self):
        for L in ["L_canon", "L_kin", "L_field"]:
            L_tku_cut_us, L_tku_cut_ds, L_tku_all = self.get_tracker_hit_data("tku", L, self.has_both_trackers)
            L_tkd_cut_us, L_tkd_cut_ds, L_tkd_all = self.get_tracker_hit_data("tkd", L, self.has_both_trackers)
            dL_cut_us = [L_tku - L_tkd_cut_us[i] for i, L_tku in enumerate(L_tku_cut_us)]
            dL_cut_ds = [L_tku - L_tkd_cut_ds[i] for i, L_tku in enumerate(L_tku_cut_ds)]
            dL_all = [L_tku - L_tkd_all[i] for i, L_tku in enumerate(L_tku_all)]
            # flipped L_res
            dL2_cut_us = [L_tkd - L_tku_cut_us[i] for i, L_tkd in enumerate(L_tkd_cut_us)]
            dL2_cut_ds = [L_tkd - L_tku_cut_ds[i] for i, L_tkd in enumerate(L_tkd_cut_ds)]
            dL2_all = [L_tkd - L_tku_all[i] for i, L_tkd in enumerate(L_tkd_all)]

            axis = L+"_{tku} - "+L+"_{tkd} [MeV/c m]"
            hist = self.make_root_histogram(L+"_res", L+"_res all", dL_all, axis, 100, [], '', 0, [], -3., 3.)
            hist_cut_us = self.make_root_histogram(L+"_res", L+"_res us cut", dL_cut_us, axis, 100, [], '', 0, [], -3., 3.)
            hist_cut_ds = self.make_root_histogram(L+"_res", L+"_res ds cut", dL_cut_ds, axis, 100, [], '', 0, [], -3., 3.)
            hist.Draw()
            hist_cut_us.Draw("SAME")
            hist_cut_ds.Draw("SAME")
            self.get_plot(L+"_res")["config"]["draw_1d_cuts"] = True
            # flipped
            axis = L+"_{tkd} - "+L+"_{tku} [MeV/c m]"
            hist = self.make_root_histogram(L+"_res2", L+"_res2 all", dL2_all, axis, 100, [], '', 0, [], -3., 3.)
            hist_cut_us = self.make_root_histogram(L+"_res2", L+"_res2 us cut", dL2_cut_us, axis, 100, [], '', 0, [], -3., 3.)
            hist_cut_ds = self.make_root_histogram(L+"_res2", L+"_res2 ds cut", dL2_cut_ds, axis, 100, [], '', 0, [], -3., 3.)
            hist.Draw()
            hist_cut_us.Draw("SAME")
            hist_cut_ds.Draw("SAME")
            self.get_plot(L+"_res2")["config"]["draw_1d_cuts"] = True


            hist = self.make_root_histogram(L+"_res_vs_"+L+"_tku", L+"_res_vs_"+L+"_tku", L_tku_cut_ds, L+"_{tku} [MeV/c m]", 100,
                                                              dL_cut_ds, L+"_{tku} - "+L+"_{tkd} [MeV/c m]", 100,
                                                              [], -2., 2., -3., 3.)
            hist.Draw("COLZ")

    def process_L_res(self):
        for L in ["L_canon", "L_kin", "L_field"]:
            L_tku_cut_us, L_tku_cut_ds, L_tku_all = self.get_tracker_hit_data("tku", L, self.has_both_trackers)
            L_tkd_cut_us, L_tkd_cut_ds, L_tkd_all = self.get_tracker_hit_data("tkd", L, self.has_both_trackers)
            dL_cut_us = [L_tku - L_tkd_cut_us[i] for i, L_tku in enumerate(L_tku_cut_us)]
            dL_cut_ds = [L_tku - L_tkd_cut_ds[i] for i, L_tku in enumerate(L_tku_cut_ds)]
            dL_all = [L_tku - L_tkd_all[i] for i, L_tku in enumerate(L_tku_all)]
            # flipped L_res
            dL2_cut_us = [L_tkd - L_tku_cut_us[i] for i, L_tkd in enumerate(L_tkd_cut_us)]
            dL2_cut_ds = [L_tkd - L_tku_cut_ds[i] for i, L_tkd in enumerate(L_tkd_cut_ds)]
            dL2_all = [L_tkd - L_tku_all[i] for i, L_tkd in enumerate(L_tkd_all)]

            L_res_hists = self.get_plot(L+"_res")["histograms"]
            for data, hist_key in (dL_cut_us, "us cut"), (dL_cut_ds, "ds cut"), (dL_all, "all"):
                hist = L_res_hists[L+"_res "+hist_key]
                for item in data:
                    hist.Fill(item)
            # flipped
            L_res_hists = self.get_plot(L+"_res2")["histograms"]
            for data, hist_key in (dL2_cut_us, "us cut"), (dL2_cut_ds, "ds cut"), (dL2_all, "all"):
                hist = L_res_hists[L+"_res2 "+hist_key]
                for item in data:
                    hist.Fill(item)

            L_res_vs_L_hist = self.get_plot(L+"_res_vs_"+L+"_tku")["histograms"]
            hist = L_res_vs_L_hist[L+"_res_vs_"+L+"_tku"]
            for i in range(len(L_tku_cut_ds)):
                hist.Fill(L_tku_cut_ds[i], dL_cut_ds[i])

    def get_tracker_hit_data(self, tracker, var, event_predicate):
        data_all = []
        data_cut_us = []
        data_cut_ds = []
        other_tracker = {"tku":"tkd", "tkd":"tku"}[tracker]
        for event in self.data_loader.events:
            if event[tracker] == None:
                continue
            if event_predicate != None and not event_predicate(event):
                continue
            if var == "L_kin" or var == "L_canon" or var == "L_field":
            #if var == "L":
                data = self.get_L_tracker(event[tracker], tracker, var)
            else:
                data = event[tracker][var]
            data_all.append(data)
            if not self.will_cut_us(event):
                data_cut_us.append(data)
            if not self.will_cut_ds(event):
                data_cut_ds.append(data)
        return data_cut_us, data_cut_ds, data_all



    def death_truncated_L(self):
        #for L in ["L_canon", "L_kin", "L_field"]:
        for L in ["L_canon",]:
            for xmin, xmax in [(-3.5, 3.5), (-3.25, 3.25), (-3., 3.), (-2.75, 2.75),
                                   (-2.5, 2.5), (-2.25, 2.25), (-2., 2.), (-1.75, 1.75),
                                   (-1.5, 1.5), (-1.25, 1.25), (-1., 1.), (-0.75, 0.75),
                                   (-0.5, 0.5), (-0.25, 0.25),]:
                reco_mean_dict = {}
                mc_mean_dict = {}

                for detector, virt_station_list in self.mc_stations.iteritems():
                    #if "tku" not in detector and "tkd" not in detector and "diffuser" not in detector:
                    if "tku" not in detector and "tkd" not in detector:
                        continue
                    station_list = [detector]
                    if self.do_ang_mc is not None:
                        station_list = [detector, virt_station_list[0]] 
                    for station in station_list:
                        name = L+"_at_"+station+'_ds_cut'
                        hist_dict = self.plots[name]["histograms"]
                        plot_name = "pid = -13"

                        if plot_name not in hist_dict:
                            print "[ERROR]:", plot_name, "not in hist dict:\
                                  self.plots["+name+"][histograms]["+plot_name+"]"
                            continue
                        hist = hist_dict[plot_name]
                        hist.GetXaxis().SetRangeUser(xmin, xmax)
                        mean = hist.GetMean()
                        for z, dummy, det_name in self.config.detectors + self.config.virtual_detectors:
                            if det_name == station or 'mc_'+det_name == station \
                            or 'mc_virtual_'+det_name == station:
                                zpos = z 
                                break
                        if 'mc_virtual' in station:
                            mean_dict = mc_mean_dict
                        else:
                            mean_dict = reco_mean_dict
                        #mean_dict[station] = {"mean":mean, "zpos":zpos}
                        mean_dict[zpos] = mean

                #for station in self.var_out.keys():
                #    name = L+"_at_"+station+'_ds_cut'
                #    hist_dict = self.plots[name]["histograms"]
                #    plot_name = "pid = -13"

                #    if plot_name not in hist_dict:
                #        print "[ERROR]:", plot_name, "not in hist dict:\
                #              self.plots["+name+"][histograms]["+plot_name+"]"
                #        continue
                #    hist = hist_dict[plot_name]
                #    hist.GetXaxis().SetRangeUser(xmin, xmax)
                #    mean = hist.GetMean()
                #    for z, dummy, det_name in self.config.detectors + self.config.virtual_detectors:
                #        if det_name == station or 'mc_'+det_name == station \
                #        or 'mc_virtual_'+det_name == station:
                #            zpos = z 
                #            break
                #    if 'mc_virtual' in station:
                #        mean_dict = mc_mean_dict
                #    else:
                #        mean_dict = reco_mean_dict
                #    #mean_dict[station] = {"mean":mean, "zpos":zpos}
                #    mean_dict[zpos] = mean

                z_list = sorted(reco_mean_dict.keys())
                var_list = [reco_mean_dict[z] for z in z_list]

                name = L+"_truncated_"+str(xmin)+'_to_'+str(xmax)
                axis = L+" ds"
                hist, graph = self.make_root_graph(name, name+"_source_tkd",
                              z_list, "z [m]", var_list, axis, True,
                              None, None, None, None)
                #if len(self.get_plot(name)["histograms"]) == 1:
                #    hist.Draw()
                hist.Draw()
                graph.SetMarkerStyle(20)
                graph.SetMarkerColor(ROOT.kRed)
                graph.Draw("p l same")

                z_list = sorted(mc_mean_dict.keys())
                var_list = [mc_mean_dict[z] for z in z_list]

                hist, graph = self.make_root_graph(name, name+"_source_mc_tkd",
                              z_list, "z [m]", var_list, axis, True,
                              None, None, None, None)
                graph.SetMarkerStyle(20)
                graph.SetMarkerColor(ROOT.kViolet)
                graph.Draw("p l same")

                det_list = [det for det in self.config.detectors if det[0]>self.min_z_us and det[0]<self.max_z_ds] # only use detectors in range
                det_list += [virt for virt in self.config.virtual_detectors if virt[2] == "virtual_absorber_centre"]
                #for z_det, dummy, detector in self.config.detectors:
                for z_det, dummy, detector in det_list:
                    var_min, var_max = min(var_list), max(var_list)
                    delta = var_max-var_min+1
                    var_max += delta
                    var_min -= delta
                    hist, graph = self.make_root_graph(name, name+"_"+detector,
                              [z_det*1e-3, z_det*1e-3], "z [m]", [var_min, var_max], axis, True,
                              None, None, None, None)
                    if "tku" in detector or "tkd" in detector:
                        line_color = ROOT.kBlue
                    elif "tof" in detector or "cal" in detector:
                        line_color = ROOT.kRed
                    else:
                        line_color = ROOT.kGreen
                    graph.SetLineColor(line_color)
                    graph.SetLineStyle(2)
                    graph.Draw("same l")

    def print_data(self):
        """
        Write the angular momentum evolution to disk.
        """
        fout = open(self.plot_dir+"/ang_mom.json", "w")
        #for detector in self.var_out:
            #if type(self.var_out[detector]) != type({}):
            #    continue
            #print self.var_out[detector].keys()
            #try:
            #    del self.amplitudes[suffix]["amplitude_dict_upstream"]
            #    del self.amplitudes[suffix]["amplitude_dict_downstream"]
            #except KeyError:
            #    pass
        out_str = json.dumps(self.ellipse_dict, indent=2)
        fout.write(out_str)
        fout.close()

    def load_corrections(self, file_name):
        """
        ----- NOT YET USED -----
        Load the angular momentum corrections to be applied during this
        analysis. Loads reco errors????? inefficiency?????
        So far no corrections propagated this way
        """
        fin = open(file_name)
        ang_str = fin.read()
        src_angmom = json.loads(ang_str)
        src_angmom["source"] = file_name
        for key in "inefficiency", "reco_error":
            self.var_out[key] = src_angmom[key]
        
    def load_one_error(self, file_name, scale):
        """
        Load the angular momentum analysis output for a given uncertainty source
        """
        fin = open(file_name)
        ang_str = fin.read()
        angmom = json.loads(ang_str)
        angmom["source"] = file_name
        angmom["scale"] = scale
        # for recon error we want the corrections
        # for storage concerns delete unnecessary sub-dictionaries (not yet used)
        #for tgt_1 in self.var_out.keys():
        #    for tgt_2 in "ds",: #"us":
        #        try:
        #            del angmom[tgt_1][tgt_2]
        #        except KeyError:
        #            pass
        #            #print "Could not find", tgt_1, tgt_2, "while loading errors"
        return angmom 

    def load_systematic_errors(self):
        """
        Load errors from each systematic passed from config file
        This currently only loads differences in means from systematics,
        not separate differences in reco effects and performance effects
        """
        systematics = self.config_anal["ang_mom_systematics"]
        for suffix in systematics:
            print "Loading", suffix
            if suffix not in self.sys_errors:
                self.sys_errors[suffix] = {}
            for ref_key in ["detector_reference", "performance_reference"]:
                ref_src = systematics[suffix][ref_key]
                if ref_src == None:
                    self.sys_errors[suffix][ref_key] = None
                else:
                    self.sys_errors[suffix][ref_key] = \
                                              self.load_one_error(ref_src, None)
                print "   Loaded reference", suffix, ref_key, ref_src, \
                                            type(self.sys_errors[suffix][ref_key])
            for us_ds in ["us", "ds"]:
                if us_ds not in self.sys_errors[suffix]:
                    self.sys_errors[suffix][us_ds] = {}
                for key in ["detector_systematics", "performance_systematics"]:
                    err_src_dict = systematics[suffix][us_ds][key]
                    print err_src_dict
                    self.sys_errors[suffix][us_ds][key] = [
                        self.load_one_error(err_src, scale) \
                              for err_src, scale in err_src_dict.iteritems()
                    ]
                    print "  Loaded", len(self.sys_errors[suffix][us_ds][key]), us_ds, key, "systematics"


    def combine_sys_errors(self):
        """
        Runs through sys errors at each station and combines in quadrature
        """
        for detector in self.var_out: 
            for cut in self.var_out[detector]: # us / ds cut
                ellipse = self.get_ellipse(detector, cut)
                for L in ("L_canon", "L_kin", "L_field"):
                    ellipse["Sys_Error_"+L] = 0
                    for suffix in self.sys_errors:
                        for us_ds in ["us", "ds"]: # us / ds systematics
                            for key in ["detector", "performance"]:
                                #sys_list_trial = self.sys_errors[suffix][us_ds]["performance_systematics"]
                                sys_list = self.sys_errors["reco"][us_ds][key+"_systematics"]
                                reference = self.sys_errors["reco"][key+"_reference"]
                                for sys in sys_list:
                                    #do some error combination for each detector ....
                                    old_error = ellipse["Sys_Error_"+L]
                                    reference_mean = reference[detector][cut][L]
                                    sys_mean = sys[detector][cut][L]
                                    this_error = sys[detector][cut][L] - reference[detector][cut][L]
                                    new_error = (old_error*old_error + this_error*this_error)**0.5
                                    ellipse["Sys_Error_"+L] = new_error
                                    continue
                    print "Detector:", detector
                    print "Combined sys error for L:", ellipse["Sys_Error_"+L]


    def combine_stat_sys_errors(self):
        """
        Runs through combined sys + stat error for each station and combine in quadrature
        """
        for detector in self.var_out: 
            for cut in self.var_out[detector]: # us / ds cut
                ellipse = self.get_ellipse(detector, cut)
                for L in ("L_canon", "L_kin", "L_field"):
                    ellipse["Total_Error_"+L] = (ellipse["Sys_Error_"+L]*ellipse["Sys_Error_"+L] + ellipse["SE_"+L]*ellipse["SE_"+L])**0.5
                    print "Detector:", detector
                    print "Combined stat+sys error for L:", ellipse["Total_Error_"+L]



