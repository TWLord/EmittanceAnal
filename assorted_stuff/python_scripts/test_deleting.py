import os
import ROOT
import xboa
import xboa.common
import numpy
import time
import sys

ROOT.gROOT.SetBatch(True)

class HistogramHolder(object):
    def __init__(self):
        self.plots = {}

    def check_memory(self):
        #print ''.join(os.popen('free -t -m').readlines())
        #print ''.join(os.popen('ps -m -o %cpu,%mem,command').readlines())
        print ''.join(os.popen('ps aux | grep phumhf | grep python').readlines())

    def get_plot(self, name):
        if name not in self.plots:
            new_plot = {}
            #new_plot["config"] = self.get_default_config()
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

    def generate_data(self):
        s = numpy.random.normal(0,1.0, 1000)
        return s

    def make_root_histogram(self, name, subname):
        my_plot = self.get_plot(name)
        s = self.generate_data()
        #hist = ROOT.TH1F(name, subname, 100, -5, 5)
        #for event in s:
        #    hist.Fill(event)
        hist = xboa.common.make_root_histogram(subname, s, 'x', 100)
        my_plot["histograms"][subname] = hist
        return hist

    def make_root_graph(self, name, subname):
        my_plot = self.get_plot(name)
        s = self.generate_data()
        #hist = ROOT.TH1F(name, subname, 100, -5, 5)
        #for event in s:
        #    hist.Fill(event)
        #print name
        hist, graph = xboa.common.make_root_graph(subname, s, 'x', s, 'y')
        my_plot["graphs"][subname] = graph
        my_plot["histograms"][subname] = hist
        return hist

    def min_del_plots(self):
        print 'Clearing', len(self.plots.keys()), 'plots'
        self.check_memory()
        for name, my_plot in self.plots.items():
            #for histname in self.plots[name]['histograms'].keys():
            #    #ROOT.SetOwnership(self.plots[name]['histograms'][histname], True)
            #    #self.plots[name]['histograms'][histname].GetListOfFunctions().Delete()
            #    self.plots[name]['histograms'][histname].Delete()
            #    del self.plots[name]['histograms'][histname]
            ##ROOT.SetOwnership(self.plots[name]['pad'], True)
            #self.plots[name]['pad'].Close()
            #self.plots[name]['pad'].Delete()
            #obj = self.plots[name]["canvas"]
            ##ROOT.SetOwnership(obj, True)
            #obj.IsA().Destructor( obj )
            #for key, item in my_plot.items():
            #    if type(item) == dict:
            #        for key2, item2 in item.items():
            #            obj = self.plots[name][key][key2]
            #            #ROOT.SetOwnership(obj, True)
            #            obj.IsA().Destructor( obj )
            #            del self.plots[name][key][key2]
            #    #print '\n', key
            #    #print self.plots[name][key]
            #    del self.plots[name][key]
            #    if key in self.plots[name]:
            #        print "Didnt delete", key, ".. Still here.." 

            del self.plots[name]

        print "After clearing plots:"
        self.check_memory()

    def mid_del_plots(self):
        print 'Clearing', len(self.plots.keys()), 'plots'
        self.check_memory()
        for name, my_plot in self.plots.items():
            #for histname in self.plots[name]['histograms'].keys():
                #ROOT.SetOwnership(self.plots[name]['histograms'][histname], True)
                #self.plots[name]['histograms'][histname].GetListOfFunctions().Delete()
                #self.plots[name]['histograms'][histname].Delete()
                #del self.plots[name]['histograms'][histname]
            #self.plots[name]['pad'].Close()
            #self.plots[name]['pad'].Delete()
            obj = self.plots[name]["canvas"]
            obj.IsA().Destructor( obj )
            for key, item in my_plot.items():
                if type(item) == dict:
                    for key2, item2 in item.items():
                        #print key, item, key2, item2
                        obj = self.plots[name][key][key2]
                        #ROOT.SetOwnership(obj, True)
                        obj.IsA().Destructor( obj )
                        del self.plots[name][key][key2]
                #print '\n', key
                #print self.plots[name][key]
                del self.plots[name][key]
                if key in self.plots[name]:
                    print "Didnt delete", key, ".. Still here.." 

            del self.plots[name]

        print "After clearing plots:"
        self.check_memory()


    def del_plots(self):
        print 'Clearing', len(self.plots.keys()), 'plots'
        self.check_memory()
        for name, my_plot in self.plots.items():
            for histname in self.plots[name]['histograms'].keys():
                #ROOT.SetOwnership(self.plots[name]['histograms'][histname].GetListOfFunctions(), True)
                ROOT.SetOwnership(self.plots[name]['histograms'][histname], True)
                self.plots[name]['histograms'][histname].GetListOfFunctions().Delete()
                self.plots[name]['histograms'][histname].Delete()
                del self.plots[name]['histograms'][histname]
            ROOT.SetOwnership(self.plots[name]['pad'], True)
            self.plots[name]['pad'].Close()
            self.plots[name]['pad'].Delete()
            obj = self.plots[name]["canvas"]
            ROOT.SetOwnership(obj, True)
            obj.IsA().Destructor( obj )
            for key, item in my_plot.items():
                if type(item) == dict:
                    for key2, item2 in item.items():
                        obj = self.plots[name][key][key2]
                        ROOT.SetOwnership(obj, True)
                        obj.IsA().Destructor( obj )
                        del self.plots[name][key][key2]
                #print '\n', key
                #print self.plots[name][key]
                del self.plots[name][key]
                if key in self.plots[name]:
                    print "Didnt delete", key, ".. Still here.." 

            #print self.plots[name]
            #del my_plot
            del self.plots[name]
            ##my_canvas = my_plot["canvas"]
            ###print my_plot["histograms"]
            ##for hist in my_plot["histograms"].keys():
            ##    #my_plot["histograms"][hist].Close()
            ##    #my_plot["histograms"][hist].Delete()
            ##    histo = my_plot["histograms"][hist]
            ##    histo.IsA().Destructor( histo )
            ##    del my_plot["histograms"][hist]
            ##my_canvas.Close()
            ###my_canvas.Delete()
            ##my_canvas.IsA().Destructor( my_canvas )
            ##del my_canvas
            ##del my_plot
            ##del self.plots[name]

        print "After clearing plots:"
        self.check_memory()

    def plots_loop(self, num1, num2):
        for name in [str(x) for x in range(num1, num2)]:
            #hist = self.make_root_histogram(name, name)
            hist = self.make_root_graph(name, name)
            hist.Draw()

