import glob
import os
import sys
sys.argv.append('-b')
import ROOT
import math

import xboa
from array import array

import utilities.utilities
from matplotlib import pyplot as plt

root_objects = []

def fit_1d_peak(hist, plot_name):
    #self.plots[plot_name]["canvas"].cd()
    # need to cd to canvas? can do externally?

    fit_range = None #self.plots[plot_name]["config"]["fit_range"]

    fit = utilities.utilities.fit_peak(hist, 2, "Q", "", fit_range)
    fit.SetLineColor(hist.GetLineColor())
    xmin, xmax = hist.GetXaxis().GetXmin(), hist.GetXaxis().GetXmax()
    hist.GetXaxis().SetRangeUser(xmin, xmax + (xmax-xmin))

    results = get_text_box([fit], [hist], plot_name)
    return results 

def get_text_box(fit_list, hist_list, plot_name):
    y0 = 0.89 - 0.19*len(hist_list)
    #print y0
    text_box = ROOT.TPaveText(0.6, y0, 0.9, 0.89, "NDC") 
    text_box.SetFillColor(0)
    text_box.SetBorderSize(0)
    text_box.SetTextSize(0.04)
    text_box.SetTextAlign(12)
    text_box.SetTextSize(0.03)

    number_list = []
    mean_list = []
    std_list = []

    for i, title in enumerate([plot_name]):
        if i >= len(hist_list) or i >= len(fit_list):
            continue
        hist = hist_list[i]
        fit = fit_list[i]
        if hist == None or fit == None:
            continue

        number_list.append(hist.GetEntries())
        mean_list.append(round(fit.GetParameter(1), 3))
        std_list.append(round(fit.GetParameter(2), 3))

        text_box.AddText(title)
        text_box.AddText("  Number:    "+str(hist.GetEntries()))
        text_box.AddText("  Mean:        "+str(round(fit.GetParameter(1), 3)))
        text_box.AddText("  Std:           "+str(round(fit.GetParameter(2), 3)))
    text_box.Draw()
    root_objects.append(text_box)
    return [text_box, number_list, mean_list, std_list]

def get_canvas(file_name, canvas_name):
    #print glob.glob(file_name)
    #file_name = glob.glob(file_name)[0]
    fin = ROOT.TFile(file_name, "READ")
    a_list = fin.GetListOfKeys()
    for key in a_list:
        old_canvas = key.ReadObj()
        target_name = canvas_name.replace(" ", "_")
        target_name = target_name.replace("*", "").replace("?", "")
        canvas_name = (old_canvas.GetName()).replace(" ", "_")
        if target_name in canvas_name:
            return old_canvas
    print "Keys found in file", file_name, "while searching for", canvas_name
    for key in a_list:
        print key.ReadObj().GetName(), "of type", type(key.ReadObj())
    raise KeyError("Failed to find canvas")


def get_hist(canvas, canvas_name):
    for item in canvas.GetListOfPrimitives():
        if item.GetName() == canvas_name+"-pad":
            pad = item
            pad.cd()
            for subitem in item.GetListOfPrimitives():
                if "_hist" in subitem.GetName():
                    hist = subitem
                    root_objects.append(hist)
    return hist


