import math
import os
import ROOT
import json

def get_graphs(c1):
    legend = ROOT.TLegend(0.1, 0.7, 0.47, 0.9)
    for i, obj in enumerate(c1.GetListOfPrimitives()):
        if obj.GetName() == "Graph":
            n = obj.GetN()
            max_x = 0
            max_y = 0
            for i_p in range(n):
                tmpX, tmpY = ROOT.Double(0), ROOT.Double(0)
                obj.GetPoint(i_p, tmpX, tmpY)
                #x = obj.GetPointX(i_p)
                #y = obj.GetPointY(i_p)
                if tmpX > max_x:
                    max_x = tmpX
                if tmpY > max_y:
                    max_y = tmpY
            obj.SetName("Graph_"+str(i))
            max_x = round(max_x, 3)
            max_y = round(max_y, 3)
            legend.AddEntry(obj.GetName(), "Max_x: "+str(max_x)+", Max_y: "+str(max_y), "L") 
            ##print obj.GetMinimum()
            #c2 = ROOT.TCanvas('c2', 'new_canvas', 200, 10, 700, 500)
            #h2 = ROOT.TH2D('h2', 'px vs py', 100, -150, 150, 100, -150, 150)
            #c2.cd()
            ##c2.Draw()
            #h2.Draw()
            #obj.Draw("SAME")
            #raw_input("WAIT")
    legend.Draw()
    c1.Update()
    raw_input("WAIT")

def draw():
   fpath = "/data/mice/phumhf/backupOutput/combinedMC+Data/officialMC/2017-02-6-c3-OfficialMC_v3+c10_redo2/plots_2017-02-6_10-140_ABS-LH2/amplitude/phase_space"
   filename = "amplitude_phase_space_ds_px_py.root" 
   rfile = ROOT.TFile(os.path.join(fpath, filename), "read")
   c1 = rfile.Get("amplitude_phase_space_ds_px_py-34")
   c1.ls()
   c1.Draw()
   raw_input("WAIT..")
   return c1

if __name__ == "__main__":
   c1 = draw()
   get_graphs(c1)

