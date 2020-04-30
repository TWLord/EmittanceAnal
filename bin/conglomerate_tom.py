import copy
import sys
import shutil
import json

import ROOT
import numpy

import utilities.utilities as utilities
import utilities.root_style as root_style
import conglomerate
from conglomerate.compare_config import CompareConfig
from conglomerate.conglomerate_merge import ConglomerateMerge
from conglomerate.conglomerate_one import ConglomerateOne
from conglomerate.conglomerate_one import ConglomerateContainer 
#from conglomerate.merge_cuts_summary_tex import MergeCutsSummaryTex

class CompareEfficiency(CompareConfig):
    def __init__(self, source_dir, target_dir, top_labels, right_labels):
        dir_list = [
            source_dir,
            #source_dir,
        ]
        #self.setup(source_dir, target_dir, "cut_plots/", "compare_plot/", dir_list)
        self.setup(source_dir, target_dir, "efficiency_plots/", "rescaled_2d_plots/", dir_list)
        #self.src_plot_dir = source_dir 
        #self.target_plot_dir = target_dir
        mod = {
            "merge_options":{
                "right_labels":right_labels,
                "top_labels":top_labels,
            },
            "redraw":{
                "z_range":[0,25],
            }
        }

        self.conglomerate_list = [
           #self.get_conglomerate_2("tku_p_9_0", None, "Whatever x axis", None, True, [0.5, 0.5, 0.9, 0.9], mod),
           self.get_conglomerate_3("efficiency_ratio_us_px_vs_py_tof_1_sp", "efficiency_ratio_us_px_vs_py_tof_1_sp", "tku px [MeV/c]", "tku py [MeV/c]", mod),
           self.get_conglomerate_3("efficiency_ratio_us_px_vs_py_upstream_aperture_cut", "efficiency_ratio_us_px_vs_py_upstream_aperture_cut", "tku px [MeV/c]", "tku py [MeV/c]", mod),
           self.get_conglomerate_3("efficiency_ratio_us_px_vs_py_p_tot_us", "efficiency_ratio_us_px_vs_py_p_tot_us", "tku px [MeV/c]", "tku py [MeV/c]", mod),
           self.get_conglomerate_3("efficiency_ratio_ds_px_vs_py_downstream_cut", "efficiency_ratio_ds_px_vs_py_downstream_cut", "tku px [MeV/c]", "tku py [MeV/c]", mod),
           self.get_conglomerate_3("efficiency_ratio_ds_px_vs_py_scifi_tracks_ds", "efficiency_ratio_ds_px_vs_py_scifi_tracks_ds", "tku px [MeV/c]", "tku py [MeV/c]", mod),
           self.get_conglomerate_3("efficiency_ratio_ds_px_vs_py_chi2_ds", "efficiency_ratio_ds_px_vs_py_chi2_ds", "tku px [MeV/c]", "tku py [MeV/c]", mod),
           self.get_conglomerate_3("efficiency_ratio_us_px_vs_py_tof_1_sp", "efficiency_ratio_us_px_vs_py_tof_1_sp", "tku px [MeV/c]", "tku py [MeV/c]", mod),
           self.get_conglomerate_3("efficiency_ratio_us_px_vs_py_tof01",  "efficiency_ratio_us_px_vs_py_tof01", "tku px [MeV/c]", "tku py [MeV/c]", mod),
           self.get_conglomerate_3("efficiency_ratio_us_px_vs_py_global_through_us_apertures", "efficiency_ratio_us_px_vs_py_global_through_us_apertures" , "tku px [MeV/c]", "tku py [MeV/c]", mod),
           self.get_conglomerate_3("efficiency_ratio_us_px_vs_py_chi2_us", "efficiency_ratio_us_px_vs_py_chi2_us", "tku px [MeV/c]", "tku py [MeV/c]", mod),
           self.get_conglomerate_3("efficiency_ratio_ds_px_vs_py_scifi_fiducial_ds", "efficiency_ratio_ds_px_vs_py_scifi_fiducial_ds", "tku px [MeV/c]", "tku py [MeV/c]", mod),
           self.get_conglomerate_3("efficiency_ratio_us_px_vs_py_tof_0_sp", "efficiency_ratio_us_px_vs_py_tof_0_sp", "tku px [MeV/c]", "tku py [MeV/c]", mod),
           self.get_conglomerate_3("efficiency_ratio_us_px_vs_py_scifi_fiducial_us", "efficiency_ratio_us_px_vs_py_scifi_fiducial_us", "tku px [MeV/c]", "tku py [MeV/c]", mod),
           self.get_conglomerate_3("efficiency_ratio_ds_px_vs_py_upstream_cut", "efficiency_ratio_ds_px_vs_py_upstream_cut", "tku px [MeV/c]", "tku py [MeV/c]", mod),
           self.get_conglomerate_3("efficiency_ratio_us_px_vs_py_scifi_tracks_us", "efficiency_ratio_us_px_vs_py_scifi_tracks_us", "tku px [MeV/c]", "tku py [MeV/c]", mod),
           self.get_conglomerate_3("efficiency_ratio_us_px_vs_py_tof01_tramlines", "efficiency_ratio_us_px_vs_py_tof01_tramlines", "tku px [MeV/c]", "tku py [MeV/c]", mod),
           self.get_conglomerate_3("efficiency_ratio_us_px_vs_py_upstream_cut", "efficiency_ratio_us_px_vs_py_upstream_cut", "tku px [MeV/c]", "tku py [MeV/c]", mod),
        ]

