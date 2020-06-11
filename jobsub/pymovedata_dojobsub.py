import sys
import subprocess
import os

def is_csc():
    uname = subprocess.check_output(['uname', '-a'])
    #uname = "blank"
    #uname = "epp-ui01"
    return '.warwick.' in uname

def run_single(scriptname, queue, version, config, templatedir, jobsuffix, CC, settings):
    print "Running each run individually"
    use_preanal = settings["use_preanal"]
    print "with use_preanal =", use_preanal 
    raw_input("Press Enter to continue...")
    run_settings = settings["runs"]
    for ABS, all_optics in run_settings.iteritems():
        for Optics, run_list in all_optics.iteritems():
            for run in run_list:
                print "Running", ABS, Optics, run
    raw_input("Press Enter to continue...")
    for ABS, all_optics in run_settings.iteritems():
        for Optics, run_list in all_optics.iteritems():
            for run in run_list:
                runnumber = str(run).rjust(5, '0')
                rc = subprocess.check_call([scriptname, ABS, run, runnumber, Optics, CC, version, config, queue, templatedir, jobsuffix, use_preanal])
                #rc = subprocess.check_call([scriptname, ABS, run, runnumber, Optics, CC, version, config, queue, templatedir, jobsuffix])



def run_cumulative(scriptname, queue, version, config, templatedir, jobsuffix, CC, settings):
    print "Running data runs cumulatively"
    print "Can't use preanal here yet"
    raw_input("Press Enter to continue...")
    run_settings = settings["runs"]
    for ABS, all_optics in run_settings.iteritems():
        for Optics, run_list in all_optics.iteritems():
            runs = ""
            for run in run_list:
                runs += run+", "
            print "Running ", ABS, Optics, runs
    raw_input("Press Enter to continue...")

    for ABS, all_optics in run_settings.iteritems():
        for Optics, run_list in all_optics.iteritems():
            runs_ = ""
            runscomma = ""
            for run in run_list:
                runs_ += run+"_"
                #runscomma += '\\"'+run+'\\", '
                runscomma += run+', '
            runs_ = runs_[0:len(runs_)-1]
            runscomma = runscomma[0:len(runscomma)-2]
            #print runs_
            #print runscomma
            #raw_input("Press Enter..")
            rc = subprocess.check_call([scriptname, ABS, runs_, runscomma, Optics, CC, version, config, queue, templatedir, jobsuffix])


def run_systematics(scriptname, queue, version, config, templatedir, jobsuffix, CC, settings):
    print "Running each run individually"
    base_only = settings["base_only"]
    print "Doing systematics with base_only =", base_only
    raw_input("Press Enter to continue...")

    #sys_list = ["tku_base_tkd_fiducial_radius", "tku_base_tkd_chi2_threshold",]

    #sys_list = ["tku_base", "tku_base_tkd_fiducial_radius", "tku_base_tkd_chi2_threshold", "tku_pos_plus", "tku_rot_plus", "tku_scale_C_plus", "tku_scale_E1_plus", "tku_scale_E2_plus", "tku_density_plus", "tkd_rot_plus", "tkd_pos_plus", "tkd_scale_C_plus", "tkd_scale_E1_plus", "tkd_scale_E2_plus", "tkd_density_plus"]

    sys_list = ["tku_density_plus"]

    run_settings = settings["runs"]

    for ABS, all_optics in run_settings.iteritems():
        for Optics, run_list in all_optics.iteritems():
            for run in run_list:
                print "Running", ABS, Optics, run
                print ', '.join(sys_list)
    raw_input("Press Enter to continue...")
    for ABS, all_optics in run_settings.iteritems():
        for Optics, run_list in all_optics.iteritems():
            for run in run_list:
                runnumber = str(run).rjust(5, '0')
                #systematic = "tku_base"
                #rc = subprocess.check_call([scriptname, ABS, run, runnumber, Optics, CC, version, config, queue, templatedir, jobsuffix, systematic])
                if base_only: # only run tku_base mc for more statistics here
                    sys_list = ["tku_base",]
                for systematic in sys_list:
                    if systematic.find("tku_base") >= 0: # Sets source data file to tku_base for cut change systematics
                        sysfile = "tku_base"
                    else:
                        sysfile = systematic
                    rc = subprocess.check_call([scriptname, ABS, run, runnumber, Optics, CC, version, config, queue, templatedir, jobsuffix, systematic, sysfile])


