import sys
import os
import site
import json
import shutil
import importlib
import time

import numpy
import ROOT

import xboa.common
import Configuration
import maus_cpp.globals
import maus_cpp.field
import maus_cpp.polynomial_map
import libxml2

import data_loader
import data_loader.load_all
import mice_analysis.mc_plotter
import mice_analysis.data_plotter
import mice_analysis.cuts_plotter
import mice_analysis.amplitude_analysis
import mice_analysis.globals_plotter
import mice_analysis.optics_plotter
import mice_analysis.efficiency_plotter
import mice_analysis.data_recorder
import mice_analysis.fractional_analysis
import mice_analysis.density_analysis
import mice_analysis.density_analysis_rogers
import mice_analysis.ang_mom_plotter
import mice_analysis.ang_mom_fields
import mice_analysis.momentum_correction
import utilities.root_style

config_file = None

class Analyser(object):
    """
    Class that drives the whole analysis
    * __init__ loads configuration file and sets up maus global stuff (fields,
               geometry, etc) for Analyser class.
    * do_analysis runs the analysis (__init__, birth and process phases as below)
    The analysis proceeds in a few different phases
    __init__: here we initialise the analysis. The analysis is divided into
              sub-analyses, each of which is a module in mice_analysis and 
              usually inheriting from the mice_analysis.analyse_base class. The
              sub-analyses are handed the configuration and a pointer to the
              data file parser (data_loader). Config is split into two portions;
              a generic config which is good for all analyses, and a 
              beam/data-specific config where things like tof cuts can be 
              stored, which might be different for different momenta etc.
    birth: in the birth phase, we load a few spills and then hand these to each
           mice_analysis class. Some of the classes use these for e.g. 
           dynamically selecting plot axes.
    process: we load more spills and hand these to mice_analysis classes for
            processing
    print/death phase: we do any calculation of global parameters, etc and then
            plot anything that needs plotting
    finalise: any final clean up
    """
    def __init__(self):
        """initialise the Analyser class"""
        config_mod = sys.argv[1].replace(".py", "")
        config_mod = config_mod.replace("scripts/", "")
        config_mod = config_mod.replace("/", ".")
        print "Using configuration module", config_mod
        config_file = importlib.import_module(config_mod)
        utilities.root_style.setup_gstyle()
        utilities.root_style.set_root_verbosity()
        ROOT.gROOT.SetBatch(True)
        self.config = config_file.Config()
        self.config_anal = None
        self.maus_globals(self.config)
        self.analysis_list = []
        self.anal_index = None
        # self.analysis_list_strings = []

    #def do_analysis(self, analysis_indices = []):
    #    """do the analysis, calling init, birth, process, print and finalise"""
    #    if not len(analysis_indices):
    #        analysis_indices = range(len(self.config.analyses))
    #    for i in analysis_indices:
    #        if i >= len(self.config.analyses):
    #            continue
    #        self.config_anal = self.config.analyses[i]
    #        print "Working in", self.config_anal["plot_dir"]
    #        try:
    #            self.init_phase()
    #            self.birth_phase()
    #            self.process_phase()
    #            self.print_phase()
    #            self.finalise_phase()
    #        except Exception:
    #            sys.excepthook(*sys.exc_info())

    def do_analysis(self, analysis_indices = []):
        """do the analysis, calling init, birth, process, print and finalise"""
        for i in range(len(self.config.analyses)):
            self.config_anal = self.config.analyses[i]
            if len(analysis_indices):
                self.anal_index = analysis_indices[0]
                self.config_anal["plot_dir"] = self.config_anal["plot_dir"] + str(self.anal_index)+"/"
            print "Working in", self.config_anal["plot_dir"]
            try:
                self.init_phase()
                self.birth_phase()
                self.process_phase()
                self.print_phase()
                self.finalise_phase()
            except Exception:
                sys.excepthook(*sys.exc_info())


    def maus_globals(self, config):
        """set up the maus globals"""
        try:
            os.makedirs("logs/tmp") # location for magnet cached maps
        except OSError:
            pass # probably the directory existed already

        print "Setting up maus globals"
        str_conf = Configuration.Configuration().\
                                          getConfigJSON(command_line_args=False)
        json_conf = json.loads(str_conf)
        json_conf["verbose_level"] = config.maus_verbose_level
        if hasattr(config, "geometry_path"):
            json_conf["simulation_geometry_filename"] = config.geometry_path
            print 'loading geom from', config.geometry_path
        maus_conf = json.dumps(json_conf)
        maus_cpp.globals.birth(maus_conf)
        #print maus_cpp.field.str(True)
        if hasattr(config, "geometry_path"):
            print 'Example field values', maus_cpp.field.get_field_value(0.0, 0.0, 15000., 0.)
            if sum([abs(val) for val in maus_cpp.field.get_field_value(0.0, 0.0, 15000., 0.)]) < 1e-9:
                print 'Failed to find any field vals. Exiting'
                sys.exit()

    def file_mangle(self, config_file_name):
        """
        Clear any old plots out of the way and make a new set of plots. This is
        done towards the end of the birth phase to give user a chance to back
        out (Ctrl-C) before things start getting deleted.
        """
        print "Clearing old data"
        try:
            if os.path.exists(self.config_anal["plot_dir"]):
                shutil.rmtree(self.config_anal["plot_dir"])
        except OSError:
            sys.excepthook(*sys.exc_info())
        os.makedirs(self.config_anal["plot_dir"])
        shutil.copy(config_file_name, self.config_anal["plot_dir"])

    def do_correction(self):
        if "momentum_correction" in self.config_anal and self.config_anal["momentum_correction"] == True:
            t1 = time.time()
            mice_analysis.momentum_correction.MomentumCorrection(self.config, self.config_anal, self.data_loader)
            t2 = time.time()
            print (t2-t1), 'seconds to run correction on', self.config.preanalysis_number_of_spills, 'spills'

    def init_phase(self):
        """
        Build the list of analyses and initialise
        """
        self.data_loader = data_loader.load_all.LoadAll(self.config, self.config_anal)
        self.data_loader.get_file_list()
        self.analysis_list = [] # force kill any analysis scripts in case death(...) did not happen in previous round
        if self.config_anal["do_mc"]:
            #print "Doing mc"
            # self.analysis_list_strings.append("Doing mc")
            self.analysis_list.append(mice_analysis.mc_plotter.MCPlotter(self.config, self.config_anal, self.data_loader))
        if self.config_anal["do_efficiency"]:
            #print "Doing efficiency"
            # self.analysis_list_strings.append("Doing efficiency")
            self.analysis_list.append(mice_analysis.efficiency_plotter.EfficiencyPlotter(self.config, self.config_anal, self.data_loader))
        if self.config_anal["do_plots"]:
            #print "Doing plots"
            # self.analysis_list_strings.append("Doing plots")
            self.analysis_list.append(mice_analysis.data_plotter.DataPlotter(self.config, self.config_anal, self.data_loader))
        if self.config_anal["do_cuts_plots"]:
            #print "Doing cuts plots"
            # self.analysis_list_strings.append("Doing cut plots")
            self.analysis_list.append(mice_analysis.cuts_plotter.CutsPlotter(self.config, self.config_anal, self.data_loader))
        if self.config_anal["do_globals"]:
            #print "Doing globals"
            # self.analysis_list_strings.append("Doing globals")
            self.analysis_list.append(mice_analysis.globals_plotter.GlobalsPlotter(self.config, self.config_anal, self.data_loader))
        if self.config_anal["do_optics"]:
            #print "Doing optics"
            # self.analysis_list_strings.append("Doing optics")
            self.analysis_list.append(mice_analysis.optics_plotter.OpticsPlotter(self.config, self.config_anal, self.data_loader))
        if self.config_anal["do_amplitude"]:
            #print "Doing amplitude"
            # self.analysis_list_strings.append("Doing amplitude")
            self.analysis_list.append(mice_analysis.amplitude_analysis.AmplitudeAnalysis(self.config, self.config_anal, self.data_loader))
        if self.config_anal["do_fractional_emittance"]:
            #print "Doing fractional emittance"
            # self.analysis_list_strings.append("Doing fractional emittance")
            self.analysis_list.append(mice_analysis.fractional_analysis.FractionalAnalysis(self.config, self.config_anal, self.data_loader))
        if self.config_anal["do_density"]:
            #print "Doing Drielsma kNN density estimation"
            # self.analysis_list_strings.append("Doing Drielsma kNN density estimation")
      	    self.analysis_list.append(mice_analysis.density_analysis.DensityAnalysis(self.config, self.config_anal, self.data_loader))
        if self.config_anal["do_density_rogers"]:
            #print "Doing Rogers kNN density estimation"
            # self.analysis_list_strings.append("Doing Rogers kNN density estimation")
      	    self.analysis_list.append(mice_analysis.density_analysis_rogers.DensityAnalysis(self.config, self.config_anal, self.data_loader))
        if self.config_anal["do_data_recorder"]:
            #print "Doing data recorder"
            # self.analysis_list_strings.append("Doing data recorder")
            self.analysis_list.append(mice_analysis.data_recorder.DataRecorder(self.config, self.config_anal, self.data_loader))
        if "do_ang_mom" in self.config_anal and self.config_anal["do_ang_mom"]:
            #print "Doing angular momentum"
            self.analysis_list.append(mice_analysis.ang_mom_plotter.AngMomPlotter(self.config, self.config_anal, self.data_loader))
        if "do_ang_mom_fields" in self.config_anal and self.config_anal["do_ang_mom_fields"]:
            #print "Doing angular momentum with field loader"
            self.analysis_list.append(mice_analysis.ang_mom_fields.AngMomFields(self.config, self.config_anal, self.data_loader))

        if self.anal_index is not None:
            self.analysis_list = [self.analysis_list[self.anal_index]]


    def birth_phase(self):
        """
        Load the first set of spills and start doing some analysis
        """
        all_event_count = 0
        self.data_loader.load_spills(self.config.preanalysis_number_of_spills)
        self.config.maus_version = self.data_loader.maus_version

        self.file_mangle(sys.argv[1])
        self.do_correction()
        for analysis in self.analysis_list:
            analysis.birth()
        self.data_loader.clear_data()

    def process_phase(self):
        """
        More processing
        """
        now = time.time()
        while self.data_loader.load_spills(self.config.analysis_number_of_spills) and \
              self.data_loader.check_spill_count():
            self.do_correction()
            for analysis in self.analysis_list:
            #for counter, analysis in enumerate(self.analysis_list):
                #print "\n\n\n -------- Running " + str(self.analysis_list_strings[counter]) + " -------- \n\n\n"
                analysis.process()
            self.data_loader.clear_data()
            if now - time.time() > 1800: # 30 mins
                self.print_phase()

    def print_phase(self):
        """
        Finalise any plots and save them to disk in analysis.death
        """
        for analysis in self.analysis_list:
            analysis.death()

    def finalise_phase(self):
        """Any final close out"""
        self.analysis_list = []
        self.data_loader = None
        print "Finished ", self.config_anal["name"], "writing results to", self.config_anal["plot_dir"]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: python calculate_emittance.py </path/to/config/script> [analyses list]"
        sys.exit(1)
    analyser = Analyser()
    analysis_indices = [int(i) for i in sys.argv[2:]]
    if len(analysis_indices) > 1 :
        print "[ERROR]: Received too many analysis indices. Require one or zero options. \n BREAK"
        sys.exit()
    analyser.do_analysis(analysis_indices)
    print "Done - press <CR> to finish"

