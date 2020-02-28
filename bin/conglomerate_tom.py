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

class ComparePlot(CompareConfig):
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
                "z_range":[0,1.5],
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
    source_dir = "/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/output/combinedMC+Data/officialMC/2017-02-6-c3-OfficialMC_v3+c6-reco-sys+corr_full/plots_Simulated_2017-02-6_3-240_ABS-LH2/"
    #source_dir = "output/combinedMC+Data/officialMC/2017-02-6-c3-OfficialMC_v3+c6-reco-sys+corr_full/plots_Simulated_2017-02-6_3-240_ABS-LH2/efficiency_plots/"
    #target_file = "~/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/output/combinedMC+Data/officialMC/2017-02-6-c3-OfficialMC_v3+c6-reco-sys+corr_full/plots_2017-02-6_3-240_ABS-LH2/cut_plots/tku_p_9_0.root"
    #target_file = "~/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/output/combinedMC+Data/officialMC/2017-02-6-c3-OfficialMC_v3+c6-reco-sys+corr_full/plots_2017-02-6_3-240_ABS-LH2/cut_plots/tku_p_9_0.root"
    #target_dir = "/home/phumhf/MICE/newdir/"
    target_dir = "output/testingCong/"
    #if not os.path.exists(target_dir)
    #  os.makedirs(target_dir)

    batch_level = 0
    hide_root_errors = True
    if batch_level < 10 and hide_root_errors:
        ROOT.gErrorIgnoreLevel = 6000
    top_labels = ["testingtop",]
    right_labels = ["testingright",]
    config = ComparePlot(source_dir, target_dir, top_labels, right_labels)
    cong = ConglomerateContainer(config)
    cong.conglomerate()
    #ConglomerateOne


if __name__ == "__main__":

    testing_one()
    if not ROOT.gROOT.IsBatch():
        raw_input("Finished - press <CR> to end")