def run_single_with_systematics(scriptname, queue, version, config, templatedir, jobsuffix, CC, settings):
    print "Running each run individually"
    use_preanal = settings["use_preanal"]
    print "with use_preanal =", use_preanal 
    raw_input("Press Enter to continue...")
    run_settings = settings["runs"]
    sys_settings = settings["sys_settings"]
    sys_vers = settings["sys_vers"]
    for ABS, all_optics in run_settings.iteritems():
        for Optics, run_list in all_optics.iteritems():
            for run in run_list:
                sys_abs = get_sys_absorber(CC, Optics)
                print "Running", ABS, Optics, run, 'sys abs:', sys_abs
    raw_input("Press Enter to continue...")
    for ABS, all_optics in run_settings.iteritems():
        for Optics, run_list in all_optics.iteritems():
            for run in run_list:
                sys_abs = get_sys_absorber(CC, Optics)
                runnumber = str(run).rjust(5, '0')
                rc = subprocess.check_call([scriptname, ABS, run, runnumber, Optics, CC, version, config, queue, templatedir, jobsuffix, use_preanal, sys_abs, sys_vers])
                #rc = subprocess.check_call([scriptname, ABS, run, runnumber, Optics, CC, version, config, queue, templatedir, jobsuffix])


def run_cumulative_with_systematics(scriptname, queue, version, config, templatedir, jobsuffix, CC, settings):
    print "Running data runs cumulatively"
    print "Can't use preanal here yet"
    raw_input("Press Enter to continue...")
    run_settings = settings["runs"]
    sys_settings = settings["sys_settings"]
    sys_vers = settings["sys_vers"]
    for ABS, all_optics in run_settings.iteritems():
        for Optics, run_list in all_optics.iteritems():
            runs = ""
            for run in run_list:
                runs += run+", "

            sys_abs = get_sys_absorber(CC, Optics)
            print "Running ", ABS, Optics, runs, 'sys abs:', sys_abs
    raw_input("Press Enter to continue...")

    for ABS, all_optics in run_settings.iteritems():
        for Optics, run_list in all_optics.iteritems():
            runs_ = ""
            runscomma = ""
            for run in run_list:
                runs_ += run+"_"
                #runscomma += '\\"'+run+'\\", '
                runscomma += run+', '
            runs_ = runs_[0:len(runs_)-1]
            runscomma = runscomma[0:len(runscomma)-2]
            sys_abs = get_sys_absorber(CC, Optics)
            rc = subprocess.check_call([scriptname, ABS, runs_, runscomma, Optics, CC, version, config, queue, templatedir, jobsuffix, sys_abs, sys_vers])

def get_sys_absorber(CC, Optics):
    run_settings = get_sys_settings(CC)
    for absorber in run_settings.keys():
        optics_dict = run_settings[absorber]
        optics_vals = optics_dict.keys()
        for optics in optics_vals:
            if optics == Optics:
                return absorber
    print "[ERROR]: No appropriate absorber found"
    print "for", Optics, ",", CC
    sys.exit()

