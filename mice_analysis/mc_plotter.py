import xboa.common
import json
import copy
import numpy
import sys

from itertools import izip

import utilities.cdb_tof_triggers_lookup
import ROOT
from xboa.bunch import Bunch
import utilities.utilities

from analysis_base import AnalysisBase

class MCPlotter(AnalysisBase):
    def __init__(self, config, config_anal, data_loader):
        super(MCPlotter, self).__init__(config, config_anal, data_loader)
        self.process_args = {}
        self.mc_stations = {}
        self.failed_pids = {}
        self.get_cut_list()

    def get_cut_list(self):
        self.us_cut_list = self.config.cut_report[0]
        self.us_cut_list = set(self.us_cut_list)
        self.us_cut_list.discard("hline")
        self.us_cut_list.discard("all events")
        self.us_cut_list = list(self.us_cut_list)
        self.ds_cut_list = self.config.cut_report[1]
        self.ds_cut_list = set(self.ds_cut_list)
        self.ds_cut_list.discard("hline")
        self.ds_cut_list = list(self.ds_cut_list)

    def get_sp_dict(self):
        sp_detector_dict = {} 
        sp_detector_dict["tku_sp_1"] = "mc_virtual_tku_tp"
        sp_detector_dict["tkd_sp_1"] = "mc_virtual_tkd_tp"
        for station in range(2,6):
            sp_detector_dict["tku_sp_"+str(station)] = "mc_virtual_tku_"+str(station)
            sp_detector_dict["tkd_sp_"+str(station)] = "mc_virtual_tkd_"+str(station)
        return sp_detector_dict

    def birth(self):
        self.set_plot_dir("mc_plots")
        self.mc_stations = self.config.mc_plots["mc_stations"]
        self.sp_detector_dict = self.get_sp_dict()
        pid_colors = {211:ROOT.kGreen, -13:ROOT.kRed, -11:ROOT.kBlue-1, +11:ROOT.kBlue+1}
        cluster_colors = {1:ROOT.kBlue, 2:ROOT.kRed, 3:ROOT.kGreen}
        for detector, virt_station_list in self.mc_stations.iteritems():
            #print "Doing MC plots comparing.. "
            #print " detector : " + detector
            #print " virt_station_list[0] : " + virt_station_list[0]

            # Tracker plots using all stations
            #if "tku_tp" in detector or "tkd_tp" in detector:
            for virt_station in virt_station_list: 
                #self.birth_var_two_d_scatter("x_vs_y_at_"+virt_station, virt_station, "pid", "x", "y", pid_colors, True) # TomL
                #self.birth_var_two_d_scatter("px_vs_py_at_"+virt_station, virt_station, "pid", "px", "py", pid_colors, True) # TomL
                self.birth_var_two_d_hist("x_vs_y_at_"+virt_station+"_us_cut_hist", virt_station, "x", "y", "upstream_cut", xmin = -150, xmax = 150, ymin = -150, ymax = 150) # TomL
                self.birth_var_two_d_hist("x_vs_y_at_"+virt_station+"_ds_cut_hist", virt_station, "x", "y", "downstream_cut", -150, 150, -150, 150) # TomL
                self.birth_var_two_d_hist("px_vs_py_at_"+virt_station+"_us_cut_hist", virt_station, "px", "py", "upstream_cut", -150, 150, -150, 150) # TomL
                self.birth_var_two_d_hist("px_vs_py_at_"+virt_station+"_ds_cut_hist", virt_station, "px", "py", "downstream_cut", -150, 150, -150, 150) # TomL
                self.birth_var_two_d_hist("x_vs_y_at_"+virt_station+"_us_cut_hist_large", virt_station, "x", "y", "upstream_cut", xmin = -250, xmax = 250, ymin = -250, ymax = 250) # TomL
                self.birth_var_two_d_hist("x_vs_y_at_"+virt_station+"_ds_cut_hist_large", virt_station, "x", "y", "downstream_cut", -250, 250, -250, 250) # TomL
                self.birth_var_two_d_hist("px_vs_py_at_"+virt_station+"_us_cut_hist_large", virt_station, "px", "py", "upstream_cut", -250, 250, -250, 250) # TomL
                self.birth_var_two_d_hist("px_vs_py_at_"+virt_station+"_ds_cut_hist_large", virt_station, "px", "py", "downstream_cut", -250, 250, -250, 250) # TomL


            # Tracker plots only using tk*_tp
            virt_station = virt_station_list[0]
            # but first doing xy & pxpy for all mc stations
            # moved these to loop above
            #self.birth_var_two_d_hist("x_vs_y_at_"+virt_station+"_us_cut_hist_large", virt_station, "x", "y", "upstream_cut", xmin = -250, xmax = 250, ymin = -250, ymax = 250) # TomL
            #self.birth_var_two_d_hist("x_vs_y_at_"+virt_station+"_ds_cut_hist_large", virt_station, "x", "y", "downstream_cut", -250, 250, -250, 250) # TomL
            #self.birth_var_two_d_hist("px_vs_py_at_"+virt_station+"_us_cut_hist_large", virt_station, "px", "py", "upstream_cut", -250, 250, -250, 250) # TomL
            #self.birth_var_two_d_hist("px_vs_py_at_"+virt_station+"_ds_cut_hist_large", virt_station, "px", "py", "downstream_cut", -250, 250, -250, 250) # TomL

            self.birth_var_one_d("p_at_"+virt_station, virt_station, "pid", "p", pid_colors, "us cut", 0., 300.)
            self.birth_var_one_d("pt_at_"+virt_station, virt_station, "pid", "pt", pid_colors, "us cut", 0., 100.)
            self.birth_var_one_d("r_at_"+virt_station, virt_station, "pid", "r", pid_colors, "us cut", 0., 300.)
            self.birth_var_two_d_hist("pt_vs_pz_at_"+virt_station+"_us_cut_hist", virt_station, "pt", "pz", "upstream_cut")
            self.birth_var_two_d_scatter("x_vs_px_at_"+virt_station, virt_station, "pid", "x", "px", pid_colors, True)
            self.birth_var_two_d_scatter("pt_vs_pz_at_"+virt_station, virt_station, "pid", "pt", "pz", pid_colors, True) # TomL
            self.birth_var_two_d_scatter("pt_vs_pz_at_"+detector, detector, "pid", "pt", "pz", pid_colors, True) # TomL
            self.birth_var_two_d_scatter("pt_vs_p_at_"+virt_station+"_cut", virt_station, "pid", "pt", "p", pid_colors, True) # TomL
            self.birth_var_two_d_scatter("pt_vs_p_at_"+detector+"_cut", detector, "pid", "pt", "p", pid_colors, True) # TomL
            self.birth_var_two_d_scatter("pt_vs_p_at_"+virt_station+"_all", virt_station, "pid", "pt", "p", pid_colors, False) # TomL
            self.birth_var_two_d_scatter("pt_vs_p_at_"+detector+"_all", detector, "pid", "pt", "p", pid_colors, False) # TomL
            self.birth_var_two_d_residual("pt_residual_vs_pt_at_"+detector+"_cut", detector, virt_station, "pid", "pt", "pt", pid_colors, False, True) # TomL
            self.birth_var_two_d_residual("pt_residual_vs_pt_at_"+detector+"_all", detector, virt_station, "pid", "pt", "pt", pid_colors, False, False) # TomL
            self.birth_var_two_d_residual("pz_residual_vs_pt_at_"+detector+"_cut", detector, virt_station, "pid", "pz", "pt", pid_colors, False, True) # TomL
            self.birth_var_two_d_residual("pz_residual_vs_pt_at_"+detector+"_all", detector, virt_station, "pid", "pz", "pt", pid_colors, False, False) # TomL
            self.birth_var_two_d_residual("p_residual_vs_pt_at_"+detector+"_cut", detector, virt_station, "pid", "p", "pt", pid_colors, False, True) # TomL
            self.birth_var_two_d_residual("p_residual_vs_pt_at_"+detector+"_all", detector, virt_station, "pid", "p", "pt", pid_colors, False, False) # TomL
            self.birth_var_two_d_residual("pz_residual_vs_pt_residual_at_"+detector, detector, virt_station, "pid", "pz", "pt", pid_colors, True, True) # TomL
            self.birth_var_two_d_residual("p_residual_vs_pt_residual_at_"+detector, detector, virt_station, "pid", "p", "pt", pid_colors, True, True) # TomL

            # reco px vs py
            self.birth_var_three_d_hist_residual("px_vs_py_vs_pt_residual_at_"+detector+"_all", detector, virt_station, "px", "py", "pt", TruthX = False, TruthY = False, TruthZ = False, doresidualX = False, doresidualY = False, doresidualZ = True) # TomL
            self.birth_var_three_d_hist_residual("px_vs_py_vs_pt_residual_at_"+detector+"_us_cut", detector, virt_station, "px", "py", "pt", TruthX = False, TruthY = False, TruthZ = False, doresidualX = False, doresidualY = False, doresidualZ = True, cuts = "upstream_cut") # TomL
            self.birth_var_three_d_hist_residual("px_vs_py_vs_pt_residual_at_"+detector+"_ds_cut", detector, virt_station, "px", "py", "pt", TruthX = False, TruthY = False, TruthZ = False, doresidualX = False, doresidualY = False, doresidualZ = True, cuts = "downstream_cut") # TomL

            # truth px vs py
            self.birth_var_three_d_hist_residual("px_truth_vs_py_truth_vs_pt_residual_at_"+detector+"_all", detector, virt_station, "px", "py", "pt", TruthX = True, TruthY = True, TruthZ = False, doresidualX = False, doresidualY = False, doresidualZ = True) # TomL
            self.birth_var_three_d_hist_residual("px_truth_vs_py_truth_vs_pt_residual_at_"+detector+"_us_cut", detector, virt_station, "px", "py", "pt", TruthX = True, TruthY = True, TruthZ = False, doresidualX = False, doresidualY = False, doresidualZ = True, cuts = "upstream_cut") # TomL
            self.birth_var_three_d_hist_residual("px_truth_vs_py_truth_vs_pt_residual_at_"+detector+"_ds_cut", detector, virt_station, "px", "py", "pt", TruthX = True, TruthY = True, TruthZ = False, doresidualX = False, doresidualY = False, doresidualZ = True, cuts = "downstream_cut") # TomL

            # New requested plots
            # vs Px residual
            # reco px vs py
            self.birth_var_three_d_hist_residual("px_vs_py_vs_px_residual_at_"+detector+"_us_cut", detector, virt_station, "px", "py", "px", TruthX = False, TruthY = False, TruthZ = False, doresidualX = False, doresidualY = False, doresidualZ = True, cuts = "upstream_cut") # TomL
            self.birth_var_three_d_hist_residual("px_vs_py_vs_px_residual_at_"+detector+"_ds_cut", detector, virt_station, "px", "py", "px", TruthX = False, TruthY = False, TruthZ = False, doresidualX = False, doresidualY = False, doresidualZ = True, cuts = "downstream_cut") # TomL

            # truth px vs py
            self.birth_var_three_d_hist_residual("px_truth_vs_py_truth_vs_px_residual_at_"+detector+"_us_cut", detector, virt_station, "px", "py", "px", TruthX = True, TruthY = True, TruthZ = False, doresidualX = False, doresidualY = False, doresidualZ = True, cuts = "upstream_cut") # TomL
            self.birth_var_three_d_hist_residual("px_truth_vs_py_truth_vs_px_residual_at_"+detector+"_ds_cut", detector, virt_station, "px", "py", "px", TruthX = True, TruthY = True, TruthZ = False, doresidualX = False, doresidualY = False, doresidualZ = True, cuts = "downstream_cut") # TomL

            # vs Py residual
            # reco px vs py
            self.birth_var_three_d_hist_residual("px_vs_py_vs_py_residual_at_"+detector+"_us_cut", detector, virt_station, "px", "py", "py", TruthX = False, TruthY = False, TruthZ = False, doresidualX = False, doresidualY = False, doresidualZ = True, cuts = "upstream_cut") # TomL
            self.birth_var_three_d_hist_residual("px_vs_py_vs_py_residual_at_"+detector+"_ds_cut", detector, virt_station, "px", "py", "py", TruthX = False, TruthY = False, TruthZ = False, doresidualX = False, doresidualY = False, doresidualZ = True, cuts = "downstream_cut") # TomL

            # truth px vs py
            self.birth_var_three_d_hist_residual("px_truth_vs_py_truth_vs_py_residual_at_"+detector+"_us_cut", detector, virt_station, "px", "py", "py", TruthX = True, TruthY = True, TruthZ = False, doresidualX = False, doresidualY = False, doresidualZ = True, cuts = "upstream_cut") # TomL
            self.birth_var_three_d_hist_residual("px_truth_vs_py_truth_vs_py_residual_at_"+detector+"_ds_cut", detector, virt_station, "px", "py", "py", TruthX = True, TruthY = True, TruthZ = False, doresidualX = False, doresidualY = False, doresidualZ = True, cuts = "downstream_cut") # TomL


        for station in range(1,6):
            station = str(station)
            # pid plots -- not working -- no pids from spacepoints I guess?
            #self.birth_var_two_d_scatter("tku_spacepoints_pids_station_"+station+"_all", "tku_sp_"+station, "pid", "x", "y", pid_colors)
            #self.birth_var_two_d_scatter("tku_spacepoints_pids_station_"+station+"_cut", "tku_sp_"+station, "pid", "x", "y", pid_colors, True)
            #self.birth_var_two_d_scatter("tkd_spacepoints_pids_station_"+station+"_all", "tkd_sp_"+station, "pid", "x", "y", pid_colors)
            #self.birth_var_two_d_scatter("tkd_spacepoints_pids_station_"+station+"_cut", "tkd_sp_"+station, "pid", "x", "y", pid_colors, True)
            # number of planes used -- "n_channels" -- should actually be called number of clusters (we think?)
            self.birth_var_two_d_scatter("tku_spacepoints_clusters_station_"+station+"_all", "tku_sp_"+station, "n_channels", "x", "y", cluster_colors)
            self.birth_var_two_d_scatter("tkd_spacepoints_clusters_station_"+station+"_all", "tkd_sp_"+station, "n_channels", "x", "y", cluster_colors)
            self.birth_var_two_d_scatter("tku_spacepoints_clusters_station_"+station+"_cut", "tku_sp_"+station, "n_channels", "x", "y", cluster_colors, True)
            self.birth_var_two_d_scatter("tkd_spacepoints_clusters_station_"+station+"_cut", "tkd_sp_"+station, "n_channels", "x", "y", cluster_colors, True)

            #self.birth_var_two_d_residual("pt_vs_pz_residual_at_"+detector, detector, "pid", "pt", "pz", pid_colors, True) # TomL
        #disabled due to file size
        #self.birth_var_two_d_scatter("x_vs_z_of_mc_track_final", "mc_track_final", "pid", "z", "x", pid_colors)
        #self.birth_var_two_d_scatter("y_vs_z_of_mc_track_final", "mc_track_final", "pid", "z", "y", pid_colors)
        #self.birth_var_two_d_scatter("r_vs_z_of_mc_track_final", "mc_track_final", "pid", "z", "r", pid_colors)
        self.birth_var_two_d_scatter("x_vs_px_of_primary", "mc_primary", "pid", "x", "px", pid_colors)
        self.birth_var_two_d_scatter("y_vs_py_of_primary", "mc_primary", "pid", "y", "py", pid_colors)
        self.birth_var_one_d("p_at_mc_tof_0", "mc_tof_0", "pid", "p", pid_colors)
        self.birth_var_one_d("p_at_mc_tof_1", "mc_tof_1", "pid", "p", pid_colors)
        self.birth_var_one_d("e_dep_at_mc_tof_0", "mc_tof_0", "pid", "e_dep", pid_colors)
        self.birth_var_one_d("e_dep_at_mc_tof_0", "mc_tof_1", "pid", "e_dep", pid_colors)
        self.birth_var_one_d("p_at_mc_primary", "mc_primary", "pid", "p", pid_colors)
        self.birth_var_one_d("x_at_mc_primary", "mc_primary", "pid", "x", pid_colors)
        self.birth_var_one_d("y_at_mc_primary", "mc_primary", "pid", "y", pid_colors)
        self.birth_var_one_d("p_at_mc_track_final", "mc_track_final", "pid", "p", pid_colors)
        self.birth_var_one_d("x_at_mc_track_final", "mc_track_final", "pid", "x", pid_colors)
        self.birth_var_one_d("y_at_mc_track_final", "mc_track_final", "pid", "y", pid_colors)

        self.birth_var_one_d("tku_ke_in_st_1_plane_0", "mc_tk_111", "pid", "kinetic_energy", pid_colors, xmin = 0., xmax = 10.)
        self.birth_var_one_d("tku_e_dep_in_st_1_plane_0", "mc_tk_111", "pid", "e_dep", pid_colors, xmin = 0., xmax = 0.5)
        my_options = {
          "sub_dir":"accumulated_e_dep",
          "logy":True,
        }

        for tracker in range(1, 3):
            for station in range(1, 6):
                for plane in range(1, 4):
                    det_str = "mc_tk_"+str(100*tracker + 10*station + plane)
                    #self.birth_var_one_d("tku_accumulated_e_dep_in_"+det_str, det_str, "pid", "accumulated_e_dep", pid_colors, cuts = "us cut", xmin = 0., xmax = 1.0)

        tku_hit_predicate = lambda hit: 13900 < hit["hit"]["z"] and hit["hit"]["z"] < 15100
        self.birth_var_one_d("tku_p_at_mc_track_initial", "mc_track_initial", "pid", "p", pid_colors, xmin = 0., xmax = 10., hit_predicate = tku_hit_predicate)
        self.birth_var_one_d("tku_z_at_mc_track_initial", "mc_track_initial", "pid", "z", pid_colors, hit_predicate = tku_hit_predicate)

        tkd_hit_predicate = lambda hit: 18800 < hit["hit"]["z"] and hit["hit"]["z"] < 20000
        self.birth_var_one_d("tkd_p_at_mc_track_initial", "mc_track_initial", "pid", "p", pid_colors, xmin = 0., xmax = 10., hit_predicate = tkd_hit_predicate)
        self.birth_var_one_d("tkd_z_at_mc_track_initial", "mc_track_initial", "pid", "z", pid_colors, hit_predicate = tkd_hit_predicate)
        #disabled due to file size
        #self.birth_var_two_d_scatter("z_vs_p_of_track_initial", "mc_track_initial", "pid", "z", "p", pid_colors)
        self.birth_data_detector_residuals()
        #self.birth_pid_comparison(pid_colors)
        # Turned off for speed / size.. Plots should maybe be produced as TStacks instead
        #self.birth_compare_bad_tracks()
        #self.birth_spacepoints()
        self.birth_spacepoints(cluster_colors)

    def process(self):
        for name in sorted(self.process_args.keys()):
            process_function = self.process_args[name][0]
            process_args = self.process_args[name][1]
            process_function(name, *process_args)
        self.process_data_detector_residuals()
        #self.process_pid_comparison()
        #self.process_compare_bad_tracks()
        self.process_spacepoints()

    def death(self):
        self.death_data_detector_residuals()
        #self.death_pid_comparison()
        self.death_hist_residuals()
        print "Failed to put the following pids into scatter plots {pid:number}:"
        print "   ", self.failed_pids
        self.print_plots()

    def get_accumulated_e_dep(self, event, detector, hit_predicate, track_final):
        """
        Return a list of accumulated energy deposited
        
        Makes one entry per detector per pid per event
        """
        e_dep_dict = {} # pertains to this event/detector
        for detector_hit in event["data"]:
            if detector_hit["detector"] != detector:
                continue
            if hit_predicate != None and not hit_predicate(detector_hit):
                continue
            hit = detector_hit["hit"]
            pid = hit["pid"]
            if pid not in e_dep_dict:
                e_dep_dict[pid] = hit["e_dep"]
            else:
                e_dep_dict[pid] += hit["e_dep"]
        # now accumulate over the e_dep_dict
        for pid, e_dep in e_dep_dict.iteritems():
            if pid not in track_final:
                track_final[pid] = [e_dep]
            else:
                track_final[pid].append(e_dep)

 
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
                    plot_var = detector_hit["hit"][plot_variable]
                    if slice_var not in track_final:
                        track_final[slice_var] = []
                    track_final[slice_var].append(plot_var)
                    break
        all_list = []
        for value in track_final.values():
            all_list += value
        return (all_list, track_final)

    def process_var_one_d(self, name, detector, slice_variable, plot_variable, color_dict, cuts, hit_predicate):
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
            #print "DEBUG"
            #print plot_name
            if plot_name not in hist_dict:
                if key not in self.failed_pids:
                    self.failed_pids[key] = 0
                self.failed_pids[key] += 1
                continue
            for item in track_final[key]:
                hist_dict[plot_name].Fill(item)

    def birth_var_one_d(self, canvas_name, detector, slice_variable, plot_variable, color_dict, cuts = "all", xmin = None, xmax = None, hit_predicate = None, options = {}):
        all_list, track_final = self.get_data_var_one_d(detector, slice_variable, plot_variable, cuts, hit_predicate)
        hist = self.make_root_histogram(canvas_name, "all", all_list, plot_variable+" at "+detector, 100, [], '', 0, [], xmin, xmax)
        #print "hist1 : " # TomL -- hists are produced by parsing args to generic histmaker; empty variable lists will break this and produce TH2s instead of TH1s
        #print hist # TomL
        hist.SetMarkerStyle(26)
        hist.Draw("P")
        hist.SetStats(True)
        for i, key in enumerate(sorted(track_final.keys())):
            var_list = track_final[key]
            name = slice_variable+" = "+str(key)
            label = plot_variable+" at "+detector+" ["+utilities.utilities.default_units(plot_variable)+"]"
            hist = self.make_root_histogram(canvas_name, name, var_list, label, 100, [], '', 0, [], xmin, xmax)
            #print "hist2 : " # TomL
            #print hist # TomL
            hist.SetMarkerStyle(24)
            if key in color_dict:
                hist.SetMarkerColor(color_dict[key])
            hist.Draw("SAMEP")
        self.plots[canvas_name]["canvas"].SetLogy()
        #self.plots[canvas_name]["canvas"].BuildLegend()
        self.process_args[canvas_name] = [self.process_var_one_d, (detector, slice_variable, plot_variable, color_dict, cuts, hit_predicate)]
        for key in options.keys():
            if key not in self.get_plot(canvas_name)["config"]:
                raise KeyError("Did not recignise plot option "+str(key))
            self.get_plot(canvas_name)["config"][key] = options[key]

    def get_data_var_two_d_hist(self, name, *args):
        track_final = ([], [])
        for event in self.data_loader.events:
            #if args[3] and event["downstream_cut"]:
            if args[3] and event[args[3]]:
                continue
            for detector_hit in event["data"]:
                if detector_hit["detector"] != args[0]:
                    continue
                x = detector_hit["hit"][args[1]]
                y = detector_hit["hit"][args[2]]
                track_final[0].append(x)
                track_final[1].append(y)
        return track_final

    def process_var_two_d_hist(self, name, *args):
        track_final = self.get_data_var_two_d_hist(name, *args)
        hist_dict = self.plots[name]["histograms"]
        plot_name = name 
        if plot_name not in hist_dict:
            print "You're not filling hist " + plot_name + " into self.plots!"
            sys.exit()
        hist = hist_dict[plot_name]
        #print "Testing var_two_d_hist"
        for x, y in izip(*track_final):
                #print "One data example"
                #print "x: " + str(x)
                #print "y: " + str(y)
                hist.Fill(x, y)


    def birth_var_two_d_hist(self, canvas_name, detector, plot_variable_1, plot_variable_2, cuts=False, xmin = None, xmax = None, ymin = None, ymax = None):
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
        name = canvas_name
        label_1 = plot_variable_1+" ["+utilities.utilities.default_units(plot_variable_1)+"]"
        label_2 = plot_variable_2+" ["+utilities.utilities.default_units(plot_variable_2)+"]"
        # Does inclusion of x_list / y_list set this up as graph, not hist?
        hist = self.make_root_histogram(canvas_name, name,
          x_list, label_1, 100, y_list, label_2, 100, [],
          xmin, xmax, ymin, ymax)
        #hist = self.make_root_histogram(canvas_name, name,
        #  [-1000], label_1, 100, [-1000], label_2, 100, [],
        #  xmin, xmax, ymin, ymax)
        hist.Draw("COLZ")
        self.process_args[canvas_name] = [self.process_var_two_d_hist, (detector, plot_variable_1, plot_variable_2, cuts)]

    def get_data_var_three_d_hist_residual(self, name, *args):
        track_final = ([], [], [])
        for event in self.data_loader.events:
            #if args[9] and event["downstream_cut"]:
            if args[11] and event[args[11]]:
                continue
            vhit, thit = None, None
            for detector_hit in event["data"]:
                if detector_hit["detector"] == args[1]:
                    vhit = detector_hit["hit"]
                elif detector_hit["detector"] == args[0]:
                    thit = detector_hit["hit"]
                else:
                    continue
                if vhit != None and thit != None:
                    if args[5]: #TruthX
                        x = vhit[args[2]]
                    elif args[8]: # doresidualX
                        x = thit[args[2]] - vhit[args[2]]
                    else:
                        x = thit[args[2]]

                    if args[6]: #TruthY
                        y = vhit[args[3]]
                    elif args[9]: # doresidualY
                        y = thit[args[3]] - vhit[args[3]]
                    else:
                        y = thit[args[3]]

                    if args[7]: #TruthZ
                        z = vhit[args[4]]
                    elif args[10]: # doresidualZ
                        z = thit[args[4]] - vhit[args[4]]
                    else:
                        z = thit[args[4]]

                    track_final[0].append(x)
                    track_final[1].append(y)
                    track_final[2].append(z)
                    #print "appended"
                    break # next event please
        return track_final

    def process_var_three_d_hist_residual(self, name, *args):
        track_final = self.get_data_var_three_d_hist_residual(name, *args)
        hist_dict = self.plots[name]["histograms"]
        plot_name = name 
        if plot_name not in hist_dict:
            print "You're not filling hist " + plot_name + " into self.plots!"
            sys.exit()
        hist = hist_dict[plot_name]
        #print "One data example for hist_residual"
        for x, y, z in izip(*track_final):
                #print "x: " + str(x)
                #print "y: " + str(y)
                #print "z: " + str(z)
                hist.Fill(x, y, z)

    def birth_var_three_d_hist_residual(self, name, detector, virt_detector, plot_variable_1, plot_variable_2, plot_variable_3, TruthX=False, TruthY=False, TruthZ=False, doresidualX=False, doresidualY=False, doresidualZ=False, cuts=False):
        track_final = self.get_data_var_three_d_hist_residual(name, detector, virt_detector, plot_variable_1, plot_variable_2, plot_variable_3, TruthX, TruthY, TruthZ, doresidualX, doresidualY, doresidualZ, cuts)
        if len(track_final) == 0:
            print "No tracks for", detector
            return
        xmin, xmax, ymin, ymax = -50., 50., -50., 50.
        zmin, zmax = -20., 30. # New
        x_list = track_final[0]
        y_list = track_final[1]
        z_list = track_final[2] # New
        xmin = min([xmin]+x_list)
        xmax = max([xmax]+x_list)
        ymin = min([ymin]+y_list)
        ymax = max([ymax]+y_list)
        zmin = min([zmin]+z_list) # New
        zmax = max([zmax]+z_list) # New
        name = "three_d_hist_"+name
        canvas_name = name
        #canvas_name = "hist_residual_"+name

        if TruthX:
          label_1 = "True "+plot_variable_1+" ["+utilities.utilities.default_units(plot_variable_1)+"]"
        elif doresidualX:
          label_1 = plot_variable_1+" Residual ["+utilities.utilities.default_units(plot_variable_1)+"]"
        else:
          label_1 = plot_variable_1+" ["+utilities.utilities.default_units(plot_variable_1)+"]"
          
        if TruthY:
          label_2 = "True "+plot_variable_2+" ["+utilities.utilities.default_units(plot_variable_2)+"]"
        elif doresidualY:
          label_2 = plot_variable_2+" Residual ["+utilities.utilities.default_units(plot_variable_2)+"]"
        else:
          label_2 = plot_variable_2+" ["+utilities.utilities.default_units(plot_variable_2)+"]"

        if TruthZ:
          label_3 = "True "+plot_variable_3+" ["+utilities.utilities.default_units(plot_variable_3)+"]" # New
        elif doresidualZ:
          label_3 = plot_variable_3+" Residual ["+utilities.utilities.default_units(plot_variable_3)+"]" # New
        else:
          label_3 = plot_variable_3+" ["+utilities.utilities.default_units(plot_variable_3)+"]" # New

        #hist = self.make_root_histogram_3d(canvas_name, name,
        #  x_list, label_1, 100, y_list, label_2, 100, z_list, label_3, 100, [],
        #  xmin, xmax, ymin, ymax, zmin, zmax) # New
        hist = self.make_root_histogram_3d(canvas_name, name,
          x_list, label_1, 50, y_list, label_2, 50, z_list, label_3, 100, [],
          xmin, xmax, ymin, ymax, zmin, zmax) # New

        hist.Draw()
        projhist = self.project_root_histogram_3d(canvas_name, name, "yx")
        projhist.Draw("COLZ")
        self.process_args[canvas_name] = [self.process_var_three_d_hist_residual, (detector, virt_detector, plot_variable_1, plot_variable_2, plot_variable_3, TruthX, TruthY, TruthZ, doresidualX, doresidualY, doresidualZ, cuts)]

    def get_data_var_two_d_scatter(self, name, *args):
        track_final = {}
        for event in self.data_loader.events:
            #print "showing event info" # TomL
            #print event["data"] # TomL
            if args[5] and event["downstream_cut"]:
                continue
            for detector_hit in event["data"]:
                if detector_hit["detector"] != args[0]:
                    continue

                if args[1] in detector_hit: # maybe remove - slow?
                    pid = detector_hit[args[1]] # maybe remove - slow?
                else: # old format
                    pid = detector_hit["hit"][args[1]] # Maybe remove - slow?

                #if args[1] not in detector_hit["hit"]:
                #  #print "Detector_hit.keys():", detector_hit.keys() # THIS IS WHERE IT IS
                x = detector_hit["hit"][args[2]]
                y = detector_hit["hit"][args[3]]
                if pid not in track_final:
                    track_final[pid] = ([], [])
                track_final[pid][0].append(x)
                track_final[pid][1].append(y)
        return track_final

    def process_var_two_d_scatter(self, name, *args):
        track_final = self.get_data_var_two_d_scatter(name, *args)
        for pid in sorted(track_final.keys()):
            graph_dict = self.plots[name]["graphs"]
            plot_name = str(args[1])+" = "+str(pid)
            if plot_name not in graph_dict:
                if pid not in self.failed_pids:
                    self.failed_pids[pid] = 0
                self.failed_pids[pid] += 1
                continue
            graph = graph_dict[plot_name]
            n_points = len(track_final[pid][0])
            n_orig = graph.GetN()
            graph.Set(n_orig+n_points)
            for i in range(n_points):
                graph_dict[plot_name].SetPoint(i + n_orig, track_final[pid][0][i], track_final[pid][1][i])

    def birth_var_two_d_scatter(self, canvas_name, detector, slice_variable, plot_variable_1, plot_variable_2, color_dict, cuts=False):
        track_final = self.get_data_var_two_d_scatter(canvas_name, detector, slice_variable, plot_variable_1, plot_variable_2, color_dict, cuts)
        if len(track_final) == 0:
            print "No tracks for", detector
            return
        xmin, xmax, ymin, ymax = 0., 0., 0., 0.
        for x_list, y_list in track_final.values():
            xmin = min([xmin]+x_list)
            xmax = max([xmax]+x_list)
            ymin = min([ymin]+y_list)
            ymax = max([ymax]+y_list)

        for i, pid in enumerate(sorted(track_final.keys())):
            x_list = track_final[pid][0]
            y_list = track_final[pid][1]
            name = slice_variable+" = "+str(pid)
            label_1 = plot_variable_1+" ["+utilities.utilities.default_units(plot_variable_1)+"]"
            label_2 = plot_variable_2+" ["+utilities.utilities.default_units(plot_variable_2)+"]"
            hist, graph = self.make_root_graph(canvas_name, name,
              x_list, label_1, y_list, label_2, True,
              xmin, xmax, ymin, ymax)
            if i == 0:
                hist.Draw()
            if pid in color_dict:
                graph.SetMarkerColor(color_dict[pid])
            graph.SetMarkerStyle(6)
            graph.Draw("PSAME")
        self.process_args[canvas_name] = [self.process_var_two_d_scatter, (detector, slice_variable, plot_variable_1, plot_variable_2, color_dict, cuts)]

    def get_data_var_two_d_residual(self, name, *args):
        track_final = {}
        for event in self.data_loader.events:
            #print "showing event info" # TomL
            #print event # TomL
            if args[7] and event["downstream_cut"]:
                continue
            vhit, thit = None, None
            for detector_hit in event["data"]:
                #if detector_hit["detector"] != args[0]: # Detector
                #    continue
                #if detector_hit["detector"] != args[1]: # VirtualStation
                if detector_hit["detector"] == args[1]:
                    vhit = detector_hit["hit"]
                elif detector_hit["detector"] == args[0]:
                    thit = detector_hit["hit"]
                else:
                    continue

                #print "showing detector_hit[hit] info" # TomL
                #print detector_hit["hit"] # TomL
                #for key in detector_hit["hit"].keys(): # TomL
                #  print detector_hit["hit"][key] # TomL

                if vhit != None and thit != None:
                    pid = detector_hit["hit"][args[2]]
                    #x = detector_hit["hit"][args[2]]
                    #y = detector_hit["hit"][args[3]]
                    x = thit[args[3]] - vhit[args[3]]
                    if args[6]:
                        y = thit[args[4]] - vhit[args[4]]
                    else:
                        y = vhit[args[4]]
                    if pid not in track_final:
                        track_final[pid] = ([], [])
                    track_final[pid][0].append(x)
                    track_final[pid][1].append(y)
                    break
        return track_final

    def process_var_two_d_residual(self, name, *args): # Can maybe replace this with process_var_two_d_scatter as functions are the same (for now)
        track_final = self.get_data_var_two_d_residual(name, *args)
        for pid in sorted(track_final.keys()):
            graph_dict = self.plots[name]["graphs"]
            plot_name = str(args[1])+" = "+str(pid)
            if plot_name not in graph_dict:
                if pid not in self.failed_pids:
                    self.failed_pids[pid] = 0
                self.failed_pids[pid] += 1
                continue
            graph = graph_dict[plot_name]
            n_points = len(track_final[pid][0])
            n_orig = graph.GetN()
            graph.Set(n_orig+n_points)
            for i in range(n_points):
                graph_dict[plot_name].SetPoint(i + n_orig, track_final[pid][0][i], track_final[pid][1][i])

    def birth_var_two_d_residual(self, canvas_name, detector, virt_station, slice_variable, plot_variable_1, plot_variable_2, color_dict, residualy=False, cuts=False):
        track_final = self.get_data_var_two_d_residual(canvas_name, detector, virt_station, slice_variable, plot_variable_1, plot_variable_2, color_dict, residualy, cuts)
        if len(track_final) == 0:
            print "No tracks for", detector
            return
        xmin, xmax, ymin, ymax = 0., 0., 0., 0.
        for x_list, y_list in track_final.values():
            xmin = min([xmin]+x_list)
            xmax = max([xmax]+x_list)
            ymin = min([ymin]+y_list)
            ymax = max([ymax]+y_list)

        for i, pid in enumerate(sorted(track_final.keys())):
            x_list = track_final[pid][0]
            y_list = track_final[pid][1]
            name = slice_variable+" = "+str(pid)
            label_1 = plot_variable_1+" ["+utilities.utilities.default_units(plot_variable_1)+"]"
            label_2 = plot_variable_2+" ["+utilities.utilities.default_units(plot_variable_2)+"]"
            hist, graph = self.make_root_graph(canvas_name, name,
              x_list, label_1, y_list, label_2, True,
              xmin, xmax, ymin, ymax)
            if i == 0:
                hist.Draw()
            if pid in color_dict:
                graph.SetMarkerColor(color_dict[pid])
            graph.SetMarkerStyle(6)
            graph.Draw("PSAME")
        self.process_args[canvas_name] = [self.process_var_two_d_residual, (detector, virt_station, slice_variable, plot_variable_1, plot_variable_2, color_dict, residualy, cuts)]

    axis_labels = {"x":"x(meas) - x(true) [mm]", "y":"y(meas) - y(true) [mm]", "z":"z(meas) - z(true) [mm]", "t":"t(meas) - t(true) [ns]",
                   "px":"p_{x}(meas) - p_{x}(true) [MeV/c]", "py":"p_{y}(meas) - p_{y}(true) [MeV/c]", "pz":"p_{z}(meas) - p_{z}(true) [MeV/c]",
                   "pt":"p_{t}(meas) - p_{t}(true) [MeV/c]", "p":"p(meas) - p(true) [MeV/c]"}

    cmp_axis_labels = {"x":"x [mm]", "y":"y [mm]", "z":"z [mm]", "t":"t [ns]",
                   "px":"p_{x} [MeV/c]", "py":"p_{y} [MeV/c]", "pz":"p_{z} [MeV/c]",
                   "pt":"p_{t} [MeV/c]", "p":"p [MeV/c]"}

    def plot_detector_residuals(self, suffix):
        self.axis_min_max = {}
        for var in self.residual_dict.keys():
            if var == "amp_virt":
                continue  
            print "Plot detector residuals doing var", var
            data = self.residual_dict[var]
            canvas = xboa.common.make_root_canvas("MC residual "+var)
            canvas.Draw()
            xmin, xmax = utilities.utilities.fractional_axis_range(data, 0.95)
            hist = xboa.common.make_root_histogram(var, data, self.axis_labels[var], 100, xmin=xmin, xmax=xmax)
            hist.Draw()
            fit = utilities.utilities.fit_peak(hist, nsigma=8)
            mean = fit.GetParameter(1)
            sigma = fit.GetParameter(2)
            xmin, xmax = mean-5*sigma, mean+5*sigma
            self.axis_min_max[var] = (xmin, xmax)
            hist = xboa.common.make_root_histogram(var, data, self.axis_labels[var], 100, xmin=xmin, xmax=xmax)
            hist.Draw()
            fit = utilities.utilities.fit_peak(hist, nsigma=1)

            text_box = utilities.utilities.get_text_box(self.config, self.config_anal, data, fit)
            canvas.Update()
            for format in ["png", "eps", "root"]:
                canvas.Print(self.plot_dir+"/mc_residual_"+suffix+"_"+var+"."+format)

    def get_tofij_residual(self, det_name):
        if det_name == "tof01":
            virtuals = ["mc_virtual_tof0", "mc_virtual_tof1"]
            cut = "upstream_cut"
            offset_i = self.config.tof0_offset
            offset_j = self.config.tof1_offset
        elif det_name == "tof12":
            virtuals = ["mc_virtual_tof1", "mc_virtual_tof2"]
            cut = "downstream_cut"
            offset_i = self.config.tof1_offset
            offset_j = self.config.tof2_offset
        residuals, mc, det = [], [], []
        for event in self.data_loader.events:
            if event[cut]:
                continue
            reco_tof = event[det_name]
            if reco_tof == None:
                continue
            t_i, t_j = None, None
            for detector_hit in event["data"]:
                if detector_hit["detector"] == virtuals[0]:
                    t_i = detector_hit["hit"]["t"]
                elif detector_hit["detector"] == virtuals[1]:
                    t_j = detector_hit["hit"]["t"]
                else:
                    continue
                if t_i != None and t_j != None:
                    mc_tof = (t_j + offset_j) - (t_i + offset_i)
                    residuals.append(reco_tof - mc_tof)
                    mc.append(mc_tof)
                    det.append(reco_tof)
                    break
        return {"t":residuals}, {"t":mc}, {"t":det}

    def get_data_detector_residuals(self, det_name, virt_name):
        if det_name in ["tof01", "tof12"]:
            return self.get_tofij_residual(det_name)
        #if det_name in ["tku_tp", "tkd_tp"]:
        if "tku_" in det_name or "tkd_" in det_name:
            residual_dict = {"x":[], "y":[], "z":[], "px":[], "py":[], "pz":[], "pt":[], "p":[]} # TomL
            #residual_dict = {"x":[], "y":[], "z":[], "px":[], "py":[], "pz":[]}
        elif det_name in ["tof0", "tof1", "tof2"]:
            residual_dict = {"x":[], "y":[], "z":[]}
        elif "global" in det_name:
            #residual_dict = {"x":[], "y":[], "z":[], "px":[], "py":[], "pz":[], "pt":[]}
            residual_dict = {"x":[], "y":[], "z":[], "px":[], "py":[], "pz":[]}
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
            for detector_hit in event["data"]:
                if detector_hit["detector"] == virt_name:
                    vhit = detector_hit["hit"]
                elif detector_hit["detector"] == det_name:
                    thit = detector_hit["hit"]
                else:
                    continue
                if vhit != None and thit != None:
                    for key in residual_dict.keys():
                        residual_dict[key].append(thit[key] - vhit[key])
                        mc_dict[key].append(vhit[key])
                        det_dict[key].append(thit[key])
                    break # next event please
        return residual_dict, mc_dict, det_dict

    def efficiency_plot(self):
        efficiency = Efficiency(self.amp.reco_mc_data_ds,
                               self.amp.all_mc_data_ds,
                               self.plot_dir)
        efficiency.reco_cut_list
        efficiency.plot()


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
            "x":(-4., 4.),
            "y":(-4., 4.),
            "z":(-10., 10.),
            "px":(-10., 10.),
            "py":(-10., 10.),
            "pz":(-30., 30.),
            "pt":(-15., 15.),#"pt":(-100., 100.),
            "p":(-30., 30.),#"p":(-100., 100.),
            "t":(-1., 1.),
        }
        return keys[var]

    def get_x_min_max_compare(self, var):
        #utilities.utilities.fractional_axis_range(data, 0.95)
        keys = {
            "x":(-150., 150.),
            "y":(-150., 150.),
            "z":(-10., 10.),
            "px":(-100., 100.),
            "py":(-100., 100.),
            "pz":(100., 260.),
            "pt":(0., 100.),
            "p":(0., 260.),
            "t":(-10., 10.),
        }
        return keys[var]

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

    def get_data_detector_pids(self, det_name, virt_name):
        if det_name in ["tof01", "tof12"]:
            #return self.get_tofij_residual(det_name) # Change this to something useful?
            return {}, {},{} # Change this to something useful?
        if det_name in ["tku_tp", "tkd_tp"]:
            template_dict = {"x":[], "y":[], "z":[], "px":[], "py":[], "pz":[], "pt":[], "p":[]} # TomL
        elif det_name in ["tof0", "tof1", "tof2"]:
            template_dict = {"x":[], "y":[], "z":[]}
        elif "global" in det_name:
            template_dict = {"x":[], "y":[], "z":[], "px":[], "py":[], "pz":[]}
        mc_dict = {}
        det_dict = {}
        #mc_dict = copy.deepcopy(residual_dict)
        #det_dict = copy.deepcopy(residual_dict)
            
        if det_name in ["tku_tp", "tof0", "tof1"] or "global_through" in det_name:
            cut = "upstream_cut"
        else:
            cut = "downstream_cut"
        for event in self.data_loader.events:
            if event[cut]:
                continue
            vhit, thit = None, None
            for detector_hit in event["data"]:
                if detector_hit["detector"] == virt_name:
                    vhit = detector_hit["hit"]
                elif detector_hit["detector"] == det_name:
                    thit = detector_hit["hit"]
                else:
                    continue
                if vhit != None and thit != None:
                    pid = vhit["pid"]
                    if pid not in mc_dict:
                         mc_dict[pid] = copy.deepcopy(template_dict)
                         det_dict[pid] = copy.deepcopy(template_dict)
                    for key in mc_dict[pid].keys():
                         #residual_dict[key].append(thit[key] - vhit[key])
                         mc_dict[pid][key].append(vhit[key])
                         det_dict[pid][key].append(thit[key])
                    break # next event please
        #return residual_dict, mc_dict, det_dict
        return template_dict, mc_dict, det_dict

    def process_pid_comparison(self):
        for detector, virtual_station_list in self.mc_stations.iteritems():
            virtual_station = virtual_station_list[0]
            # old routine ends here
            if detector in ["tof01", "tof12"]:
                continue
            template_dict, mc_dict, det_dict = \
                     self.get_data_detector_pids(detector, virtual_station) # TomL
            for var in sorted(template_dict.keys()):
                canvas_name = "compare_pid_"+detector+"_"+var
                hist_dict = self.plots[canvas_name]["histograms"]
                for pid in sorted(mc_dict.keys()):
                    if "mc_"+str(pid) not in hist_dict:
                        if pid not in self.failed_pids:
                            self.failed_pids[pid] = 0
                        self.failed_pids[pid] += 1
                    else:
                        mc_data = mc_dict[pid][var]
                        hist = self.plots[canvas_name]["histograms"]["mc_"+str(pid)]
                        try: # TomL
                            for item in mc_data: # TomL
                                hist.Fill(item) # TomL
                        except TypeError: # TomL
                            print "Process pid comparison in mc_plotter failed to Fill with type error" # TomL
                            print canvas_name, detector, var, virtual_station # TomL
                            print item # TomL
                            sys.excepthook(*sys.exc_info()) # TomL
                    if "det_"+str(pid) not in hist_dict:
                        if pid not in self.failed_pids:
                            self.failed_pids[pid] = 0
                        self.failed_pids[pid] += 1
                        continue
                    else:
                        det_data = det_dict[pid][var]
                        hist = self.plots[canvas_name]["histograms"]["det_"+str(pid)]
                        for item in det_data:
                            hist.Fill(item)

    def birth_pid_comparison(self, color_dict):
        dummy_canvas = xboa.common.make_root_canvas("dummy")
        for detector, virtual_station_list in self.mc_stations.iteritems():
            virtual_station = virtual_station_list[0]
            # New bit - TomL
            template_dict, mc_dict, det_dict = \
                 self.get_data_detector_pids(detector, virtual_station) # TomL
            if detector in ["tof01", "tof12"]:
                continue
            for var in sorted(template_dict.keys()):
                for i, pid in enumerate(sorted(mc_dict.keys())):
                    #for var in sorted(mc_dict[pid].keys()):
                        #print "pid : "
                        #print pid
                        canvas_name = "compare_pid_"+detector+"_"+var
                        xmin, xmax = self.get_x_min_max_compare(var)
                        mc_data = mc_dict[pid][var]
                        hist = self.make_root_histogram(canvas_name, "mc_"+str(pid), mc_data, self.cmp_axis_labels[var], 100, [], '', 0, [], xmin, xmax)
                        #hist = self.plots[canvas_name]["histograms"]["mc_"+pid]
                        #hist.SetFillColor(ROOT.kOrange-2)
                        hist.SetMarkerStyle(24)
                        if pid in color_dict:
                            hist.SetMarkerColor(color_dict[pid])
                            hist.SetFillColor(color_dict[pid])
                        if i == 1:
                            hist.Draw()
                        else:
                            hist.Draw("SAME")

                        det_data = det_dict[pid][var]
                        hist = self.make_root_histogram(canvas_name, "det_"+str(pid), det_data, self.cmp_axis_labels[var], 100, [], '', 0, [], xmin, xmax)
                        hist.SetMarkerStyle(20)
                        hist.Draw("P E1 PLC SAME")
                        #dummy_canvas.cd() # make sure we don't accidentally overwrite "current" canvas
                dummy_canvas.cd() # make sure we don't accidentally overwrite "current" canvas

    def get_data_compare_bad_tracks(self, det_name, virt_name, this_cut):
        if det_name in ["tku_tp", "tkd_tp"]:
            residual_dict = {"x":[], "y":[], "z":[], "px":[], "py":[], "pz":[], "pt":[], "p":[]} # TomL
        #elif det_name in ["tku_sp", "tkd_sp"]:
        elif "tku_sp" in det_name or "tkd_sp" in det_name:
            residual_dict = {"x":[], "y":[], "z":[]} # TomL
        elif det_name in ["tof0", "tof1", "tof2"]:
            residual_dict = {"x":[], "y":[], "z":[]}
        elif "global" in det_name:
            residual_dict = {"x":[], "y":[], "z":[], "px":[], "py":[], "pz":[]}
        #mc_dict = {}
        #det_dict = {}
        mc_dict = copy.deepcopy(residual_dict)
        det_dict = copy.deepcopy(residual_dict)
        mc_only_dict = copy.deepcopy(residual_dict)
        det_only_dict = copy.deepcopy(residual_dict)
            
        if det_name in ["tku_tp", "tof0", "tof1"] or "global_through" in det_name:
            cut = "upstream_cut"
            mc_cut = "mc_true_us_cut"
        else:
            cut = "downstream_cut"
            mc_cut = "mc_true_ds_cut"
        for event in self.data_loader.events:
            #if event[mc_cut]: # skip events cut by mc_cuts
            if event["upstream_cut"]: # skip events cut by us_cuts
                continue
            if not event[cut]: # skip events not cut by us/ds cut
                continue
            if this_cut in event["will_cut"]: 
                will_cut = event["will_cut"][this_cut]
            elif this_cut in event:
                will_cut = event[this_cut]
            if not will_cut: # skip events not cut by this_cut
                continue
            #if not cut and not this_cut: # skip events not cut by this_cut (and us/ds cut)
            #    continue
            vhit, thit = None, None
            for detector_hit in event["data"]:
                if detector_hit["detector"] == virt_name:
                    vhit = detector_hit["hit"]
                elif detector_hit["detector"] == det_name:
                    thit = detector_hit["hit"]
                else:
                    continue
                if vhit != None and thit != None:
                    for key in residual_dict.keys():
                        residual_dict[key].append(thit[key] - vhit[key])
                        mc_dict[key].append(vhit[key])
                        det_dict[key].append(thit[key])
                    break # next event please
            if vhit != None and thit == None:
                for key in residual_dict.keys():
                    mc_only_dict[key].append(vhit[key])
            if vhit == None and thit != None:
                for key in residual_dict.keys():
                    det_only_dict[key].append(thit[key])
                
        return residual_dict, mc_dict, det_dict, mc_only_dict, det_only_dict
        #return template_dict, mc_dict, det_dict

    def process_compare_bad_tracks(self):
        mc_stations = copy.deepcopy(self.mc_stations)
        for key, value in self.sp_detector_dict.iteritems():
            mc_stations[key] = [value]

        #for detector, virtual_station_list in self.mc_stations.iteritems():
        for detector, virtual_station_list in mc_stations.iteritems():
            virtual_station = virtual_station_list[0]
            if detector in ["tof01", "tof12"]:
                continue
            if detector in ["tku_tp", "tof0", "tof1"] or "global_through" in detector:
                #cut_list = self.us_cut_list
                continue
            else:
                cut_list = self.ds_cut_list
            for cut in cut_list:
                residual_dict, mc_dict, det_dict, mc_only_dict, det_only_dict = \
                     self.get_data_compare_bad_tracks(detector, virtual_station, cut) # TomL
                for var in sorted(residual_dict.keys()):
                    #canvas_name = "compare_pid_"+detector+"_"+var
                    canvas_name = "failed_"+cut+"_"+detector+"_"+var+"_residual"
                    data = residual_dict[var]
                    hist = self.plots[canvas_name]["histograms"][var]
                    for item in data:
                        hist.Fill(item)

                    canvas_name = "failed_"+cut+"_"+detector+"_"+var+"_compare"
                    mc_data = mc_dict[var]
                    hist = self.plots[canvas_name]["histograms"]["mc_"+var]
                    try: # TomL
                        for item in mc_data: # TomL
                            hist.Fill(item) # TomL
                    except TypeError: # TomL
                        print "Process bad tracks comparison in mc_plotter failed to Fill with type error" # TomL
                        print canvas_name, detector, var, virtual_station # TomL
                        print item # TomL
                        sys.excepthook(*sys.exc_info()) # TomL
                    det_data = det_dict[var]
                    hist = self.plots[canvas_name]["histograms"]["det_"+var]
                    for item in det_data:
                        hist.Fill(item)
                        
                    #canvas_name = "failed_"+cut+"_"+detector+"_"+var+"_mc_only"
                    mc_only_data = mc_only_dict[var]
                    hist = self.plots[canvas_name]["histograms"]["mc_only_"+var]
                    for item in mc_only_data:
                        hist.Fill(item)

                    #canvas_name = "failed_"+cut+"_"+detector+"_"+var+"_det_only"
                    det_only_data = det_only_dict[var]
                    hist = self.plots[canvas_name]["histograms"]["det_only_"+var]
                    for item in det_only_data:
                        hist.Fill(item)

                dict_of_dicts = {
                                "mc":mc_dict,
                                "data":det_dict,
                                "mc_only":mc_only_dict,
                                "data_only":det_only_dict,
                                }

                for var1, var2 in (["x", "y"], ["px", "py"]):
                    for data_type in dict_of_dicts.keys():
                        if var1 not in dict_of_dicts[data_type].keys():
                            continue
                        data_x = dict_of_dicts[data_type][var1]
                        data_y = dict_of_dicts[data_type][var2]
                        canvas_name = "failed_"+cut+"_"+detector+"_"+var1+"_vs_"+var2+"_"+data_type
                        hist = self.plots[canvas_name]["histograms"][data_type]
                        for x, y in izip(data_x, data_y):
                            hist.Fill(x, y)

    def birth_compare_bad_tracks(self):
        dummy_canvas = xboa.common.make_root_canvas("dummy")
        us_cut_list = self.us_cut_list
        ds_cut_list = self.ds_cut_list

        mc_stations = copy.deepcopy(self.mc_stations)
        for key, value in self.sp_detector_dict.iteritems():
            mc_stations[key] = [value]

        #for detector, virtual_station_list in self.mc_stations.iteritems():
        for detector, virtual_station_list in mc_stations.iteritems():
            virtual_station = virtual_station_list[0]
            if detector in ["tof01", "tof12"]:
                continue
            #if detector not in ["tku_tp", "tkd_tp"]:
            #    continue
            print "Birth bad tracks", detector, virtual_station_list
            if detector in ["tku_tp", "tof0", "tof1"] or "global_through" in detector:
                #cut_list = us_cut_list
                print "Not doing bad tracks for US cuts"
                continue
            else:
                cut_list = ds_cut_list
            #for virtual_station in virtual_station_list:
            for cut in cut_list:
                    residual_dict, mc_dict, det_dict, mc_only_dict, det_only_dict = \
                             self.get_data_compare_bad_tracks(detector, virtual_station, cut) # TomL
                    for var in sorted(residual_dict.keys()):
                        self.check_empty(self.get_x_min_max, var, [residual_dict])
                        self.check_empty(self.get_x_min_max_compare, var, [mc_dict, det_dict, mc_only_dict, det_only_dict])
                        canvas_name = "failed_"+cut+"_"+detector+"_"+var+"_residual"
                        data = residual_dict[var]
                        xmin, xmax = self.get_x_min_max(var)
                        dummy_canvas.cd() # make sure we don't accidentally overwrite "current" canvas
                        hist = self.make_root_histogram(canvas_name, var, data, self.axis_labels[var], 100, [], '', 0, [], xmin, xmax)
                        hist.Draw()
    
                        # superimpose mc over recon mc
                        canvas_name = "failed_"+cut+"_"+detector+"_"+var+"_compare"
                        xmin, xmax = self.get_x_min_max_compare(var)
                        if len(data) == 0:
                            print "WARNING - Failed to find bad tracks residual data for "+var+" "+detector+" "+virtual_station
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
    
                        mc_only_data = mc_only_dict[var]
                        hist = self.make_root_histogram(canvas_name, "mc_only_"+var, mc_only_data, self.cmp_axis_labels[var], 100, [], '', 0, [], xmin, xmax)
                        hist.SetFillColorAlpha(ROOT.kRed, 0.35)
                        #hist.SetFillColor(ROOT.kRed)
                        #hist.SetFillStyle(4050)
                        hist.Draw("SAME")

                        det_only_data = det_only_dict[var]
                        hist = self.make_root_histogram(canvas_name, "det_only_"+var, det_only_data, self.cmp_axis_labels[var], 100, [], '', 0, [], xmin, xmax)
                        hist.SetMarkerStyle(21)
                        hist.SetMarkerColor(ROOT.kBlue)
                        hist.Draw("P SAME")
                        dummy_canvas.cd() # make sure we don't accidentally overwrite "current" canvas

                        #if cut == "all":
                        #self.check_empty(self.get_x_min_max_compare, var1, [mc_dict, det_dict, mc_only_dict, det_only_dict])
                        #self.check_empty(self.get_x_min_max_compare, var2, [mc_dict, det_dict, mc_only_dict, det_only_dict])

                    dict_of_dicts = {
                                    "mc":mc_dict,
                                    "data":det_dict,
                                    "mc_only":mc_only_dict,
                                    "data_only":det_only_dict,
                                    }

                    for var1, var2 in (["x", "y"], ["px", "py"]): 
                        for data_type in dict_of_dicts.keys():
                            if var1 not in dict_of_dicts[data_type].keys():
                                continue
                            data_x = dict_of_dicts[data_type][var1]
                            data_y = dict_of_dicts[data_type][var2]

                            canvas_name = "failed_"+cut+"_"+detector+"_"+var1+"_vs_"+var2+"_"+data_type
                            name = data_type
                            xmin, xmax = self.get_x_min_max_compare(var1)
                            ymin, ymax = self.get_x_min_max_compare(var2)
                            label_1 = var1+" ["+utilities.utilities.default_units(var1)+"]"
                            label_2 = var2+" ["+utilities.utilities.default_units(var2)+"]"
                            hist = self.make_root_histogram(canvas_name, name,
                                data_x, label_1, 100, data_y, label_2, 100, [],
                                xmin, xmax, ymin, ymax)
                            hist.Draw("COLZ")
                            dummy_canvas.cd() # make sure we don't accidentally overwrite "current" canvas

    def get_data_spacepoints(self, det_name, virt_name, this_cut):
        #if det_name in ["tku_sp", "tkd_sp"]:
        residual_dict = {"x":[], "y":[], "z":[]} # TomL
        mc_dict = copy.deepcopy(residual_dict)
        det_dict = copy.deepcopy(residual_dict)
        mc_only_dict = copy.deepcopy(residual_dict)
        det_only_dict = copy.deepcopy(residual_dict)
            
        """if "tku_sp" in det_name:
            cut = "upstream_cut"
            mc_cut = "mc_true_us_cut"
        else:
            cut = "downstream_cut"
            mc_cut = "mc_true_ds_cut" """
        for event in self.data_loader.events:
            if this_cut in event:
                if event[this_cut]:
                    continue
            #"upstream_cut"
            #if not event[cut] and not event[this_cut]:
            #    continue
            vhit, thit = None, None
            for detector_hit in event["data"]:
                if detector_hit["detector"] == virt_name:
                    vhit = detector_hit["hit"]
                elif detector_hit["detector"] == det_name:
                    thit = detector_hit["hit"]
                else:
                    continue
                if vhit != None and thit != None:
                    for key in residual_dict.keys():
                        residual_dict[key].append(thit[key] - vhit[key])
                        mc_dict[key].append(vhit[key])
                        det_dict[key].append(thit[key])
                    break # next event please
            if vhit != None and thit == None:
                for key in residual_dict.keys():
                    mc_only_dict[key].append(vhit[key])
            if vhit == None and thit != None:
                for key in residual_dict.keys():
                    det_only_dict[key].append(thit[key])
                
        return residual_dict, mc_dict, det_dict, mc_only_dict, det_only_dict

    def process_spacepoints(self):
        """sp_detector_dict ={} 
        sp_detector_dict["tku_sp_1"] = "mc_virtual_tku_tp"
        sp_detector_dict["tkd_sp_1"] = "mc_virtual_tkd_tp"
        for station in range(2,6):
            sp_detector_dict["tku_sp_"+str(station)] = "mc_virtual_tku_"+str(station)
            sp_detector_dict["tkd_sp_"+str(station)] = "mc_virtual_tkd_"+str(station)
        """
        sp_detector_dict = self.sp_detector_dict
        for detector, virtual_station in sp_detector_dict.iteritems():
            """if "tku_sp" in detector:
                cut_list = self.us_cut_list
            else:
                cut_list = self.ds_cut_list
            for cut in cut_list:"""
            for cut in ["all", "upstream_cut"]:
                residual_dict, mc_dict, det_dict, mc_only_dict, det_only_dict = \
                     self.get_data_spacepoints(detector, virtual_station, cut) # TomL
                for var in sorted(residual_dict.keys()):
                    canvas_name = "spacepoints_"+cut+"_"+detector+"_"+var+"_residual"
                    data = residual_dict[var]
                    hist = self.plots[canvas_name]["histograms"][var]
                    try: # TomL
                        for item in data:
                            hist.Fill(item)
                    except TypeError: # TomL
                        print "Process bad tracks residual in mc_plotter failed to Fill with type error" # TomL
                        print canvas_name, detector, var, virtual_station # TomL
                        print item # TomL
                        sys.excepthook(*sys.exc_info()) # TomL
                    canvas_name = "spacepoints_"+cut+"_"+detector+"_"+var+"_compare"
                    mc_data = mc_dict[var]
                    hist = self.plots[canvas_name]["histograms"]["mc_"+var]
                    try: # TomL
                        for item in mc_data: # TomL
                            hist.Fill(item) # TomL
                    except TypeError: # TomL
                        print "Process bad tracks comparison in mc_plotter failed to Fill with type error" # TomL
                        print canvas_name, detector, var, virtual_station # TomL
                        print item # TomL
                        sys.excepthook(*sys.exc_info()) # TomL
                    det_data = det_dict[var]
                    hist = self.plots[canvas_name]["histograms"]["det_"+var]
                    for item in det_data:
                        hist.Fill(item)
                        
                    mc_only_data = mc_only_dict[var]
                    hist = self.plots[canvas_name]["histograms"]["mc_only_"+var]
                    for item in mc_only_data:
                        hist.Fill(item)

                    det_only_data = det_only_dict[var]
                    hist = self.plots[canvas_name]["histograms"]["det_only_"+var]
                    for item in det_only_data:
                        hist.Fill(item)

                # Adding MC only "spacepoints" to spacepoint plots
                if cut == "all":
                    if "tku" in detector:
                        canvas_name = "tku_spacepoints_clusters_station_"+detector.split("_")[2]+"_all"
                    if "tkd" in detector:
                        canvas_name = "tkd_spacepoints_clusters_station_"+detector.split("_")[2]+"_all"
                    plot_name = "mc_only"
                    mc_only_x = mc_only_dict["x"]
                    mc_only_y = mc_only_dict["y"]
                    """ "print "Processing.. "
                    print detector
                    print "mc_only lens:"
                    print len(mc_only_x)
                    print len(mc_only_y)
                    if len(mc_only_x):
                        print "minX:", min(mc_only_x)
                        print "maxX:", max(mc_only_x)
                        print "minY:", min(mc_only_y)
                        print "maxY:", max(mc_only_y) """

                    for canvas_name in [canvas_name, canvas_name+"_separate"]:
                        graph_dict = self.plots[canvas_name]["graphs"]
                        graph = graph_dict[plot_name]
                        n_points = len(mc_only_x)
                        n_orig = graph.GetN()
                        graph.Set(n_orig+n_points)
                        for i in range(n_points):
                            graph_dict[plot_name].SetPoint(i + n_orig, mc_only_x[i], mc_only_y[i])

                    """graph_dict = self.plots[canvas_name]["graphs"]
                    graph = graph_dict[plot_name]
                    n_points = len(mc_only_x)
                    n_orig = graph.GetN()
                    #print "n_orig:", n_orig
                    graph.Set(n_orig+n_points)
                    for i in range(n_points):
                        graph_dict[plot_name].SetPoint(i + n_orig, mc_only_x[i], mc_only_y[i])"""

    def birth_spacepoints(self, colors_dict):
        dummy_canvas = xboa.common.make_root_canvas("dummy")
        us_cut_list = self.us_cut_list
        ds_cut_list = self.ds_cut_list
        sp_detector_dict = self.sp_detector_dict
        #sp_detector_dict ={} 
        #sp_detector_dict["tku_sp_1"] = "mc_virtual_tku_tp"
        #sp_detector_dict["tkd_sp_1"] = "mc_virtual_tkd_tp"
        #for station in range(2,6):
        #    sp_detector_dict["tku_sp_"+str(station)] = "mc_virtual_tku_"+str(station)
        #    sp_detector_dict["tkd_sp_"+str(station)] = "mc_virtual_tkd_"+str(station)
    
        for detector, virtual_station in sp_detector_dict.iteritems():
            """if "tku_sp" in detector:
                cut_list = self.us_cut_list
            else:
                cut_list = self.ds_cut_list
            for cut in cut_list:"""
            for cut in ["all", "upstream_cut"]:
                residual_dict, mc_dict, det_dict, mc_only_dict, det_only_dict = \
                     self.get_data_spacepoints(detector, virtual_station, cut) # TomL

                for var in sorted(residual_dict.keys()):
                    self.check_empty(self.get_x_min_max, var, [residual_dict])
                    self.check_empty(self.get_x_min_max_compare, var, [mc_dict, det_dict, mc_only_dict, det_only_dict])
                    canvas_name = "spacepoints_"+cut+"_"+detector+"_"+var+"_residual"
                    data = residual_dict[var]
                    xmin, xmax = self.get_x_min_max(var)
                    dummy_canvas.cd() # make sure we don't accidentally overwrite "current" canvas
                    hist = self.make_root_histogram(canvas_name, var, data, self.axis_labels[var], 100, [], '', 0, [], xmin, xmax)
                    hist.Draw()

                    # superimpose mc over recon mc
                    canvas_name = "spacepoints_"+cut+"_"+detector+"_"+var+"_compare"
                    xmin, xmax = self.get_x_min_max_compare(var)
                    if len(data) == 0:
                        print "WARNING - Failed to find spacepoints residual data for "+var+" "+detector+" "+virtual_station
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
                    #dummy_canvas.cd() # make sure we don't accidentally overwrite "current" canvas

                    #canvas_name = "spacepoints_"+cut+"_"+detector+"_"+var+"_mc_only"
                    #canvas_name = "spacepoints_"+cut+"_"+detector+"_"+var+"_compare"
                    mc_only_data = mc_only_dict[var]
                    hist = self.make_root_histogram(canvas_name, "mc_only_"+var, mc_only_data, self.cmp_axis_labels[var], 100, [], '', 0, [], xmin, xmax)
                    hist.SetFillColor(ROOT.kRed)
                    hist.Draw("SAME")
                    #hist.Draw()
                    #dummy_canvas.cd() # make sure we don't accidentally overwrite "current" canvas

                    #canvas_name = "spacepoints_"+cut+"_"+detector+"_"+var+"_det_only"
                    #canvas_name = "spacepoints_"+cut+"_"+detector+"_"+var+"_compare"
                    det_only_data = det_only_dict[var]
                    hist = self.make_root_histogram(canvas_name, "det_only_"+var, det_only_data, self.cmp_axis_labels[var], 100, [], '', 0, [], xmin, xmax)
                    hist.SetMarkerStyle(21)
                    hist.SetMarkerColor(ROOT.kRed)
                    hist.Draw("P SAME")
                    dummy_canvas.cd() # make sure we don't accidentally overwrite "current" canvas

                # Adding MC only "spacepoints" to spacepoint plots
                if cut == "all":
                    self.check_empty(self.get_x_min_max_compare, "x", [mc_only_dict])
                    self.check_empty(self.get_x_min_max_compare, "y", [mc_only_dict])
                    mc_only_x = mc_only_dict["x"]
                    mc_only_y = mc_only_dict["y"]
                    """print "mc_only lens:"
                    print len(mc_only_x)
                    print len(mc_only_y)
                    print "minX:", min(mc_only_x)
                    print "maxX:", max(mc_only_x)
                    print "minY:", min(mc_only_y)
                    print "maxY:", max(mc_only_y)"""

                    """ detector = "tku_sp_1" """
                    #canvas_name = "tku_spacepoints_clusters_station_"+station+"_all"
                    if "tku" in detector:
                        canvas_name = "tku_spacepoints_clusters_station_"+detector.split("_")[2]+"_all"
                    if "tkd" in detector:
                        canvas_name = "tkd_spacepoints_clusters_station_"+detector.split("_")[2]+"_all"

                    my_plot = self.get_plot(canvas_name)
                    my_plot["canvas"].cd()
                    my_plot["pad"].Draw()

                    #name = slice_variable+" = "+str(pid)
                    #name = "n_channels = 0"
                    name = "mc_only"
                    xmin, xmax = self.get_x_min_max_compare("x")
                    ymin, ymax = self.get_x_min_max_compare("y")
                    label_1 = "x ["+utilities.utilities.default_units("x")+"]"
                    label_2 = "y ["+utilities.utilities.default_units("y")+"]"
                    hist, graph = self.make_root_graph(canvas_name, name,
                        mc_only_x, label_1, mc_only_y, label_2, True,
                        xmin, xmax, ymin, ymax)
                    #hist.Draw()

                    graph.SetMarkerColor(ROOT.kBlack)
                    graph.SetMarkerStyle(6)
                    graph.Draw("PSAME")
                    dummy_canvas.cd() # make sure we don't accidentally overwrite "current" canvas

                    canvas_name += "_separate" 
                    hist, graph = self.make_root_graph(canvas_name, name,
                        mc_only_x, label_1, mc_only_y, label_2, True,
                        xmin, xmax, ymin, ymax)
                    hist.Draw()
                    graph.SetMarkerColor(ROOT.kBlack)
                    graph.SetMarkerStyle(6)
                    graph.Draw("PSAME")



                # 2D scatter plot showing xy/PxPy points for bad tracks depending on 
                # data dict found in
                #canvas_name = "spacepoints_"+cut+"_"+detector+"_xy_scatter"
                #xmin, xmax = self.get_x_min_max_compare("x")
                #ymin, ymax = self.get_x_min_max_compare("y")
                # Want to plot positions from det when also found in mc, 
                # positions of mc_only, and det_only points
                #scatter_dict = {
                #    "mc":mc_dict,
                #    "det":det_dict,
                #    "mc_only":mc_only_dict,
                #    "det_only":det_only_dict,
                #}
                #scatter_colours = {
                ##    "mc":ROOT.kBlack,
                #    "det":ROOT.kGreen,
                #    "mc_only":ROOT.kRed,
                #    "det_only":ROOT.kBlue,
                #}

                """
                # 2D scatter plot showing the number of planes in each spacepoint by colour
                # This should show bad channels clearly
                canvas_name = "spacepoints_"+cut+"_"+detector+"_xy_scatter"
                xmin, xmax = self.get_x_min_max_compare("x")
                ymin, ymax = self.get_x_min_max_compare("y")
                # Want to plot positions from det when also found in mc, 
                # positions of mc_only, and det_only points

                # USE "n_channels" as slice_variable?
                scatter_dict = {
                    "mc":mc_dict,
                    "det":det_dict,
                    "mc_only":mc_only_dict,
                    "det_only":det_only_dict,
                }
                scatter_colours = {
                    1:ROOT.kBlue,
                    2:ROOT.kRed,
                    3:ROOT.kGreen,
                }

                for i, name, data_dict in enumerate(scatter_dict.iteritems()):
                    list_x = data_dict["x"]
                    list_y = data_dict["y"]
                    hist, graph = self.make_root_graph(canvas_name, name, list_x, self.cmp_axis_labels["x"], 
                      list_y, self.cmp_axis_labels["y"], True, xmin, xmax, ymin, ymax)

                    if i == 0:
                        hist.Draw()
                    if cat in scatter_colours:
                        graph.SetMarkerColor(scatter_colours[cat])
                    graph.SetMarkerStyle(6)
                    graph.Draw("PSAME")"""


    def death_data_detector_residuals(self):
        for name in self.plots:
            if "mc_residual_" not in name:
                continue
            #print name
            self.plots[name]["canvas"].cd()
            for hist_name in self.plots[name]["histograms"]:
                hist = self.plots[name]["histograms"][hist_name]
                fit = utilities.utilities.fit_peak(hist, nsigma=1)
                text_box = utilities.utilities.get_text_box(self.config, self.config_anal, None, fit, hist)

    #def death_compare_bad_tracks(self):
    #    for name in self.plots:
    #      if "failed_" not in name:
    #          continue
    #      self.plots[name]["canvas"].cd()
    #      # Rescale y-axis here to fit all plots if necessary
          
    def death_pid_comparison(self):
        for name in self.plots.keys():
            if "compare_pid" not in name:
                continue
            new_canvas = name.replace("compare_pid", "pid_comparison")
            my_plot = self.get_plot(new_canvas)
            stack = ROOT.THStack(new_canvas, new_canvas)
            for hist_name in self.plots[name]["histograms"]:
                stack.Add(self.plots[name]["histograms"][hist_name])
            stack.Draw("nostack")
            my_plot["histograms"][new_canvas] = stack
            #self.plots[name]["canvas"].cd()


    def death_hist_residuals(self):
        for name in self.plots:
            if "three_d_hist_" not in name:
                continue
            elif "_profile_" in name:
                #print "skipped profiling a _profile_ hist"
                continue
            #print name
            #self.plots[name]["canvas"].cd() # Changed
            for hist_name in self.plots[name]["histograms"]:
                #hist = self.plots[name]["histograms"][hist_name]
                projhist = self.project_root_histogram_3d(name, hist_name, "yx")
                #print name
                #print "NbinsX:", projhist.GetNbinsX()
                #print "NbinsY:", projhist.GetNbinsY()
                # projhist.Draw() # Include??

    def check_empty(self, function, var, dict_list):
        xmin, xmax = function(var)
        for a_dict in dict_list:
            data = a_dict[var]  
            if len(data) == 0:
                #print "found empty data dict"
                #print data
                #print "Filling.."
                #data = [xmax+(xmax-xmin)*100.]
                data.append(xmax+(xmax-xmin)*100.)
                #print data

    """def get_data_var_two_d_hist_residual(self, name, *args):
        track_final = ([], [], [])
        for event in self.data_loader.events:
            #if args[9] and event["downstream_cut"]:
            if args[9] and event[args[9]]:
                continue
            do_res = {
                False:0,
                True:None
            }
            xthit, ythit, zthit = None, None, None
            xvhit, yvhit, zvhit = (do_res[bool(args[6])], 
                                   do_res[bool(args[7])], 
                                   do_res[bool(args[8])]) # Sets vhits to 0 if no res required
            #print "xvhit : " + str(xvhit)
            #print "yvhit : " + str(yvhit)
            #print "zvhit : " + str(zvhit)
            # could set all to 0, 0 to start? # if thit = none, but vhit found, set to 0? 
            # really inefficiencies handle case where thit = none, but vhit = found so ignore these?
            for detector_hit in event["data"]:
                if detector_hit["detector"] == args[0]:
                    xthit = detector_hit["hit"]
                elif detector_hit["detector"] == args[1]:
                    ythit = detector_hit["hit"]
                elif detector_hit["detector"] == args[2]:
                    zthit = detector_hit["hit"]
                elif args[6] and detector_hit["detector"] == args[6]:
                    xvhit = detector_hit["hit"]
                elif args[7] and detector_hit["detector"] == args[7]:
                    yvhit = detector_hit["hit"]
                elif args[8] and detector_hit["detector"] == args[8]:
                    zvhit = detector_hit["hit"]
                else:
                    continue

            print "values so far.. : "
            print str(xthit)+","+str(ythit)+","+str(zthit)
            print str(xvhit)+","+str(yvhit)+","+str(zvhit)
            #if all([xthit, ythit, zthit, xvhit, yvhit, zvhit]): # Checks all vals are assigned
            if xthit != None and ythit != None and zthit != None and xvhit != None and yvhit != None and zvhit != None: # Checks all vals are assigned
                    x = xthit - xvhit
                    # change all this to single / double detector check, then assign x = xthit[args[3]] etc..
                    y = ythit - yvhit
                    z = zthit - zvhit
                    track_final[0].append(x)
                    track_final[1].append(y)
                    track_final[2].append(z)
                    print "appended"
        return track_final

    def process_var_two_d_hist_residual(self, name, *args):
        track_final = self.get_data_var_two_d_hist_residual(name, *args)
        hist_dict = self.plots[name]["histograms"]
        plot_name = name 
        if plot_name not in hist_dict:
            print "You're not filling hist " + plot_name + " into self.plots!"
            sys.exit()
        hist = hist_dict[plot_name]
        for data in track_final:
                hist.Fill(data[0], data[1], data[2])

    def birth_var_two_d_hist_residual(self, canvas_name, detector1, detector2, detector3, plot_variable_1, plot_variable_2, plot_variable_3, doresidualX=False, doresidualY=False, doresidualZ=False, cuts=False):
        track_final = self.get_data_var_two_d_hist_residual(canvas_name, detector1, detector2, detector3, plot_variable_1, plot_variable_2, plot_variable_3, doresidualX, doresidualY, doresidualZ, cuts)
        if len(track_final) == 0:
            print "No tracks for", detector
            return
        xmin, xmax, ymin, ymax = 0., 0., 0., 0.
        x_list = track_final[0]
        y_list = track_final[1]
        xmin = min([xmin]+x_list)
        xmax = max([xmax]+x_list)
        ymin = min([ymin]+y_list)
        ymax = max([ymax]+y_list)
        name = canvas_name
        label_1 = plot_variable_1+" ["+utilities.utilities.default_units(plot_variable_1)+"]"
        label_2 = plot_variable_2+" ["+utilities.utilities.default_units(plot_variable_2)+"]"
        # Does inclusion of x_list / y_list set this up as graph, not hist?
        hist = self.make_root_histogram(canvas_name, name,
          x_list, label_1, 100, y_list, label_2, 100, [],
          xmin, xmax, ymin, ymax)
        #hist = self.make_root_histogram(canvas_name, name,
        #  [-1000], label_1, 100, [-1000], label_2, 100, [],
        #  xmin, xmax, ymin, ymax)
        hist.Draw("COLZ")
        self.process_args[canvas_name] = [self.process_var_two_d_hist_residual, (detector1, detector2, detector3, plot_variable_1, plot_variable_2, plot_variable_3, doresidualX, doresidualY, doresidualZ, cuts)]"""

    @staticmethod
    def do_mc_plots(config, config_anal, data_loader):
        plotter = MCPlotter(config, config_anal, data_loader)
        pid_colors = {211:2, -13:4, -11:8, +11:ROOT.kGray}
        for detector in ["tkd", "tku"]:
            plotter.plot_amplitude_residuals(detector)



