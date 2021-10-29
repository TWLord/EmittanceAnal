import os
import sys 
sys.argv.append( '-b-' )
import ROOT

fpath="./output/combinedMC+Data/officialMC/2017-02-6_AngMom_v111/compare_ang_mom/"
dest = os.path.join(fpath, "blanked_plots")
print "DEST:", dest
#raw_input("...")

if not os.path.exists(dest):
    os.makedirs(dest)

#replace_list = ["L_canon_ds"]
replace_list = ["L_canon_ds", "L_field_ds", "L_kin_ds",
                "L_canon_ds_stat_sys_error", "L_field_ds_stat_sys_error", "L_kin_ds_stat_sys_error",
                "l_twiddle_3_ds", "beta_4d_ds"
               ]

for fname in replace_list:
    fullname = os.path.join(fpath, fname+".root")
    rfile = ROOT.TFile(fullname, "READ")
    rfile.ls()
    c1 = rfile.Get(fname+"_c1_")
    c1.Draw()
    for obj in c1.GetListOfPrimitives(): 
        if obj.GetName() == fname+"_c1__1":
            pad = obj
            print obj.GetName()
        #print obj.IsA()
        #print obj.GetName()
    pad.ls()
    pad.cd()
    index_list = range(1,17)
    blank_list = [2, 6, 16]
    redo_list = [12]
    for i in index_list:
        if i not in blank_list:
            continue
        for obj in pad.GetListOfPrimitives(): 
            print obj.GetName()
            if obj.GetName() == fname+"_c1__1_"+str(i):
                subpad = obj
        print "SUBPAD"
        print subpad.ls()
        for obj in subpad.GetListOfPrimitives():
            if obj.InheritsFrom(ROOT.TH2D.Class()):
                print "LAA"
                print obj.GetName()
                hist = obj
        subpad.cd()
        print hist.GetXaxis().GetLabelSize()
        subpad.SetFillStyle(4000)
        #subpad.SetFrameFillStyle(4000)
        #subpad.SetFillStyle(0)
        print i, hist.GetLabelOffset()
        fake_hist = ROOT.TH2D()
        fake_graph = ROOT.TGraph()
        #fake_hist.Draw("AXIS")
        fake_hist.Draw("")
        fake_graph.Draw("")
        #hist.Draw("AXIS")
        print "overwriting pad", i
        if 11 < i < 17:
            subpad.Clear()
            subpad.Close()
        c1.Update()
    for i in redo_list:
        for obj in pad.GetListOfPrimitives(): 
            print obj.GetName()
            if obj.GetName() == fname+"_c1__1_"+str(i):
                subpad = obj
        for obj in subpad.GetListOfPrimitives():
            if obj.InheritsFrom(ROOT.TH2D.Class()):
                print "LAA"
                print obj.GetName()
                hist = obj
        print hist.GetXaxis().GetLabelOffset()
        print hist.GetXaxis().GetLabelSize()
        subpad.cd()
        subpad.Draw()
        subpad.Update()
    c1.Update()

    c1.Print(dest+"/"+fname+"_blanked.pdf")
    #c1.Print(dest+"/"+fname+"_blanked.eps")
    c1.Print(dest+"/"+fname+"_blanked.png")
    #raw_input("WAIT")