if __name__ == "__main__":
    HH = HistogramHolder()
    print "Before doing much of anything.."
    HH.check_memory()


    for i in range(3):
        HH.plots_loop(0, 1000)
        print "loop", i
        #HH.del_plots()
        HH.mid_del_plots()
        #HH.min_del_plots()
        #HH.check_memory()


    sys.exit()



    # Works better for TGraphs... 

    HH.plots_loop(0, 1000)
    #time.sleep(10)

    print "After 1k"
    HH.check_memory()

    #HH.min_del_plots()
    #HH.mid_del_plots()
    HH.del_plots()


    HH.plots_loop(0, 1000)

    print "After 2k"
    HH.check_memory()

    #HH.min_del_plots()
    #HH.mid_del_plots()
    HH.del_plots()

    HH.plots_loop(0, 1000)

    print "After 3k"
    HH.check_memory()

    #HH.min_del_plots()
    #HH.mid_del_plots()
    HH.del_plots()

    print "After del.."
    HH.check_memory()


    # works well plotting hists..

    ###HH.plots_loop(0, 10000)

    ####HH.min_del_plots()
    ###HH.mid_del_plots()
    ####HH.del_plots()


    ###print "After 10k"
    ###HH.check_memory()

    ###HH.plots_loop(10001, 20000)
    ####HH.min_del_plots()
    ###HH.del_plots()

    ###print "After 20k"
    ###HH.check_memory()

    ###HH.plots_loop(20001, 30000)
    ####HH.min_del_plots()
    ###HH.del_plots()

    ###print "After 30k"
    ###HH.check_memory()

    ###HH.plots_loop(30001, 40000)
    ####HH.min_del_plots()
    ###HH.del_plots()

    ###print "After 40k"
    ###HH.check_memory()

    """for name in [str(x) for x in range(10000)]:
        #HH.get_plot(name)
        hist = HH.make_root_histogram(name, name)
        hist.Draw()
        #raw_input("WAIT")"""