class CompareData2D(CompareConfig):
    def __init__(self, source_dir, target_dir, top_labels, right_labels):
        dir_list = [
            source_dir,
            #source_dir,
        ]
        #self.setup(source_dir, target_dir, "cut_plots/", "compare_plot/", dir_list)
        self.setup(source_dir, target_dir, "data_plots/", "rescaled_2d_plots/", dir_list)
        #self.src_plot_dir = source_dir 
        #self.target_plot_dir = target_dir
        mod = {
            "merge_options":{
                "right_labels":right_labels,
                "top_labels":top_labels,
            },
            "redraw":{
                "z_range":[0,100.0],
            }
        }

        self.conglomerate_list = [
           #self.get_conglomerate_2("tku_p_9_0", None, "Whatever x axis", None, True, [0.5, 0.5, 0.9, 0.9], mod),
           self.get_conglomerate_3("tku_px_tku_py_us_cut", "tku_px_tku_py_us_cut", "tku px [MeV/c]", "tku py [MeV/c]", mod),
           self.get_conglomerate_3("tkd_px_tkd_py_ds_cut", "tkd_px_tkd_py_ds_cut", "tkd px [MeV/c]", "tkd py [MeV/c]", mod),
        ]

class CompareMC2D(CompareConfig):
    def __init__(self, source_dir, target_dir, top_labels, right_labels):
        dir_list = [
            source_dir,
            #source_dir,
        ]
        #self.setup(source_dir, target_dir, "cut_plots/", "compare_plot/", dir_list)
        self.setup(source_dir, target_dir, "mc_plots/", "rebinned_2d_plots/", dir_list)
        #self.src_plot_dir = source_dir 
        #self.target_plot_dir = target_dir
        mod = {
            "merge_options":{
                "right_labels":right_labels,
                "top_labels":top_labels,
            },
            "rebin":2,
        }

        self.conglomerate_list = [
           self.get_conglomerate_3("three_d_hist_px_truth_vs_py_truth_vs_pt_residual_at_tku_tp_us_cut_profile_yx", "three_d_hist_px_truth_vs_py_truth_vs_pt_residual_at_tku_tp_us_cut_profile_yx", "tku px [MeV/c]", "tku py [MeV/c]", mod),
           self.get_conglomerate_3("three_d_hist_px_truth_vs_py_truth_vs_pt_residual_at_tkd_tp_us_cut_profile_yx", "three_d_hist_px_truth_vs_py_truth_vs_pt_residual_at_tkd_tp_us_cut_profile_yx", "tkd px [MeV/c]", "tkd py [MeV/c]", mod),
        ]