def get_currents(optics, dipole):
    current_list = {
                   # 2017-02-2
                   "D1":{
                        #"3-200":[0.79027247206, 0.79027247206, 0.79027247206, 0.79106274453, 0.79817519678, 0.79106274453], # old
                        #"6-200":[150,140,152,155,165,170], # old
                        #"10-200":[150,140,152,155,165,170], # old
                        "3-200":[x*0.786362*1.005*0.999973 for x in [1.001, 1.003, 1.003, 1.003, 1.003, 1.005, 1.005, 1.0, 1.0, 1.001, 1.0015, 1.0015, 1.0015]],
                        "6-200":[x*0.862115*1.005*0.999973 for x in [1.015, 1.01, 1.01, 1.0075, 1.0025, 1.0025, 1.005, 1.05, 1.01, 1.003, 1.003, 0.998, 0.998]],
                        "10-200":[x*0.908808*1.005*0.999973 for x in [1.01, 1.0075, 1.0055, 1.0035, 1.0015, 1.0015, 1.0015, 1.04, 1.02, 1.00125, 1.001, 1.0, 1.0]],
                        },
                   "D2":{
                        #"3-200":[0.4020629115, 0.4020629115, 0.40286703732, 0.40286703732, 0.40286703732, 0.40286703732], # old
                        #"6-200":[150,140,152,155,165,170], # old
                        #"10-200":[150,140,152,155,165,170], # old
                        "3-200":[x*0.400071*1.005*0.999979 for x in [1.005, 1.005, 1.005, 1.003, 1.001, 1.001, 1.005, 1.0, 1.0, 1.005, 1.005, 1.005, 1.05]],
                        "6-200":[x*0.412951*1.005*0.999979 for x in [1.025, 1.02, 1.025, 1.015, 1.015, 1.045, 1.045, 1.045, 1.045, 1.0475, 1.0525, 1.0525, 1.06]],
                        "10-200":[x*0.454908*1.005*0.999979 for x in [1.015, 1.0175, 1.0195, 1.0215, 1.0235, 1.035, 1.0375, 1.0375, 1.02, 1.0395, 1.045, 1.0475, 1.05]],
                        },
                   }[dipole][optics]
    return current_list


