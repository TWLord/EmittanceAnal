import sys
import subprocess
import os

def is_csc():
    uname = subprocess.check_output(['uname', '-a'])
    #uname = "blank"
    #uname = "epp-ui01"
    return '.warwick.' in uname

def is_imp():
    uname = subprocess.check_output(['uname', '-a'])
    #uname = "blank"
    #uname = "epp-ui01"
    return '.ic.ac' in uname

def run_single(scriptname, queue, version, config, templatedir, jobsuffix, CC, geodir, settings):
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
                geopath = os.path.join(geodir,'runnumber_'+runnumber+'/ParentGeometryFile.dat')
                rc = subprocess.check_call([scriptname, ABS, run, runnumber, Optics, CC, version, config, queue, templatedir, jobsuffix, geopath, use_preanal])
                #rc = subprocess.check_call([scriptname, ABS, run, runnumber, Optics, CC, version, config, queue, templatedir, jobsuffix])



def run_cumulative(scriptname, queue, version, config, templatedir, jobsuffix, CC, geodir, settings):
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
            runnumber = str(run_list[0]).rjust(5, '0')
            geopath = os.path.join(geodir,'runnumber_'+runnumber+'/ParentGeometryFile.dat')
            rc = subprocess.check_call([scriptname, ABS, runs_, runscomma, Optics, CC, version, config, queue, templatedir, jobsuffix, geopath])


def run_systematics(scriptname, queue, version, config, templatedir, jobsuffix, CC, geodir, settings):
    print "Running each run individually"
    base_only = settings["base_only"]
    print "Doing systematics with base_only =", base_only
    raw_input("Press Enter to continue...")

    #sys_list = ["tku_base_tkd_fiducial_radius", "tku_base_tkd_chi2_threshold",]

    sys_list = ["tku_base", "tku_base_tkd_fiducial_radius", "tku_base_tkd_chi2_threshold", "tku_pos_plus", "tku_rot_plus", "tku_scale_C_plus", "tku_scale_E1_plus", "tku_scale_E2_plus", "tku_density_plus", "tkd_rot_plus", "tkd_pos_plus", "tkd_scale_C_plus", "tkd_scale_E1_plus", "tkd_scale_E2_plus", "tkd_density_plus"]

    #sys_list = ["tku_density_plus"]

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
                geopath = os.path.join(geodir,'runnumber_'+runnumber+'/ParentGeometryFile.dat')
                #systematic = "tku_base"
                #rc = subprocess.check_call([scriptname, ABS, run, runnumber, Optics, CC, version, config, queue, templatedir, jobsuffix, systematic])
                if base_only: # only run tku_base mc for more statistics here
                    sys_list = ["tku_base",]
                for systematic in sys_list:
                    if systematic.find("tku_base") >= 0: # Sets source data file to tku_base for cut change systematics
                        sysfile = "tku_base"
                    else:
                        sysfile = systematic
                    rc = subprocess.check_call([scriptname, ABS, run, runnumber, Optics, CC, version, config, queue, templatedir, jobsuffix, geopath, systematic, sysfile])


def run_single_with_systematics(scriptname, queue, version, config, templatedir, jobsuffix, CC, geodir, settings):
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
                geopath = os.path.join(geodir,'runnumber_'+runnumber+'/ParentGeometryFile.dat')
                rc = subprocess.check_call([scriptname, ABS, run, runnumber, Optics, CC, version, config, queue, templatedir, jobsuffix, geopath, use_preanal, sys_abs, sys_vers])
                #rc = subprocess.check_call([scriptname, ABS, run, runnumber, Optics, CC, version, config, queue, templatedir, jobsuffix])


def run_cumulative_with_systematics(scriptname, queue, version, config, templatedir, jobsuffix, CC, geodir, settings):
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
            runnumber = str(run_list[0]).rjust(5, '0')
            geopath = os.path.join(geodir,'runnumber_'+runnumber+'/ParentGeometryFile.dat')
            sys_abs = get_sys_absorber(CC, Optics)
            rc = subprocess.check_call([scriptname, ABS, runs_, runscomma, Optics, CC, version, config, queue, templatedir, jobsuffix, geopath, sys_abs, sys_vers])

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

