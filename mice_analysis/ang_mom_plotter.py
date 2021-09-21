import copy
import sys
import numpy
import ROOT
import xboa.common

from itertools import izip
import utilities.utilities

from analysis_base import AnalysisBase

# global constants
c = 299792458.0
e = 1.60218e-19

class AngMomPlotter(AnalysisBase):
    def __init__(self, config, config_anal, data_loader):
        super(AngMomPlotter, self).__init__(config, config_anal, data_loader)
        self.data_loader = data_loader
        self.ellipse_dict = {}
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
        #do_mc = self.config_anal["do_mc"]
        self.do_ang_mc = self.config_anal["do_ang_mom_mc"]
        if self.do_ang_mc is not None:
            for station in self.var_out.keys():
                self.var_out["mc_virtual_"+station] = {"ds":[]}

        """    for z_pos, dummy, detector in self.config.virtual_detectors:
                if z_pos < self.min_z_us:
                    continue
                self.var_out["global_through_"+detector] = {"ds":[]}
        #        if z_pos < self.min_z_ds:
        #            continue
        #        self.var_out["global_ds_"+detector] = {"ds":[]}"""
        self.refaffed_ellipse_dict = {}
        # individual plots
        self.process_args = {}
        self.mc_stations = {}
        self.failed_pids = {}
        #self.bz = {"tku":0., "tkd":0.}
        self.bz = {}

        if hasattr(self.config, "ang_mom_bz"):
            self.bz = self.config.ang_mom_bz
        else:
            for i in range(2,6)+["tp"]:
                self.bz["tku_"+str(i)] = self.config.bz_tku
                self.bz["tkd_"+str(i)] = self.config.bz_tkd

    def birth(self):
        self.set_plot_dir("ang_mom_plots")
        self.get_var_list()
        for detector in self.var_out:
            for cut in self.var_out[detector]:
                self.birth_ellipse(detector, cut)
                self.process_ellipse(detector, cut)
        # Individual plots
        self.mc_stations = self.config.mc_plots["mc_stations"]
        # includes other stations
        #for i in range(2,6):
        #    self.mc_stations["tku_"+str(i)] = ["mc_virtual_tku_"+str(i)]
        #    self.mc_stations["tkd_"+str(i)] = ["mc_virtual_tkd_"+str(i)]
        #print self.mc_stations

        self.birth_L_res()
        for detector, virt_station_list in self.mc_stations.iteritems(): 
            if "tku" not in detector and "tkd" not in detector:
                continue
            if self.do_ang_mc is not None:
                for virt_station in virt_station_list:
                    self.birth_var_one_d("Bz_at_"+virt_station+"_us_cut", virt_station, "pid", "bz", cuts = "us cut")
                    self.birth_var_two_d_hist("r_vs_Bz_at_"+virt_station+"_us_cut", virt_station, "r", "bz", cuts = "upstream_cut", wild_x_axis=True, wild_y_axis=True)

            virt_station = virt_station_list[0]

            self.birth_var_two_d_hist("L_kin_vs_L_field_at_"+detector+"_us_cut", detector, "L_kin", "L_field", cuts = "upstream_cut")
            for L in ["L_canon", "L_kin", "L_field"]:
                if self.do_ang_mc is not None:
                    #self.birth_var_one_d(L+"_at_"+virt_station+'_all', virt_station, "pid", L)
                    self.birth_var_one_d(L+"_at_"+virt_station+'_ds_cut', virt_station, "pid", L, cuts = "ds cut", wild_x_axis=True)

                self.birth_var_one_d(L+"_at_"+detector+'_all', detector, "pid", L, wild_x_axis=True)
                self.birth_var_one_d(L+"_at_"+detector+'_ds_cut', detector, "pid", L, cuts = "ds cut", wild_x_axis=True)

                self.birth_var_two_d_hist("r_vs_"+L+"_at_"+detector+"_us_cut", detector, "r", L, cuts = "upstream_cut")
                self.birth_var_two_d_hist("r_vs_"+L+"_at_"+detector+"_ds_cut", detector, "r", L, cuts = "downstream_cut")

                #self.birth_var_three_d_hist("px_vs_py_vs_"+L+"_at_"+detector+"_all", detector, "px", "py", L)
                #self.birth_var_three_d_hist("px_vs_py_vs_"+L+"_at_"+detector+"_us_cut", detector, "px", "py", L, cuts = "upstream_cut")
                #self.birth_var_three_d_hist("px_vs_py_vs_"+L+"_at_"+detector+"_ds_cut", detector, "px", "py", L, cuts = "downstream_cut")

                self.birth_var_three_d_hist("x_vs_y_vs_"+L+"_at_"+detector+"_all", detector, "x", "y", L)
                self.birth_var_three_d_hist("x_vs_y_vs_"+L+"_at_"+detector+"_us_cut", detector, "x", "y", L, cuts = "upstream_cut")
                self.birth_var_three_d_hist("x_vs_y_vs_"+L+"_at_"+detector+"_ds_cut", detector, "x", "y", L, cuts = "downstream_cut")



    def process(self):
        # Individual plots
        for name in sorted(self.process_args.keys()):
            process_function = self.process_args[name][0]
            process_args = self.process_args[name][1]
            process_function(name, *process_args)
        self.process_L_res()
        # Ellipse plots
        self.get_var_list()
        for detector in self.var_out:
            for cut in self.var_out[detector]:
                self.process_ellipse(detector, cut)

    def death(self):
        # Individual plots
        self.death_three_d_hist()
        # Ellipse plots
        ds_lambda = lambda detector_name: "mc_virtual_tk" not in detector_name
        virtual_lambda = lambda detector_name: "mc_virtual_tk" in detector_name

        lambda_list = [("source_tkd", ds_lambda, ROOT.kRed)]
        if self.do_ang_mc is not None:
            lambda_list.append(("source_mc_tkd", virtual_lambda, ROOT.kViolet))

        #ds_lambda = lambda detector_name: "global_through_" in detector_name

        #us_lambda = lambda detector_name: detector_name == "tku_tp" or "global_through" in detector_name
        #ds_lambda = lambda detector_name: detector_name == "tkd_tp" or "global_ds" in detector_name
        #for prefix, detector_lambda, color in ("source_tku", us_lambda, ROOT.kBlue), ("source_tkd", ds_lambda, ROOT.kRed):

        #for prefix, detector_lambda, color in ("source_mc_tkd", virtual_lambda, ROOT.kViolet), ("source_tkd", ds_lambda, ROOT.kRed):

        for prefix, detector_lambda, color in lambda_list:
            self.refaff_ellipse_dict(detector_lambda) # rotate the data structure view
            for var, sub_var in [
                            ("mean", 0),
                            ("mean", 1),
                            ("mean", 2),
                            ("mean", 3),
                            ("mean", 4),
                            ("mean", 5),
                            ("beta_4d", None),
                            ("beta_x", None),
                            ("beta_y", None),
                            ("l_kin", None),
                            ("l_centre", None),
                            ("l_field", None),
                            ("l_canon", None),
                            ("l_canon_plus_mean", None),
                            ("l_twiddle_1", None), # Calculated L_canon/(2.*emit*mu_mass)
                            ("l_twiddle_x", None), # from beta_x
                            ("l_twiddle_y", None), # from beta_y
                            ("l_twiddle_2", None), # (l_twiddle_x**2 + l_twiddle_y**2)**0.5
                            ("l_twiddle_3", None), # from l_kin + beta_perp*kappa
                            ("mean_r2", None),
                            ("Bz", None),
                            ("nevents", None),
                            ("sigma", 0),
                            ("sigma", 2),
                        ]:
                try:
                    self.plot("ds", var, sub_var, color, prefix) # mean z
                except Exception:
                    sys.excepthook(*sys.exc_info())
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
                if "all" in cuts and not self.will_cut_us(event):
                    self.var_out[detector]["all"].append(this_var_list)
                if "us" in cuts and not self.will_cut_ds(event):
                    self.var_out[detector]["us"].append(this_var_list)
                if "ds" in cuts and not self.will_cut_ds(event):
                    self.var_out[detector]["ds"].append(this_var_list)

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
        ellipse["Bz"] = 0.
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
        for data in all_data:
            m_events += 1
            for i in range(n_var):
                this_mean[i] += data[i]
                for j in range(i, n_var):
                    this_matrix[i][j] += data[i]*data[j]
        if m_events+n_events == 0:
            return

        # sum r2 and update ellipse
        this_r2 = 0.
        for data in all_data:
            this_r2 += (data[0]**2 + data[2]**2)
        r2 = ellipse["mean_r2"]
        r2 = r2*n_events/(n_events+m_events) + \
                  this_r2/(n_events+m_events)
        ellipse["mean_r2"] = r2

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
        Bz = self.get_field(detector)*1e3 # conv to Tesla # Does not use exact field for MC virtual planes
        ellipse["Bz"] = Bz
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
        print ' ---- '
        print 'Detector :', detector
        print 'Bz', Bz
        print 'beta', beta
        print 'kappa', kappa
        print 'beta*kappa', beta*kappa
        print '<xPy - yPx>', l_kin
        print '<xPy - yPx>/2*m*c*epsilon = l_twiddle - beta_perp*kappa = ', l_kin/2./mu_mass/(emit)
        print 'l_twiddle from <l_canon> with mean subtracted', ellipse["l_twiddle_1"]
        print 'l_twiddle from <l_canon> with mean added back in', ellipse["l_twiddle_1_plus_mean"]
        print 'l_twiddle from <l_kin>/2*m*c*epsilon + beta*kappa ', ellipse["l_twiddle_3"]
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

        # ang_mom bits in m
        """l_kin = (matrix[0][3]-matrix[1][2]) * (1e-3) # Conversion from MeV/c mm to MeV/c m
        Bz = self.get_field(detector)*1e3 # conv to Tesla # Does not use exact field for MC virtual planes
        ellipse["Bz"] = Bz
        beta_m = beta/1e3 # beta is in terms of mm! Scale up to m
        kappa = (Bz/2./mean[4]) / (1e6/c) # convert Bz to MeV/c to J/m^2/A?
        #kappa = Bz/2./mean[4]/(1.4440271*1e-3) # conv Tesla to natural
        ellipse["l_twiddle_x"] = matrix[0][3] # <xPy> for now
        ellipse["l_twiddle_y"] = matrix[1][2] # <yPx> for now

        l_field = (1*r2*Bz/2)  / (1e6*1e6/c) # q/q # conv from J mm /s (q/q) -> eV mm /s (sq) -> to MeV/c m 
        ellipse["l_kin"] = l_kin # L_average - L_beamcentre
        ellipse["l_centre"] = (mean[0]*mean[3] - mean[1]*mean[2]) * 1e-3 # conv from MeV/c mm to MeV/c m
        ellipse["l_field"] = l_field # 
        ellipse["l_canon"] = l_kin + l_field # 
        ellipse["l_canon_plus_mean"] = l_kin + l_field + ellipse["l_centre"] # have to add back in mean 
        ellipse["l_twiddle_1"] = ellipse["l_canon"]/2./mu_mass/(emit*1e-3) # with means added back in
        ellipse["l_twiddle_1_plus_mean"] = ellipse["l_canon_plus_mean"]/2./mu_mass/(emit*1e-3) # no messing with mean
        ellipse["l_twiddle_3"] = (l_kin/2./mu_mass/(emit*1e-3)) + beta_m*kappa # should maybe be without messing with means
        ellipse["emit_4d"] = emit
        print ' ---- '
        print 'Detector :', detector
        print 'Bz', Bz
        #print 'beta', beta
        #print 'beta_m', beta_m
        #print 'kappa', kappa
        #print 'beta_m*kappa', beta_m*kappa
        #print '<xPy - yPx>', l_kin
        #print '<xPy - yPx>/-2*m*c*epsilon = beta_m_perp*kappa - l_twiddle = ', l_kin/-2./mu_mass/(emit*1e-3)
        #print 'l_twiddle from <l_canon> with mean added', ellipse["l_twiddle_1"]
        #print 'l_twiddle from <l_canon> leaving mean subtracted', ellipse["l_twiddle_1_minus_mean"]
        #print 'l_twiddle from <l_kin>/2*m*c*epsilon ', ellipse["l_twiddle_3"]
        print 'l_canon', ellipse["l_canon"]
        print 'l_canon_plus_mean', ellipse["l_canon_plus_mean"]
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
        ellipse["l_twiddle_x"] = (ellipse["l_twiddle_x"]/mu_mass/(ellipse["emit_x"]*1e-3)) + (ellipse["beta_x"]*1e-6*kappa)
        ellipse["l_twiddle_y"] = (ellipse["l_twiddle_y"]/-1./mu_mass/(ellipse["emit_y"]*1e-3)) + (ellipse["beta_y"]*1e-6*kappa)
        ellipse["l_twiddle_2"] = (ellipse["l_twiddle_x"]**2 + ellipse["l_twiddle_x"]**2)**0.5"""

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
            name = str(var)+"_"+self.ellipse_variables[sub_var]+"_"+cut
            axis = str(var)+" "+self.ellipse_variables[sub_var]+" ("+cut+")"
        return name, axis

    def get_field(self, detector):
        for key in self.bz.keys():
            if key in detector: 
                bz = self.bz[key]
                return bz
        return 0.

        """if "tku" in detector:
            bz = self.bz["tku"]
        elif "tkd" in detector:
            bz = self.bz["tkd"]
        else: 
            bz = 0.
        return bz"""

    def get_L_hit(self, detector_hit, var): # takes detector_hit as inp
        hit = detector_hit["hit"]
        bz = self.get_field(detector_hit["detector"])
        """if "tku" in detector_hit["detector"]:
            bz = self.bz["tku"]
        elif "tkd" in detector_hit["detector"]:
            bz = self.bz["tkd"]
        else: 
            bz = 0."""
        if "mc_virtual_tk" in detector_hit["detector"]: # use true field - maybe remove, disentangle
            #print "mc bz", detector_hit["hit"]["bz"]
            bz = detector_hit["hit"]["bz"]
            #charge = detector_hit["hit"]["charge"]
            #pid = detector_hit["hit"]["pid"]
            #print "charge", charge
            #print "pid", pid

        L = self.get_L(hit, bz, var)
        #L = self.get_L_SI(bz, var, hit["x"], hit["y"], hit["px"], hit["py"])
        return L
        #return L*1e23

    def get_L_tracker(self, hit, tracker, var): # takes event[tracker] as inp
        bz = self.bz[tracker+"_tp"]
        L = self.get_L(hit, bz, var)
        #L = self.get_L_SI(bz, var, hit["x"], hit["y"], hit["px"], hit["py"])
        return L
        #return L*1e23

    def get_L(self, hit, bz, var):
        x = hit["x"] * 1e-3 # mm to m
        y = hit["y"] * 1e-3 # mm to m
        px = hit["px"] # MeV
        py = hit["py"] # MeV
        bz *= 1e3 # Field values are scaled 1e-3 in MAUS - bc mm units?

        r = (x**2 + y**2)**0.5
        #q = 1.60218e-19 # J
        q = 1 # eV

        # in MeV/c
        L_kin = (x*py) - (y*px)
        L_field = q*(r**2)*bz/2 / (1e6 / c)

        L_canon = L_kin + L_field 
        if var == "L_kin":
            return L_kin
        elif var == "L_field":
            return L_field
        elif var == "L_canon":
            return L_canon
        return 0 

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

    def plot(self, cut, var, sub_var, color, prefix):
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
            #try:
            var_list = [ellipse[var][sub_var]*units for ellipse in ellipse_list if pred(ellipse)]
            #except TypeError:
            #    print "TYPE ERROR", var, sub_var, ellipse
            #    raise
        name, axis = self.name_lookup(var, sub_var, cut)
        hist, graph = self.make_root_graph(name, name+"_"+prefix,
                      z_list, "z [m]", var_list, axis, True,
                      None, None, None, None)
        if len(self.get_plot(name)["histograms"]) == 1:
            hist.Draw()
        graph.SetMarkerStyle(20)
        graph.SetMarkerColor(color)
        graph.Draw("p l same")
        #det_list = self.config.detectors
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
                    #if "L_" in plot_variable:
                        #x*Py - y*Px
                        plot_var = self.get_L_hit(detector_hit, plot_variable)
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
                    #if var == "L":
                        #x*Py - y*Px
                        val = self.get_L_hit(detector_hit, var)
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
                    #if var == "L":
                        #x*Py - y*Px
                        val = self.get_L_hit(detector_hit, var)
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

    def birth_var_three_d_hist(self, name, detector, plot_variable_1, plot_variable_2, plot_variable_3, cuts=False):
        track_final = self.get_data_var_three_d_hist(name, detector, plot_variable_1, plot_variable_2, plot_variable_3, cuts)
        if len(track_final) == 0:
            print "No tracks for", detector
            return
        xmin, xmax, ymin, ymax = -50., 50., -50., 50.
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


    def birth_L_res(self):
        for L in ["L_canon", "L_kin", "L_field"]:
            L_tku_cut_us, L_tku_cut_ds, L_tku_all = self.get_tracker_hit_data("tku", L, self.has_both_trackers)
            L_tkd_cut_us, L_tkd_cut_ds, L_tkd_all = self.get_tracker_hit_data("tkd", L, self.has_both_trackers)
            dL_cut_us = [L_tku - L_tkd_cut_us[i] for i, L_tku in enumerate(L_tku_cut_us)]
            dL_cut_ds = [L_tku - L_tkd_cut_ds[i] for i, L_tku in enumerate(L_tku_cut_ds)]
            dL_all = [L_tku - L_tkd_all[i] for i, L_tku in enumerate(L_tku_all)]

            axis = L+"_{tku} - "+L+"_{tkd} [MeV/c m]"
            hist = self.make_root_histogram(L+"_res", L+"_res all", dL_all, axis, 100, [], '', 0, [], -10., 10.)
            hist_cut_us = self.make_root_histogram(L+"_res", L+"_res us cut", dL_cut_us, axis, 100, [], '', 0, [], -10., 10.)
            hist_cut_ds = self.make_root_histogram(L+"_res", L+"_res ds cut", dL_cut_ds, axis, 100, [], '', 0, [], -10., 10.)
            hist.Draw()
            hist_cut_us.Draw("SAME")
            hist_cut_ds.Draw("SAME")
            self.get_plot(L+"_res")["config"]["draw_1d_cuts"] = True

            hist = self.make_root_histogram(L+"_res_vs_"+L+"_tku", L+"_res_vs_"+L+"_tku", L_tku_cut_ds, L+"_{tku} [MeV/c m]", 100,
                                                              dL_cut_ds, L+"_{tku} - "+L+"_{tkd} [MeV/c m]", 100,
                                                              [], None, None, -15, 15)
            hist.Draw("COLZ")

    def process_L_res(self):
        for L in ["L_canon", "L_kin", "L_field"]:
            L_tku_cut_us, L_tku_cut_ds, L_tku_all = self.get_tracker_hit_data("tku", L, self.has_both_trackers)
            L_tkd_cut_us, L_tkd_cut_ds, L_tkd_all = self.get_tracker_hit_data("tkd", L, self.has_both_trackers)
            dL_cut_us = [L_tku - L_tkd_cut_us[i] for i, L_tku in enumerate(L_tku_cut_us)]
            dL_cut_ds = [L_tku - L_tkd_cut_ds[i] for i, L_tku in enumerate(L_tku_cut_ds)]
            dL_all = [L_tku - L_tkd_all[i] for i, L_tku in enumerate(L_tku_all)]

            L_res_hists = self.get_plot(L+"_res")["histograms"]
            for data, hist_key in (dL_cut_us, "us cut"), (dL_cut_ds, "ds cut"), (dL_all, "all"):
                hist = L_res_hists[L+"_res "+hist_key]
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