if __name__ == "__main__":

    indir = "~/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/output/combinedMC+Data/ownMC/"
    if not os.path.exists("dipolefitting"):
        os.mkdir("dipolefitting")

    CC = "2017-02-2"
    #mc_versions = [CC+"_v"+str(x) for x in range(1,7)]
    #mc_versions = [CC+"_v"+str(x) for x in range(7,11)]
    mc_versions = [CC+"_v"+str(x) for x in range(7,20)]

    canvas_list = ["tku_p_9_0"]
    optics_list = ["3-200", "6-200", "10-200"]
    absorber_list = ["ABS-LH2"]
    #current_list = range(1,7)*100

    for optics in optics_list:
        for ABS in absorber_list:
            for canvas_name in canvas_list:
                # Set up TGraph for results
                #c1 = ROOT.TCanvas('c1', 'Dipole Tunes', 1000, 1000, 1000, 1000)
                """c1 = ROOT.TCanvas('c1', 'Dipole Tunes', 1000, 800)
                c1.cd()
                tgraph = ROOT.TGraph2D()
                tgraph2 = ROOT.TGraph2D()
                #tgraph.SetTitle("Graph of means; D1 current; D2 current; Mean")
                #tgraph2.SetTitle("Graph of stddevs; D1 current; D2 current; Std")
                root_objects.append(tgraph)
                root_objects.append(tgraph2)"""
                true_mean = 0.
                true_stddev = 0.
                means = []
                stddevs = []
                d1_current = get_currents(optics, "D1")
                d2_current = get_currents(optics, "D2")
                print len(d1_current), "entries in D1 current values"
                print len(d2_current), "entries in D2 current values"
                # editing length
                #d1_current.pop()
                #d2_current.pop()
                test_2D_root = False
                do_matplot = False 
                if test_2D_root:
                    means = [.8, .7, .6, .5, .4, .65]*200
                    d1_current = d1_current*200
                    d2_current = d2_current*200
                    stddevs = [.8, .7, .6, .5, .4, .65]*200
                    # Fill TGraph2D
                    """for i in range(len(means)):
                        tgraph.SetPoint(i, d1_current[i], d2_current[i], means[i]) 
                        print means[i]
                        tgraph2.SetPoint(i, d1_current[i], d2_current[i], stddevs[i]) 
                        print stddevs[i]"""
                    c1 = ROOT.TCanvas('c1', 'Dipole Tunes', 200, 10, 1200, 800)
                    c1.SetFillColor(18)
                    #c1.cd()
                    pad1 = ROOT.TPad('pad1', 'Pad1', 0.05, 0.5, 0.95, 0.95, 21)
                    pad2 = ROOT.TPad('pad1', 'Pad1', 0.05, 0.05, 0.95, 0.45, 21)
                    pad1.Draw()
                    pad2.Draw()
                    pad1.cd()
                    x, y, z = array('d'), array('d'), array('d')
                    for i in range(len(means)):
                        x.append(d1_current[i])
                        y.append(d2_current[i])
                        z.append(means[i])
                        print x[i], y[i], z[i]
                    hist, tgraph2d, tgraph2d_2 = xboa.common.make_root_graph_2d("test", d1_current, "D1 current", d2_current, "D2 current", means, "Means")
                    """tgraph = ROOT.TGraph2D(len(means), x, y, z)
                    tgraph.SetMarkerSize(1.0)
                    tgraph.SetMarkerColor(38)
                    tgraph.SetMarkerStyle(21)
                    #tgraph.SetTitle("Graph of means; D1 current; D2 current; Mean")
                    #tgraph2.SetTitle("Graph of stddevs; D1 current; D2 current; Std")
                    root_objects.append(tgraph)
                    tgraph2 = ROOT.TGraph2D()
                    root_objects.append(tgraph2)
    
                    c1.cd()
                    c1.Draw()
                    #tgraph.GetZaxis().SetRangeUser(130.0, 170.0)
                    tgraph.Draw()
                    #tgraph.Draw("TRI")
                    #tgraph.Draw("SURF1")
                    #marker = ROOT.TMarker(true_mean, true_stddev, 22)
                    #marker = ROOT.TMarker(true_mean, true_stddev, 22)
                    #marker.SetMarkerSize(10)
                    #marker.SetMarkerColor(38)
                    #marker.Draw()"""
                    #c1.Draw()
                    hist.Draw()
                    tgraph2d.Draw("SURF1")
                    c1.Update()
                    pad2.cd()
                    tgraph2d_2.Draw()
                    c1.Update()

                    #c1.Modified()
                    raw_input("..Waiting..")
                    c1.SaveAs("dipolefitting/Graph_"+optics+"_"+ABS+".png")
                    sys.exit()
                if do_matplot:
                    np = 200
                    means = []
                    d1_current = []
                    d2_current = []
                    for i in range(np):
                        means.append(math.sin(i))
                        d1_current.append(math.cos(i))
                        d2_current.append(math.cos(i**2))
                    #means = [.8, .7, .6, .5, .4, .65]
                    #d1_current = d1_current*200
                    #d2_current = d2_current*200
                    #stddevs = [.8, .7, .6, .5, .4, .65]*200

                    #hist = xboa.common.make_matplot_histogram(d1_current, "D1 current", np, d2_current, "D2 current", np, "Means")
                    hist = xboa.common.make_matplot_3D(d1_current, "D1 current", d2_current, "D2 current", means, "Means")
                    xboa.common.wait_for_matplot()
                    
                    raw_input("..Waiting..")
                    sys.exit()


                # Get true value
                data_dir = os.path.join(indir, CC+"_v2", "plots_"+CC+"_"+optics+"_"+ABS, "cut_plots/")
                data_file = os.path.join(data_dir, canvas_name+".root")
                data_canv = get_canvas(data_file, canvas_name)
                data_canv.Draw()
                data_hist = get_hist(data_canv, canvas_name)
                #pad.cd()
                results = fit_1d_peak(data_hist, CC+"_"+optics+"_"+ABS)
                true_mean = results[2][0]
                true_stddev = results[3][0]
                data_canv.Update()
                data_canv.SaveAs("dipolefitting/Data_"+optics+"_"+ABS+".png")

                # Run through MC versions
                for tune in mc_versions:
                    this_dir = os.path.join(indir, tune, "plots_Simulated_"+CC+"_"+optics+"_"+ABS, "cut_plots/")
                    this_file = os.path.join(this_dir, canvas_name+".root")
                    canv = get_canvas(this_file, canvas_name)
                    canv.Draw()
                    hist = get_hist(canv, canvas_name)
                    #pad.cd()
                    results = fit_1d_peak(hist, CC+"_"+optics+"_"+ABS)
                    means.append(results[2][0])
                    stddevs.append(results[3][0])
                    canv.Update()
                    canv.SaveAs("dipolefitting/"+tune+"_"+optics+"_"+ABS+".png")

                # Make TGraph
                """c1 = ROOT.TCanvas('c1', 'Dipole Tunes', 200, 10, 1200, 800)
                c1.SetFillColor(18)
                #c1.cd()
                pad1 = ROOT.TPad('pad1', 'Pad1', 0.05, 0.5, 0.95, 0.95, 21)
                pad2 = ROOT.TPad('pad1', 'Pad1', 0.05, 0.05, 0.95, 0.45, 21)
                pad1.Draw()
                pad2.Draw()
                pad1.cd()
                x, y, z = array('d'), array('d'), array('d')
                # Fill TGraph2D
                for i in range(len(means)):
                    x.append(d1_current[i])
                    y.append(d2_current[i])
                    z.append(means[i])
                    #tgraph.SetPoint(i, d1_current[i], d2_current[i], means[i]) 
                    #print means[i]
                    #tgraph2.SetPoint(i, d1_current[i], d2_current[i], stddevs[i]) 
                    #print stddevs[i]

                hist, tgraph2d, tgraph2d_2 = xboa.common.make_root_graph_2d("test", d1_current, "D1 current", d2_current, "D2 current", means, "Means")
                #c1.Draw()
                hist.Draw()
                tgraph2d.Draw("SURF1")
                c1.Update()
                pad2.cd()
                tgraph2d_2.Draw()
                c1.Update()
                #marker = ROOT.TMarker(true_mean, true_stddev, 22)
                #marker = ROOT.TMarker(true_mean, true_stddev, 22)
                #marker.SetMarkerSize(10)
                #marker.SetMarkerColor(38)
                #marker.Draw()
                c1.Update()

                raw_input("..Waiting..")
                c1.SaveAs("dipolefitting/Graph_"+optics+"_"+ABS+".png")"""

                print len(means), "entries in mean values"
                print len(stddevs), "entries in stddev values"
                # MEANS
                hist = xboa.common.make_matplot_3D(d1_current, "D1 current", d2_current, "D2 current", means, "Means, true mean = "+str(true_mean))
                plt.savefig("dipolefitting/mpl3d_means_"+optics+"_"+ABS+".png")
                xboa.common.wait_for_matplot()

                hist = xboa.common.make_matplot_3D(d1_current, "D1 current", d2_current, "D2 current", means, "Means, true mean = "+str(true_mean), scatter=True)
                plt.savefig("dipolefitting/mpl3d_means_scatter_"+optics+"_"+ABS+".png")
                xboa.common.wait_for_matplot()

                # STDDEVs
                hist = xboa.common.make_matplot_3D(d1_current, "D1 current", d2_current, "D2 current", stddevs, "StdDevs, true std = "+str(true_stddev))
                plt.savefig("dipolefitting/mpl3d_stddevs_"+optics+"_"+ABS+".png")
                xboa.common.wait_for_matplot()

                hist = xboa.common.make_matplot_3D(d1_current, "D1 current", d2_current, "D2 current", stddevs, "StdDevs, true std = "+str(true_stddev), scatter=True)
                plt.savefig("dipolefitting/mpl3d_stddevs_"+optics+"_"+ABS+".png")
                xboa.common.wait_for_matplot()