def testing_one(batch_level = 0): 

    """
    Main program; 
    - batch_level tells how much output for ROOT: batch_level 0 is silent, 10 is most verbose
    """
    fd_1 = {}
    root_style.setup_gstyle()
    ROOT.gROOT.SetBatch(True)

    #target_dir = "~/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/output/combinedMC+Data/officialMC/2017-02-6-c3-OfficialMC_v3+c6-reco-sys+corr_full/plots_2017-02-6_3-240_ABS-LH2/cut_plots/tku_p_9_0.root"
    #target_dir = "output/combinedMC+Data/officialMC/2017-02-6-c3-OfficialMC_v3+c6-reco-sys+corr_full/plots_2017-02-6_3-240_ABS-LH2/cut_plots/tku_p_9_0.root"
    ####source_dirs = ["/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/output/combinedMC+Data/officialMC/2017-02-6-c3-OfficialMC_v3+c6-reco-sys+corr_full/plots_Simulated_2017-02-6_3-240_ABS-LH2/",]
    # thisone ##########source_dirs = ["output/officialMC/2017-02-6-v3-OfficialMC_full/plots_9909_2017-02-6_3-240_ABS-LH2/", ]
    #source_dir = "output/combinedMC+Data/officialMC/2017-02-6-c3-OfficialMC_v3+c6-reco-sys+corr_full/plots_Simulated_2017-02-6_3-240_ABS-LH2/efficiency_plots/"
    #target_file = "~/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/output/combinedMC+Data/officialMC/2017-02-6-c3-OfficialMC_v3+c6-reco-sys+corr_full/plots_2017-02-6_3-240_ABS-LH2/cut_plots/tku_p_9_0.root"
    #target_file = "~/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/output/combinedMC+Data/officialMC/2017-02-6-c3-OfficialMC_v3+c6-reco-sys+corr_full/plots_2017-02-6_3-240_ABS-LH2/cut_plots/tku_p_9_0.root"
    #target_dir = "/home/phumhf/MICE/newdir/"
    #######target_dir = "output/testingCong2/"


    #source_dir = "LowPtholeplots/Data/plots_9907_9908_9909_9912_9913_9914_2017-02-6_3-240_ABS-LH2/"
    #source_dirs = [ "LowPtholeplots/Data/plots_9907_9908_9909_9912_9913_9914_2017-02-6_3-240_ABS-LH2/", "LowPtholeplots/Data/plots_ReconstructedRaw_9907_9908_9909_9912_9913_9914_2017-02-6_3-240_ABS-LH2/" ]
    #target_dir = "output/testingPxPy/"
    source_dirs = [
    #    "output/officialMC/2017-02-6-v3-OfficialMC_full/plots_9911_2017-02-6_3-170_ABS-LH2/",
        "output/officialMC/2017-02-6-v3-OfficialMC_full/plots_9910_2017-02-6_3-200_ABS-LH2/", 
    #    "output/officialMC/2017-02-6-v3-OfficialMC_full/plots_9909_2017-02-6_3-240_ABS-LH2/", 
    #    "output/officialMC/2017-02-6-v3-OfficialMC_full/plots_10268_2017-02-6_3-170_ABS-LH2-EMPTY/",
    #    "output/officialMC/2017-02-6-v3-OfficialMC_full/plots_10267_2017-02-6_3-200_ABS-LH2-EMPTY/", 
    #    "output/officialMC/2017-02-6-v3-OfficialMC_full/plots_10265_2017-02-6_3-240_ABS-LH2-EMPTY/", 
    ]
    target_dir = "output/testingRebinMC2D/"
    #target_dir = "output/testingMergePxPy/"
    #if not os.path.exists(target_dir)
    #  os.makedirs(target_dir)

    batch_level = 0
    hide_root_errors = True
    if batch_level < 10 and hide_root_errors:
        ROOT.gErrorIgnoreLevel = 6000
    top_labels = ["testingtop",]
    right_labels = ["testingright",]
    #config = CompareEfficiency(source_dir, target_dir, top_labels, right_labels)

    for source_dir in source_dirs:
        config = CompareMC2D(source_dir, target_dir, top_labels, right_labels)
        #config = CompareData2D(source_dir, target_dir, top_labels, right_labels)
        #config = CompareEfficiency(source_dir, target_dir, top_labels, right_labels)
        cong = ConglomerateContainer(config)
        cong.conglomerate()
    #ConglomerateOne


if __name__ == "__main__":

    testing_one()
    if not ROOT.gROOT.IsBatch():
        raw_input("Finished - press <CR> to end")
