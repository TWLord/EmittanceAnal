import subprocess

def run_single(scriptname, queue, version, config, templatedir, jobsuffix, CC, settings):
    print "Running each run individually"
    raw_input("Press Enter to continue...")
    for ABS, all_optics in settings.iteritems():
        for Optics, run_list in all_optics.iteritems():
            for run in run_list:
                print "Running", ABS, Optics, run
    raw_input("Press Enter to continue...")
    for ABS, all_optics in settings.iteritems():
        for Optics, run_list in all_optics.iteritems():
            for run in run_list:
                rc = subprocess.check_call([scriptname, ABS, run, Optics, CC, version, config, queue, templatedir, jobsuffix])



def run_cumulative(scriptname, queue, version, config, templatedir, jobsuffix, CC, settings):
    print "Running data runs cumulatively"
    raw_input("Press Enter to continue...")
    for ABS, all_optics in settings.iteritems():
        for Optics, run_list in all_optics.iteritems():
            runs = ""
            for run in run_list:
                runs += run+", "
            print "Running ", ABS, Optics, runs
    raw_input("Press Enter to continue...")

    for ABS, all_optics in settings.iteritems():
        for Optics, run_list in all_optics.iteritems():
            runs = ""
            for run in run_list:
                #runs += run+", "
                runs += run+"_"
            runs = runs.substring(0, runs.length() -1)
            rc = subprocess.check_call([scriptname, ABS, runs, Optics, CC, version, config, queue, templatedir, jobsuffix])

def get_mc_settings(CC):
    settings = {
        "2017-02-6":{
            "ABS-LH2":{
                #"3-140":["9883",],
                #"6-140":["9885",],
                #"10-140":["9886",],
                #"3-170":["9911",],
                #"3-200":["9910",],
                "3-240":["9909",],
            },
            #"ABS-LH2-EMPTY":{
            #    "3-140":["10243",],
            #    "6-140":["10245",],
            #    "10-140":["10246",],
            #    "3-170":["10268",],
            #    "3-200":["10267",],
            #    "3-240":["10265",],
            #},
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
            #"ABS-LH2-EMPTY":{
            #    "3-140":["10143",],
            #    "6-140":["10144",],
            #    "10-140":["10145",],
            #},
        },
    }[CC]

    return settings


def get_data_settings(CC):
    settings = {
        "2017-02-6":{
            "ABS-LH2":{
                #"3-140":["9883", "9888", "9893", "9897", "9903", "9906",],
                #"6-140":["9884", "9885", "9889", "9894", "9898", "9904", "9905",],
                #"10-140":["9886", "9887", "9890", "9891", "9892", "9895", "9896", "9899", "9900", "9901", "9902",],
                #"3-170":["9911",],
                #"3-200":["9910", "9915"],
                "3-240":["9907", "9908", "9909", "9912", "9913", "9914",],
            },
#            "ABS-LH2-EMPTY":{
#                "3-140":["10243", "10248", "10253", "10254", "10255", "10256",],
#                "6-140":["10245", "10247", "10249",],
#                "10-140":["10246", "10250", "10251", "10252", "10257", "10258", "10259", "10260",],
#                "3-170":["10268", "10269",],
#                "3-200":["10262", "10266", "10267", "10275",],
#                "3-240":["10261", "10264", "10265", "10270", "10271", "10272", "10273", "10274",],
#            },
#            "ABS-SOLID-EMPTY":{
#                "3-140":["10313", "10314", "10323", "10327", "10333",],
#                "4-140":["10315", "10317", "10322", "10328", "10334",],
#                "6-140":["10318", "10324", "10329", "10335",],
#                "10-140":["10319", "10321", "10325", "10326", "10330", "10331", "10332",],
#            },
#            "ABS-SOLID-LiH":{
#                "3-140":["10508", "10511",],
#                "4-140":["10504", "10505", "10506", "10507",],
#                "6-140":["10509", "10510"],
#            },
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

    return settings

def get_jobsuffix(config):
    jobsuffix = {
        "c2":"reco",
        "c3":"mc",
        "c4":"ownmc",
        "c5":"recomcstat+corr",
        "c6":"recoownmcstat+corr",
        "c7":"systematics",
        "c8":"sysstat+corr",
        "2f":"recopreanal",
        "3f":"mcpreanal",
    }[config]
    return jobsuffix

if __name__ == "__main__":
  
    # RUN SETTINGS HERE
    ######################
    queue = "xxl" #"medium" #"xxl" #### Currently redundant for SLURM jobsub
    version = "v3"
    #config = "3f"
    config = "c3"
    #version = "v2"
    #config = "c4"
    #CC = "2017-02-5"
    CC = "2017-02-6"

    #config = "c2"

    SLURM = True

    ###################### 

    #run_function = run_single
    run_function = run_cumulative
  
    #templatedir = "config/solenoid/2017-02-6/ABS-TEMPLATE"
    templatedir = "config/templates"

    jobsuffix = get_jobsuffix(config)
  
    if config == "c7":
        scriptname = "pymovedata_dojobsub_systematics.sh"
    elif config == "2f" or config == "3f":
        scriptname = "py_dopreanalysis.sh"
        templatedir = "config/templates/file_reducer"
    else:
        scriptname = "pymovedata_dojobsub.sh"

    if SLURM:
        scriptname = "./SLURM/" + scriptname
    else:
        scriptname = "./LSF/" + scriptname

    if config == "c3" or config == "c4" or config == "c7" or config == "3f":
        run_function = run_single
        settings = get_mc_settings(CC)
    elif config == "2f":
        run_function = run_single
        settings = get_data_settings(CC)
    else:
        settings = get_data_settings(CC)
  
    print "Config", config
    config = config.strip("c")
    run_function(scriptname, queue, version, config, templatedir, jobsuffix, CC, settings)

