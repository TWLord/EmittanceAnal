import os
import ROOT

import xboa

import utilities.utilities

class AnalysisBase(object):
    def __init__(self, config, config_anal, data_loader):
        self.data_loader = data_loader
        self.config = config
        self.config_anal = config_anal
        self.plot_dir = config_anal["plot_dir"]
        self.plots = {}
        self.process_list = {}
        self.death_list = {}

    def set_plot_dir(self, sub_dir):
        self.plot_dir = self.config_anal["plot_dir"]+"/"+sub_dir+"/"
        os.makedirs(self.plot_dir)

    def birth(self):
        raise NotImplementedError("should be implemented by derived class")

    def process(self):
        raise NotImplementedError("should be implemented by derived class")

    def death(self):
        raise NotImplementedError("should be implemented by derived class")

    def check_memory(self):
        #print ''.join(os.popen('free -t -m').readlines())
        #print ''.join(os.popen('ps -m -o %cpu,%mem,command').readlines())
        print ''.join(os.popen('ps aux | grep phumhf | grep python').readlines())

    def get_plot(self, name):
        if name not in self.plots:
            new_plot = {}
            new_plot["config"] = self.get_default_config()
            
            new_plot["canvas"] = ROOT.TCanvas(name, name, 1400, 1000)
            pad = ROOT.TPad(name+"-pad", "pad info", 0.10, 0.05, 0.97, 1.0)
            pad.Draw()
            new_plot["pad"] = pad
            new_plot["histograms"] = {}
            new_plot["graphs"] = {}
            new_plot["misc"] = {}
            self.plots[name] = new_plot
        self.plots[name]["pad"].cd()
        return self.plots[name]

    def make_root_histogram(self, name, *args):
        my_plot = self.get_plot(name)
        if len(args[4]) > 0: # 2d hist
            frame_color = utilities.utilities.get_frame_fill()
            my_plot["canvas"].SetFrameFillColor(frame_color)
        hist = xboa.common.make_root_histogram(*args)
        my_plot["histograms"][args[0]] = hist
        #print my_plot
        return hist

    def project_root_histogram_3d(self, name, *args): 
        hist = self.plots[name]["histograms"][args[0]]
        #print "old plot : "
        #print self.plots[name]
        #print "args[0] : " + str(args[0])
        #print "args[1] : " + str(args[1])
        projhist = hist.Project3DProfile(args[1])
        projhist.SetStats(0)
        projhist.GetXaxis().SetTitle(hist.GetXaxis().GetTitle())
        projhist.GetYaxis().SetTitle(hist.GetYaxis().GetTitle())
        projhist.GetZaxis().SetTitle(hist.GetZaxis().GetTitle())
        #newname = name+"_p"+args[1]
        newname = name+"_profile_"+args[1]
        my_plot = self.get_plot(newname)
        frame_color = utilities.utilities.get_frame_fill() # New
        my_plot["canvas"].SetFrameFillColor(frame_color) # New
        my_plot["histograms"][args[1]] = projhist
        #print "new plot : "
        #print my_plot 
        return projhist

    """def make_root_histogram_3d(self, name, *args):
        my_plot = self.get_plot(name)
        #if len(args[4]) > 0: # 2d hist
        #    frame_color = utilities.utilities.get_frame_fill()
        #    my_plot["canvas"].SetFrameFillColor(frame_color)
        hist = xboa.common.make_root_histogram_3d(*args)
        my_plot["histograms"][args[0]] = hist
        return hist"""

    def make_root_histogram_3d(self, name, name_string, x_float_list, x_axis_string, n_x_bins, y_float_list, y_axis_string, n_y_bins, z_float_list, z_axis_string, n_z_bins, weight_list=[], xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None,
                        line_color=1, line_style=1, line_width=2, fill_color=0, stats=0, hist_title_string=''):
        #line_color=rg.line_color, line_style=rg.line_style, line_width=rg.line_width, fill_color=rg.fill_color, stats=rg.stats, hist_title_string=''):
        my_plot = self.get_plot(name)

        ###### xboa starts here
        xboa.common.has_root()
        histo_margin = 0.0
        #name_string += " "+str(len(_hist_persistent)) ### Need to replace hist_persistent with suitable proxy??
        if len(y_float_list) == len(x_float_list) and len(y_float_list) == len(z_float_list) :
          x_min_max = xboa.common.min_max(x_float_list, weight_list, margin=histo_margin, xmin=xmin, xmax=xmax)
          y_min_max = xboa.common.min_max(y_float_list, weight_list, margin=histo_margin, xmin=ymin, xmax=ymax)
          z_min_max = xboa.common.min_max(z_float_list, weight_list, margin=histo_margin, xmin=zmin, xmax=zmax)
          hist = ROOT.TH3D(name_string, hist_title_string+';'+x_axis_string+';'+y_axis_string+';'+z_axis_string, n_x_bins, x_min_max[0], x_min_max[1], n_y_bins, y_min_max[0], y_min_max[1], n_z_bins, z_min_max[0], z_min_max[1])
          if(len(weight_list) == len(x_float_list)):
            for i in range( len(x_float_list) ):
              hist.Fill(x_float_list[i], y_float_list[i], z_float_list[i], weight_list[i])
          else:
            for i in range( len(x_float_list) ):
              hist.Fill(x_float_list[i], y_float_list[i], z_float_list[i])
        else:
          print "passed variable lists not all same length"
        #_hist_persistent.append(hist) ### Need to replace hist_persistent with suitable proxy??
        hist.SetLineColor(line_color)
        hist.SetLineStyle(line_style)
        if fill_color!=None: hist.SetFillColor(fill_color)
        hist.SetStats(stats)
        ###### xboa ends here

        my_plot["histograms"][name_string] = hist
        return hist

    def make_root_graph(self, name, *args):
        my_plot = self.get_plot(name)
        hist, graph = xboa.common.make_root_graph(*args)
        my_plot["graphs"][args[0]] = graph
        my_plot["histograms"][args[0]] = hist
        return hist, graph

    def print_plots(self):
        for name, my_plot in self.plots.iteritems():
            #print "name : " + str(name)
            #print "my_plot : " + str(my_plot)
            plot_dir = self.plot_dir
            if my_plot["config"]["sub_dir"] != None:
                plot_dir = os.path.join(plot_dir, my_plot["config"]["sub_dir"])
                try:
                    os.makedirs(plot_dir)
                except OSError:
                    pass
            my_plot["canvas"].cd()
            my_plot["canvas"].Draw()
            my_plot["canvas"].Update()
            plot_title = name.replace(" ", "_")
            for format in ["png", "root", "eps"]:
                my_plot["canvas"].Print(plot_dir+"/"+plot_title+"."+format)

    def del_plots(self):
        print 'Clearing', len(self.plots.keys()), 'plots'
        self.check_memory()
        for name, my_plot in self.plots.items():
            for histname in self.plots[name]['histograms'].keys():
                self.plots[name]['histograms'][histname].GetListOfFunctions().Delete()
                self.plots[name]['histograms'][histname].Delete()
                del self.plots[name]['histograms'][histname]
            self.plots[name]['pad'].Close()
            self.plots[name]['pad'].Delete()
            obj = self.plots[name]["canvas"]
            obj.IsA().Destructor( obj )
            for key, item in my_plot.items():
                if key == 'config':
                    continue
                if type(item) == dict:
                    for key2, item2 in item.items():
                        if type(item2) == dict:
                            print key, item, key2, item2
                            continue
                        print key, item, key2, item2
                        obj = self.plots[name][key][key2]
                        obj.IsA().Destructor( obj )
                        del self.plots[name][key][key2]
                del self.plots[name][key]
            del self.plots[name]

            ###my_canvas = my_plot["canvas"]
            ####print my_plot["histograms"]
            ###for hist in my_plot["histograms"].keys():
            ###    #my_plot["histograms"][hist].Close()
            ###    my_plot["histograms"][hist].Delete()
            ###    del my_plot["histograms"][hist]
            ###my_canvas.Close()
            ###my_canvas.Delete()
            ###del my_canvas
            ###del my_plot
            ###del self.plots[name]
        print "After clearing plots:"
        self.check_memory()

    def get_default_config(self):
        return {
            "rescale":False,
            "logy":False,
            "fit_1d_cuts":False,
            "fit_1d_cuts_list":["all", "us cut", "ds cut", "ex cut"],
            "fit_range":None,
            "draw_1d_cuts":False,
            "normalise":False,
            "background_fill":False,
            "title":True,
            "labels":{
                "title_offset":0.8,
                "title_size":0.08,
                "label_size":0.05,
            },
            "sub_dir":None,
        }

    def base_death(self):
        #print " --- [Calling Base Death] ---"
        for plot_name in sorted(self.plots.keys()):
            self.plots[plot_name]["canvas"].cd()
            plot_config = self.plots[plot_name]["config"]
            for key in plot_config.keys():
                if key not in self.get_default_config().keys():
                    raise KeyError("Failed to parse plot config "+str(key)+" in plot "+str(plot_name))
            # Note the order is important
            if plot_config["normalise"]: # normalise histograms to integral = 1
                self.normalise(plot_name)
            if plot_config["logy"]: # logy histograms axis
                self.logy(plot_name)
            if plot_config["rescale"]: # rescale histograms axis
                self.rescale(plot_name)
            if plot_config["draw_1d_cuts"]: # color according to all, us cut, ds cut then draw
                self.draw_1d_cuts(plot_name)
            if plot_config["fit_1d_cuts"]: # fit and make a text box according to all, us cut, ds cut
                self.fit_1d_cuts(plot_name)
            if plot_config["background_fill"]:
                self.set_background_fill(plot_name)
            if plot_config["title"]:
                self.set_title(plot_name)
            self.set_label_size(plot_name)
            self.plots[plot_name]["canvas"].Update()

    def set_title(self, plot_name):
        hist_dict = self.get_plot(plot_name)["histograms"]
        for hist_name in hist_dict.keys():
            hist_dict[hist_name].SetTitle(self.config_anal['name'])

    def draw_1d_cuts(self, plot_name):
        hist_dict = self.get_plot(plot_name)["histograms"]
        for key, color, draw_option in (("all", 1, ""),
                                        ("us cut", 2, "SAME"),
                                        ("ds cut", 8, "SAME"),
                                        ("ex cut", 4, "SAME"),
                                        ):
            for hist_name in hist_dict.keys():
                if key not in hist_name:
                    continue
                hist = hist_dict[hist_name]
                hist.SetLineColor(color)
                hist.Draw(draw_option)

    def logy(self, plot_name):
        self.get_plot(plot_name)["canvas"].SetLogy(True)
        self.get_plot(plot_name)["pad"].SetLogy(True)

    def rescale(self, plot_name):
        hist_dict = self.get_plot(plot_name)["histograms"]
        min_value, max_value = None, None
        for hist_name, hist in hist_dict.iteritems():
            if min_value == None:
                min_value = hist.GetMinimum()
                max_value = hist.GetMaximum()
            else:
                min_value = min(hist.GetMinimum(), min_value)
                max_value = max(hist.GetMaximum(), max_value)
        logy = self.get_plot(plot_name)["canvas"].GetLogy()
        if logy:
            min_value = max(1e-4, min_value/2.)
            max_value *= 2.
        else:
            min_value = 0.
            max_value *= 1.1
        for hist in hist_dict.values():
            hist.GetYaxis().SetRangeUser(min_value, max_value)
            hist.GetYaxis().SetRangeUser(min_value, max_value)

    def normalise(self, plot_name):
        for key, hist in self.get_plot(plot_name)["histograms"].iteritems():
            if hist.GetEntries() > 0:
                hist.Scale(1./hist.GetEntries())
        self.get_plot(plot_name)["canvas"].Update()

    def fit_1d_cuts(self, plot_name):
        self.plots[plot_name]["canvas"].cd()
        fit_range = self.plots[plot_name]["config"]["fit_range"]
        fit_name_list = self.plots[plot_name]["config"]["fit_1d_cuts_list"]
        hist_dict = self.plots[plot_name]["histograms"]
        fit_list = [None for i in range(len(fit_name_list))]
        hist_list = [None for i in range(len(fit_name_list))]
        for hist_name in sorted(hist_dict.keys()):
            for i, key in enumerate(fit_name_list):
                if key in hist_name:
                    hist_list[i] = hist_dict[hist_name]
                    fit_list[i] = utilities.utilities.fit_peak(hist_list[i], 2, "Q", "SAME", fit_range)
                    fit_list[i].SetLineColor(hist_list[i].GetLineColor())
                    xmin, xmax = hist_list[i].GetXaxis().GetXmin(), hist_list[i].GetXaxis().GetXmax()
                    hist_list[i].GetXaxis().SetRangeUser(xmin, xmax + (xmax-xmin))
        box = self.get_text_box(fit_list, hist_list)

    def set_label_size(self, plot_name):
        plot_config = self.plots[plot_name]["config"]
        hist_dict = self.plots[plot_name]["histograms"]
        for hist in hist_dict.values():
            for axis in hist.GetXaxis(), hist.GetYaxis():
                axis.SetTitleOffset(plot_config["labels"]["title_offset"])
                axis.SetTitleSize(plot_config["labels"]["title_size"])
                axis.SetLabelSize(plot_config["labels"]["label_size"])

    def set_background_fill(self, plot_name):
        canvas = self.plots[plot_name]["pad"]
        canvas.SetFrameFillColor(utilities.utilities.get_frame_fill())


    def get_text_box(self, fit_list, hist_list):
        y0 = 0.89 - 0.19*len(hist_list)
        text_box = ROOT.TPaveText(0.6, y0, 0.9, 0.89, "NDC")
        text_box.SetFillColor(0)
        text_box.SetBorderSize(0)
        text_box.SetTextSize(0.04)
        text_box.SetTextAlign(12)
        text_box.SetTextSize(0.03)

        for i, title in enumerate(["All (Black)", "US Cut (Red)", "DS Cut (Green)", "DS Apert. Cut (Blue)"]):
            if i >= len(hist_list) or i >= len(fit_list):
                continue
            hist = hist_list[i]
            fit = fit_list[i]
            if hist == None or fit == None:
                continue
            text_box.AddText(title)
            text_box.AddText("  Number:    "+str(hist.GetEntries()))
            text_box.AddText("  Mean:        "+str(round(fit.GetParameter(1), 3)))
            text_box.AddText("  Std:           "+str(round(fit.GetParameter(2), 3)))
        text_box.Draw()
        self.root_objects.append(text_box)
        return text_box