def get_sys_settings(CC):
    run_settings = {
        "2017-02-6":{
            "ABS-LH2":{
                "3-140":["9883",],
                "6-140":["9885",],
                "10-140":["9886",],
                #"3-170":["9911",],
                #"3-200":["9910",],
                #"3-240":["9909",],
            },
            "ABS-SOLID-EMPTY":{
                "4-140":["10317",],
            },
        },
        "2017-02-5":{
            #"ABS-LH2":{
            #    "3-140":["9920",],
            #    "6-140":["9921",],
            #    "10-140":["9922",],
            #},
            "ABS-LH2-EMPTY":{
                "3-140":["10143",],
                "6-140":["10144",],
                "10-140":["10145",],
            },
        },
    }[CC]

    return run_settings



def get_mc_settings(CC):
    run_settings = {
        "2017-02-6":{
            "ABS-LH2":{
                "3-140":["9883",],
            #    "6-140":["9885",],
            #    "10-140":["9886",],
            #    "3-170":["9911",],
            #    #"3-200":["9910",],
            #    "3-240":["9909",],
            },
            "ABS-LH2-EMPTY":{
                "3-140":["10243",],
            #    "6-140":["10245",],
            #    "10-140":["10246",],
            #    "3-170":["10268",],
            #    "3-200":["10267",],
            #    "3-240":["10265",],
            },
            #"ABS-SOLID-EMPTY":{
            #    "3-140":["10314",],
            #    "4-140":["10317",],
            #    "6-140":["10318",],
            #    "10-140":["10319",],
            #},
            #"ABS-SOLID-LiH":{
            #    "3-140":["10508",],
            #    "4-140":["10504",],
            #    "6-140":["10509",],
            #},
        },
        "2017-02-5":{
            "ABS-LH2":{
                "3-140":["9920",],
                "6-140":["9921",],
                "10-140":["9922",],
            },
            "ABS-LH2-EMPTY":{
                "3-140":["10143",],
                "6-140":["10144",],
                "10-140":["10145",],
            },
        },
    }[CC]

    return run_settings


def get_data_settings(CC):
    run_settings = {
        "2017-02-6":{
            "ABS-LH2":{
            #    "3-140":["9883", "9888", "9893", "9897", "9903", "9906",],
            #    "6-140":["9884", "9885", "9889", "9894", "9898", "9904", "9905",],
            #    "10-140":["9886", "9887", "9890", "9891", "9892", "9895", "9896", "9899", "9900", "9901", "9902",],
            #    "3-170":["9911",],
            #    "3-200":["9910", "9915"],
            #    "3-240":["9907", "9908", "9909", "9912", "9913", "9914",],
            },
            "ABS-LH2-EMPTY":{
            #    "3-140":["10243", "10248", "10253", "10254", "10255", "10256",],
            #    "6-140":["10245", "10247", "10249",],
            #    "10-140":["10246", "10250", "10251", "10252", "10257", "10258", "10259", "10260",],
            #    "3-170":["10268", "10269",],
            #    "3-200":["10262", "10266", "10267", "10275",],
            #    "3-240":["10261", "10264", "10265", "10270", "10271", "10272", "10273", "10274",],
            },
            "ABS-SOLID-EMPTY":{
            #    "3-140":["10313", "10314", "10323", "10327", "10333",],
                "4-140":["10315", "10317", "10322", "10328", "10334",],
            #    "6-140":["10318", "10324", "10329", "10335",],
            #    "10-140":["10319", "10321", "10325", "10326", "10330", "10331", "10332",],
            },
            "ABS-SOLID-LiH":{
            #    "3-140":["10508", "10511",],
                "4-140":["10504", "10505", "10506", "10507",],
            #    "6-140":["10509", "10510"],
            },
        },
        "2017-02-5":{
            "ABS-LH2":{
                "3-140":["9918", "9920", "9923", "9926", "9932",],
                "6-140":["9921", "9924", "9927", "9931",],
                "10-140":["9922", "9925", "9928", "9929", "9930",],
            },
            "ABS-LH2-EMPTY":{
                "3-140":["10142", "10143", "10147",],
                "6-140":["10141", "10144", "10148",],
                "10-140":["10138", "10139", "10140", "10145", "10146", "10149", "10150",],
            },
        },
    }[CC]

    return run_settings