# shared systematics run used for all absorber settings
def get_sys_settings(CC):
    run_settings = {
        "2017-02-6":{
            "ABS-LH2":{
                "3-140":["9883",],
                "6-140":["9885",],
                "10-140":["9886",],
                "3-170":["9911",],
                "3-200":["9910",],
                "3-240":["9909",],
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
       "2017-02-7":{
            "ABS-LH2":{
                "10-140":["9953",],
            },
        },
        "2017-02-6":{
            "ABS-LH2":{
                "3-140":["9883",],
           #     "6-140":["9885",],
           #     "10-140":["9886",],
           #     "3-170":["9911",],
           #     "3-200":["9910",],
           #     "3-240":["9909",],
            },
           # "ABS-LH2-EMPTY":{
           #     "3-140":["10243",],
           #     "6-140":["10245",],
           #     "10-140":["10246",],
           #     "3-170":["10268",],
           #     "3-200":["10267",],
           #     "3-240":["10265",],
           # },
           # "ABS-SOLID-EMPTY":{
           #     "3-140":["10314",],
           #     "4-140":["10317",],
           #     "6-140":["10318",],
           #     "10-140":["10319",],
           # },
           # "ABS-SOLID-LiH":{
           #     "3-140":["10508",],
           #     "4-140":["10504",],
           #     "6-140":["10509",],
           # },
        },
        "M2D-flip-2017-02-5":{
            "ABS-LH2":{
                "3-140":["9867",],
                "6-140":["9868",],
                "10-140":["9869",],
            },
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
        "2017-02-2":{
            "ABS-LH2":{
                ####"3-200":["9756",], # old
                "3-200":["9760",], # use this
                #"6-200":["9761",], # use this
                ####"10-200":["9762",], # old + bad diffuser
                #"10-200":["9763",],
            },
            #"ABS-LH2-EMPTY":{
            #    ##"3-200":["10231",], # single run D1 current different, not used
            #    "3-200":["10236",], # old - use this
            #    "6-200":["10235",], # old - use this
            #    "10-200":["10233",], # old - use this
            #    ##"10-200":["10238",], # maybe cancel this one, not used
            #    "6-240":["10241",], # old - use this
            #},
        },
        "2017-02-1":{
            "ABS-LH2":{
                "3-140":["9723",],
                "6-140":["9724",],
                "10-140":["9725",],
            },
            "ABS-LH2-EMPTY":{
                "3-140":["9661",], # M3-Test3
                "6-140":["9665",], # M3-Test2
                "10-140":["9667",], # M3-Test4
                "3-170":["9717",], # M3-Test1
                "3-200":["9718",], # M3-Test1
                "3-240":["9719",], # M3-Test1
		# Early (probably bad) settings
                ##"3-140":["9634",], # M3-Test2
                ##"10-140":["9638",], # M3-Test3, not used..
		# Different geomID to the above
                #"3-140":["10288",], # M3-Test3
                #"6-140":["10290",], # M3-Test2
                #"10-140":["10292",], # M3-Test4
            },
        },
        "2016-05-1":{
            "ABS-SOLID-LiH":{
	        "3-200":["9060",],
            },
        },
        "2016-05-1-SSUSSD":{
            "ABS-SOLID-LiH":{
	        "3-140":["9161",],
	        "3-170":["9160",],
	        "3-200":["9155",],
	        "3-240":["9159",],
            },
        },
        "2016-04-2.4a":{
            "ABS-SOLID-EMPTY":{
                "6-240":["10404",],
                "10-240":["10405",],
            },
            #"ABS-SOLID-LiH":{
            #    "6-240":["8877",],
            #    "10-240":["8908",],
            #},
        },
        "2016-04-1.7":{
            "ABS-SOLID-EMPTY":{
	        "3-200":["10372",],
	        "6-200":["10373",],
	        "10-200":["10375",],
	    },
            "ABS-SOLID-LiH":{
	        "3-200":["8793",],
	        "6-200":["8795",],
	        "10-200":["8817",],
            },
        },
        "2016-04-1.5":{
            "ABS-SOLID-LiH":{
	        "3-140":["8733",],
	        "6-140":["8736",],
	        "10-140":["8737",],
	        "3-170":["8767",],
	        "3-200":["8757",],
	        "3-240":["8747",],
            },
        },
        "2016-04-1.2":{
            "ABS-SOLID-EMPTY":{
	        "3-140":["10345",],
	        "6-140":["10346",],
	        "10-140":["10347",],
            },
            "ABS-SOLID-LiH":{
	        "3-140":["8643",],
	        "3-170":["8646",],
	        "3-200":["8647",],
	        "3-240":["8649",],
            },
        },
    }[CC]

    return run_settings


def get_data_settings(CC):
    run_settings = {
        "2017-02-6":{
            "ABS-LH2":{
                "3-140":["9883", "9888", "9893", "9897", "9903", "9906",],
                "6-140":["9884", "9885", "9889", "9894", "9898", "9904", "9905",],
                "10-140":["9886", "9887", "9890", "9891", "9892", "9895", "9896", "9899", "9900", "9901", "9902",],
                "3-170":["9911",],
                "3-200":["9910", "9915"],
                "3-240":["9907", "9908", "9909", "9912", "9913", "9914",],
            },
            "ABS-LH2-EMPTY":{
                "3-140":["10243", "10248", "10253", "10254", "10255", "10256",],
                "6-140":["10245", "10247", "10249",],
                "10-140":["10246", "10250", "10251", "10252", "10257", "10258", "10259", "10260",],
                "3-170":["10268", "10269",],
                "3-200":["10262", "10266", "10267", "10275",],
                "3-240":["10261", "10264", "10265", "10270", "10271", "10272", "10273", "10274",],
            },
            "ABS-SOLID-EMPTY":{
                "3-140":["10313", "10314", "10323", "10327", "10333",],
                "4-140":["10315", "10317", "10322", "10328", "10334",],
                "6-140":["10318", "10324", "10329", "10335",],
                "10-140":["10319", "10321", "10325", "10326", "10330", "10331", "10332",],
            },
            "ABS-SOLID-LiH":{
                "3-140":["10508", "10511",],
                "4-140":["10504", "10505", "10506", "10507",],
                "6-140":["10509", "10510"],
            },
        },
        "M2D-flip-2017-02-5":{
            "ABS-LH2":{
                "3-140":["9867",],
                "6-140":["9868", "9871", "9873", "9874",],
                "10-140":["9869", "9870",],
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
        "2017-02-2":{
            "ABS-LH2":{
                "3-200":["9756", "9757", "9758", "9760", "9764", "9766", "9769", "9770", "9771",],
                "6-200":["9749", "9750", "9751", "9752", "9761", "9765",],
                "10-200":["9754", "9755", "9759", "9763", "9767", "9768",], # not 9762, bad diffuser
            },
            "ABS-LH2-EMPTY":{
                #"3-200":["10231",], # single run D1 current different - M3-Test1
                "3-200":["10236", "10237", "10240",], # M3-Test2 - not 10231, M3-Test1
                "6-200":["10232", "10234", "10235", "10242",], # 
                "10-200":["10227", "10230", "10233", "10238", "10239",], # 
                "6-240":["10241",], # only run 
            },
        },
        "2017-02-1":{
            "ABS-LH2":{
                "3-140":["9723", "9726", "9729", "9733", "9738", "9741", "9744", "9745",], # M3-Test3
                "6-140":["9724", "9727", "9730", "9734", "9736", "9739", "9742", "9747",], # M3-Test2
                "10-140":["9725", "9728", "9732", "9737", "9740", "9743",], # M3-Test4
            },
            "ABS-LH2-EMPTY":{
                "3-140":["9654", "9659", "9660", "9661", "9677", "9678", "9679", "9683", "9687", "9690", "9691", "9694", "9698",], # M3-Test3
                "6-140":["9637", "9662", "9663", "9665", "9666", "9671", "9676", "9680", "9681", "9684", "9688", "9692", "9695", "9699",], # M3-Test2
                "10-140":["9667", "9668", "9670", "9672", "9673", "9674", "9675", "9685", "9686", "9689", "9693", "9697",], # M3-Test4
		# Early (probably bad) settings
                ##"3-140":["9634",], # M3-Test2
                ##"10-140":["9638", "9664",], # M3-Test3, not used..
                "3-170":["9717",], # M3-Test1
                "3-200":["9701", "9718",], # M3-Test1
                "3-240":["9719", "9720",], # M3-Test1
		## Different geomID to the above
                ##"3-140":["10288", "10289", "10294",], # M3-Test3
                ##"6-140":["10287", "10290", "10293",], # M3-Test2
                ##"10-140":["10286", "10292", "10295", "10296", "10297", "10298",], # M3-Test4
            },
        },
        "2016-05-1":{
            "ABS-SOLID-LiH":{
	        "3-200":["9053", "9059", "9060", "9061", "9062", "9063", "9064", "9065", "9066",],
            },
        },
        "2016-05-1-SSUSSD":{
            "ABS-SOLID-LiH":{
	        "3-140":["9161",],
	        "3-170":["9160", "9162",],
	        "3-200":["9155", "9156", "9157", "9158",],
	        "3-240":["9159",],
            },
        },
        "2016-04-2.4a":{
            "ABS-SOLID-EMPTY":{
	        "6-240":["10404", "10406", "10408", "10411", "10413", "10414", "10417", "10420",],
                "10-240":["10402", "10403", "10405", "10407", "10410", "10412", "10415", "10416", "10418", "10419", "10421", "10422",],
	    },
            "ABS-SOLID-LiH":{
                "6-240":["8873", "8874", "8875", "8877", "8878", "8879", "8880", "8881", "8882",],
                "10-240":["8907", "8908", "8914", "8915", "8916", "8917",],
            },
        },
        "2016-04-1.7":{
            "ABS-SOLID-EMPTY":{
	        "3-200":["10372", "10377", "10391", "10392",],
	        "6-200":["10373", "10378", "10393", "10394",],
	        "10-200":["10375", "10380", "10381", "10388", "10389", "10395", "10396", "10397",],
	    },
            "ABS-SOLID-LiH":{
	        "3-200":["8776", "8777", "8793", "8797", "8798", "8799", "8816",],
	        "6-200":["8794", "8795", "8796",],
	        "10-200":["8817", "8818", "8819", "8820", "8821", "8822", "8823", "8824", "8825", "8826", "8827", "8828",],
            },
        },
        "2016-04-1.5":{
            "ABS-SOLID-LiH":{
	        "3-140":["8733", "8734", "8738", "8749", "8751", "8754", "8762", "8768", "8771", "8774",],
	        "6-140":["8736", "8739", "8744", "8752", "8755", "8761", "8769", "8772", "8775",],
	        "10-140":["8737", "8740", "8745", "8753", "8756", "8759", "8760", "8773",],
	        "3-170":["8764", "8766", "8767",],
	        "3-200":["8757", "8765",],
	        "3-240":["8747", "8748", "8750",],
            },
        },
        "2016-04-1.2":{
            "ABS-SOLID-EMPTY":{
	        "3-140":["10344", "10345", "10349", "10353", "10357", "10358", "10365",],
	        "6-140":["10346", "10350", "10354", "10359", "10366",],
	        "10-140":["10347", "10348", "10351", "10352", "10355", "10356", "10360", "10361", "10362", "10363", "10364", "10367",],
            },
            "ABS-SOLID-LiH":{
	        "3-140":["8643", "8650", "8664", "8675", "8678", "8681", "8684", "8686", "8688", "8690", "8694", "8695", "8696", "8697", "8698", "8709",],
	        "3-170":["8646", "8655", "8656", "8660", "8666", "8705", "8706", "8710", "8711", "8712", "8713", "8714", "8715", "8717", "8718", "8719", "8720", "8721", "8722", "8723", "8724", "8725", "8726", "8727", "8728", "8729", "8730", "8731",],
	        "3-200":["8647", "8648", "8657", "8661", "8707",],
	        "3-240":["8649", "8658", "8662", "8668", "8672", "8673", "8674", "8708",],
            },
        },
    }[CC]

    return run_settings

def get_jobsuffix(config):
    jobsuffix = {
        "c1":"mc_cuts",
        "c2":"reco",
        "c3":"mc",
        "c4":"c4", #"ownmc",
        "c5":"c5", #"recomcstat+corr",
        "c6":"c6", #"recoownmcstat+corr",
        "c7":"c7", #"systematics",
        "c8":"c8", #"sysstat+corr",
        "c9":"c9", #"mcsysstat+corr",
        "c10":"c10", #"sysstat+corr_abs",
        "c11":"c11", #"mcsysstat+corr_abs",
        "c12":"c12", #"angmomfields",
        "c13":"c13", #"mcangmomfields",
        "c14":"c14", #"angmomfields_scaledcorr",
        "c15":"c15", #"mcangmomfields_scaledcorr",
        "c16":"c16", #"angmomfields_recalccorr",
        "c17":"c17", #"mcangmomfields_recalccorr",
        "c18":"c18", #"angmomfields_sysstat_abs",
        "c19":"c19", #"mcangmomfields_sysstat_abs",
        "2f":"recopreanal",
        "3f":"mcpreanal",
        "beams":"beams",
    }[config]
    return jobsuffix

if __name__ == "__main__":
  #for config in ("c14", "c15", "c16", "c17"):
  #for config in ("c13",):
  #for config in ("c15", "c17"):
 #for d1 in ["0pt96", "0pt98", "1pt02", "1pt04"]:
  #for d2 in ["0pt96", "0pt98", "1pt0", "1pt02", "1pt04", "1pt06"]:
    #version = "v"+d1+"_d1_"+d2+"_d2"
    #print version

    ############################################################# 

    #geodir = "/vols/mice/tlord1/Geometries/"
    geodir = "/storage/epp2/phumhf/MICE/Geometries/"
    #geodir = "/data/mice/phumhf/Geometries/"
  
    # RUN SETTINGS HERE
    ######################
    queue = "xxl" #"medium" #"xxl" #### Currently redundant for SLURM/QSUB jobsub
    version = "v3" # Official MC version
    #config = "3f"
    #config = "c3"
    #config = "c1"
    #config = "c5"
    #config = "c8"
    #config = "c2"
    #config = "c12"
    #config = "c13"
    #config = "c18"
    #config = "c19"

    config = "beams"

    #config = "c4"
    #config = "c6"
    #version = "v1"
    #version = "v2"
    #version = "v3"
    #version = "v4"
    #version = "v5"
    #version = "v6"
    #version = "v7"
    #version = "v8"
    #version = "v9"
    #version = "v10"
    #version = "v11"
    #version = "v12"
    #version = "v13"
    #version = "v14"
    #version = "v15"
    #version = "v16"
    #version = "v17"
    #version = "v18"
    #version = "v19"
    #version = "v20"
    #version = "v21"
    #version = "v22"
    #version = "v23"
    #version = "v24"
    #version = "v25"
    #version = "v26"
    #version = "v27"
    #version = "v28"
    #version = "v29"

    #version = "v102"
    #version = "v104"

    #version = "v500"
    #version = "v501"
    #version = "v502"
    #version = "v503"
    #version = "v504"
    #version = "v505"
    #version = "v506"
    #version = "v507"
    #version = "v508"
    #version = "v509"
    #version = "v600"
    #version = "v666"
    #version = "v700"

    #version = "v30"
    #version = "v201"

    #version = "v111"

    #config = "c7"
    #version = "v107"

    #config = "c10"
    #config = "c11"

    sys_vers = "v107"

    #CC = "2016-04-1.2"
    #CC = "2016-04-1.5"
    #CC = "2016-04-1.7"
    #CC = "2016-04-2.4a"
    #CC = "2016-05-1"
    #CC = "2016-05-1-SSUSSD"
    #CC = "2017-02-1"
    #CC = "2017-02-2"
    #CC = "2016-04-2.4a"
    CC = "2017-02-5"
    #CC = "M2D-flip-2017-02-5"
    #CC = "2017-02-6"
    #CC = "2017-02-7"

    #use_preanal = "True" # "FALSE" # "True" # Old self-defined version.. user error possible
    use_preanal = False # True # False # True 
    base_only = False #True # False 
    split_routines = False # True

    #config = "c2"

    #SLURM = False # True
    SLURM = is_csc()
    QSUB = is_imp()
    print "is csc -", SLURM
    print "is imp -", QSUB

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
    elif config == "c2" or config == "c5" or config == "c6" or config == "c8" or config == "c10" or config == "c12" or config == "c14" or config == "c16" or config == "c18":
        scriptname = "py_dojobsub.sh"
        if split_routines:
            scriptname = "py_dojobsub_splitroutines.sh"
    else:
        scriptname = "pymovedata_dojobsub.sh"
        if split_routines:
            scriptname = "pymovedata_dojobsub_splitroutines.sh"

    if SLURM:
        scriptname = "./SLURM/" + scriptname
    elif QSUB:
        scriptname = "./QSUB/" + scriptname
    else:
        scriptname = "./LSF/" + scriptname

    settings = {}

    if use_preanal:
        use_preanal = "True"
    else:
        use_preanal = "FALSE"

    if config == "c1" or config == "c3" or config == "c4" or config == "3f" or config == "c13" or config == "c15" or config == "c17" or config == "beams":
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
    elif config == "c8" or config == "c10" or config == "c18":
        run_function = run_cumulative_with_systematics
        settings["runs"] = get_data_settings(CC)
        settings["sys_vers"] = sys_vers
        settings["sys_settings"] = get_sys_settings(CC) 
    elif config == "c9" or config == "c11" or config == "c19":
        run_function = run_single_with_systematics
        settings["runs"] = get_mc_settings(CC)
        settings["sys_vers"] = sys_vers
        settings["sys_settings"] = get_sys_settings(CC) 
        settings["use_preanal"] = use_preanal
    else:
        settings["runs"] = get_data_settings(CC)
  
    print "Split Routines -", split_routines
    print "Config", config
    print "version", version
    config = config.strip("c")
    run_function(scriptname, queue, version, config, templatedir, jobsuffix, CC, geodir, settings)
    #run_function(scriptname, queue, version, config, templatedir, jobsuffix, CC, settings, extra_opt)