def get_jobsuffix(config):
    jobsuffix = {
        "c2":"reco",
        "c3":"mc",
        "c4":"ownmc",
        "c5":"recomcstat+corr",
        "c6":"recoownmcstat+corr",
        "c7":"systematics",
        #"c8":"sysstat+corr",
        "2f":"recopreanal",
        "3f":"mcpreanal",
        "c8":"c8",
        "c9":"c9",
        "c10":"c10",
        "c11":"c11",
    }[config]
    return jobsuffix

if __name__ == "__main__":
  
    # RUN SETTINGS HERE
    ######################
    queue = "xxl" #"medium" #"xxl" #### Currently redundant for SLURM jobsub
    #version = "v3" # Official MC version
    #config = "3f"
    #config = "c3"
    #config = "c5"
    #config = "c8"
    #config = "c2"

    #config = "c4"
    config = "c6"
    version = "v1"
    #version = "v2"

    #config = "c7"
    #version = "v107"

    #config = "c10"
    #config = "c11"
    #version = "v107"

    sys_vers = "v107"

    CC = "2017-02-5"
    #CC = "2017-02-6"

    #use_preanal = "True" # "FALSE" # "True" # Old self-defined version.. user error possible
    use_preanal = True # False # True 
    base_only = False #True # False 

    #config = "c2"

    #SLURM = False # True
    SLURM = is_csc()
    print "is csc -", SLURM

    ###################### 

    #run_function = run_single
    run_function = run_cumulative
  
    #templatedir = "config/solenoid/2017-02-6/ABS-TEMPLATE"
    templatedir = "config/templates"

    jobsuffix = get_jobsuffix(config)
  
    if config == "c7":
        scriptname = "py_dojobsub_systematics.sh"
        #scriptname = "py_dojobsub.sh"
    elif config == "2f" or config == "3f":
        scriptname = "py_dopreanalysis.sh"
        templatedir = "config/templates/file_reducer"
    elif config == "c2" or config == "c5" or config == "c6" or config == "c8" or config == "c10":
        scriptname = "py_dojobsub.sh"
    else:
        scriptname = "pymovedata_dojobsub.sh"

    if SLURM:
        scriptname = "./SLURM/" + scriptname
    else:
        scriptname = "./LSF/" + scriptname

    settings = {}

    if use_preanal:
        use_preanal = "True"
    else:
        use_preanal = "FALSE"

    if config == "c3" or config == "c4" or config == "3f":
        run_function = run_single
        settings["runs"] = get_mc_settings(CC)
        settings["use_preanal"] = use_preanal
        #extra_opt = use_preanal
    elif config == "2f":
        run_function = run_single
        settings["runs"] = get_data_settings(CC)
    elif config == "3f":
        run_function = run_single
        settings["runs"] = get_mc_settings(CC)
    elif config == "c7":
        run_function = run_systematics
        settings["runs"] = get_sys_settings(CC)
        settings["base_only"] = base_only
        #extra_opt = base_only
    elif config == "c8" or config == "c10":
        run_function = run_cumulative_with_systematics
        settings["runs"] = get_data_settings(CC)
        settings["sys_vers"] = sys_vers
        settings["sys_settings"] = get_sys_settings(CC) 
    elif config == "c9" or config == "c11":
        run_function = run_single_with_systematics
        settings["runs"] = get_mc_settings(CC)
        settings["sys_vers"] = sys_vers
        settings["sys_settings"] = get_sys_settings(CC) 
        settings["use_preanal"] = use_preanal
    else:
        settings["runs"] = get_data_settings(CC)
  
    print "Config", config
    config = config.strip("c")
    run_function(scriptname, queue, version, config, templatedir, jobsuffix, CC, settings)
    #run_function(scriptname, queue, version, config, templatedir, jobsuffix, CC, settings, extra_opt)
