import ROOT
import os

ROOT.gROOT.SetBatch(True)


def plot(h_list, var):
              c3 = ROOT.TCanvas("c3", "c3", 1500, 1200)
              #mypad = ROOT.TPad(L, L, 0.2, 0.2, 0.8, 0.8)
              c3.Draw()
              #frame1.Draw()
              c3.cd()
              #mypad.Draw()
              #mypad.cd()

              colours = [ROOT.kGray, ROOT.kRed, ROOT.kBlue, ROOT.kOrange-1, ROOT.kMagenta+1]
              hnames  = ["No Corr", "Rescaled", "Recalc", "MAUS, r=0mm", "MAUS, r=100mm"]

              for i, h in enumerate(h_list):
                  h.SetFillColorAlpha(colours[i], 0.01)
                  h.SetLineColor(colours[i])
              #h1.SetFillColorAlpha(ROOT.kGray, 0.5)
              title1 = h_list[0].GetXaxis().GetTitle()
              #mypad.SetTitle(title1)
              c3.SetTitle(title1)
              h_list[0].SetTitle(title1)
              #h_list[0].GetXaxis().SetTitle()

              # normalise hist
              for i, h in enumerate(h_list):
                  nentries = h.GetEntries()
                  h.Scale(1./nentries)

                  # Sorting out stats boxes
                  h.SetStats(1)
                  h.SetName(var+'_'+hnames[i])

              #h_list[0].Draw()
              #ROOT.gPad.Update()

              # increase y axis scale to accommodate
              ymax = 0
              for i, h in enumerate(h_list):
                  #print h_list[i].GetMaximum(), ',', h_list[i+1].GetMaximum()
                  ymax = max(h_list[i].GetMaximum(), ymax) 
                  
              h_list[0].SetMaximum(ymax*1.04)

              base_h = ROOT.TH1D('base', 'base hist', h_list[0].GetNbinsX(), h_list[0].GetXaxis().GetBinLowEdge(1), h_list[0].GetXaxis().GetBinLowEdge(h_list[0].GetNbinsX()) ) 
              base_h.Fill(h_list[0].GetBinCenter(h_list[0].GetNbinsX()*100))
              base_h.SetMaximum(ymax*1.1)
              base_h.GetXaxis().SetTitle(h_list[0].GetXaxis().GetTitle())
              base_h.SetTitle("Correction Residuals")
              #base_h = ROOT.TH1F()
              #base_h.Draw()
              print "ymax", ymax
              #h_list[0].Draw()
              #ROOT.gPad.Update()

              # more stats box drawing
              for i, h in enumerate(h_list):
                  #if i == 0:
                  #  continue
                  h.Draw("SAMES")
                  ROOT.gPad.Update()


              ydelta = 0.8/len(h_list)
              stats_list = []
              for i, h in enumerate(h_list):
                  """stats = ROOT.TPaveText(.7, .8, .9, .97, "brNDC")

                  stats.AddText(h.GetName())
                  stats.AddLine(0.0, 0.73, 1.0, 0.73)
                  stats.AddText(" Entries:              {0:.5f}".format(h.GetEntries()))
                  stats.AddText(" Mean:                 {0:.5f}".format(h.GetMean()))
                  stats.AddText(" RMS:                  {0:.5f}".format(h.GetRMS()))"""

                  #stats.Draw()
                  #'ROOT.gPad.Update()
                  stats = h.FindObject("stats").Clone("stats"+str(i))
                  y_l = 0.2 + ydelta*i
                  stats.SetY1NDC(y_l)
                  stats.SetY2NDC(y_l+ydelta/2)
                  stats_list.append(stats)
                  stats.Draw()
                  ROOT.gPad.Update()

              base_h.SetStats(0)
              base_h.Draw()
              for h in h_list:
                  h.SetStats(0)
                  h.Draw("SAME")
              for stats in stats_list:
                  stats.Draw("SAME")
              
              ROOT.gPad.Update()

              #stats1.Draw()
              #stats2.Draw()
              c3.SaveAs(newdir+"/compare"+var+histname+".pdf")
              c3.SaveAs(newdir+"/compare"+var+histname+".png")
              # testing
              return


if __name__ == "__main__":
  #ROOT.gStyle.SetOptStat(0000) # doesnt work
  newdir = "./comparingAll"
  if not os.path.exists(newdir):
      os.mkdir(newdir)
  for L in ["L_canon", "L_kin", "L_field"]:
      for tracker in ["tku", "tkd"]:
          for station in ["tp", "2", "3", "4", "5"]:
              h_list = []
              object_list = []
              mystat = tracker+'_'+station
              histname = "mc_residual_"+mystat+"_"+L
              print "HIST:", histname

              for version in ["v30", "v43", "v43_recalcCorr", "v201", "v301"]:
                  myfile = ROOT.TFile(version+"/plots_Simulated_2017-02-6_6-140_ABS-LH2/ang_mom_field_plots/"+histname+".root", "read")
                  object_list.append(myfile)
                  #myfile.ls()
                  c1 = myfile.Get(histname);
                  object_list.append(c1)
                  #c1.GetListOfPrimitives().ls()
                  p1 = c1.GetPrimitive(histname+"-pad")
                  object_list.append(p1)
                  #print "\n"
                  #p1.GetListOfPrimitives().ls()
                  #print "\n"
                  plist = p1.GetListOfPrimitives()
                  print plist.GetSize()
                  for obj in plist:
                      print obj.GetName()
                      if L in obj.GetName():
                          h1 = obj
                          print "histname:", obj.GetName()
                          #h1.SetDirectory(0)
                          h1.ResetBit(ROOT.kCanDelete)
                          h_list.append(h1)
                          print "Can delete:", h1.TestBit(ROOT.kCanDelete)
                      #if "TFrame" in obj.GetName():
                      #    frame1 = obj
      
      
                  #h1 = p1.GetPrimitive("L_canon 2656")
              plot(h_list, L)
      

  for var in ["px", "py", "pz", "pt", "p", "x", "y", "z"]:
      for tracker in ["tku", "tkd"]:
          for station in ["tp", "2", "3", "4", "5"]:
              h_list = []
              object_list = []
              mystat = tracker+'_'+station
              histname = "mc_residual_"+mystat+"_"+var
              print "HIST:", histname
                
              for version in ["v30", "v43", "v43_recalcCorr", "v201", "v301"]:
                  myfile = ROOT.TFile(version+"/plots_Simulated_2017-02-6_6-140_ABS-LH2/mc_plots/"+histname+".root", "read")
                  object_list.append(myfile)
                  #myfile.ls()
                  c1 = myfile.Get(histname);
                  object_list.append(c1)
                  c1.GetListOfPrimitives().ls()
                  #p1 = c1.GetPrimitive(histname+"-pad")
                  object_list.append(p1)
                  #print "\n"
                  #p1.GetListOfPrimitives().ls()
                  #print "\n"
                  plist = c1.GetListOfPrimitives()
                  print plist.GetSize()
                  for obj in plist:
                      print obj.GetName()
                      if var in obj.GetName():
                          h1 = obj
                          print "histname:", obj.GetName()
                          #h1.SetDirectory(0)
                          h1.ResetBit(ROOT.kCanDelete)
                          h_list.append(h1)
                          print "Can delete:", h1.TestBit(ROOT.kCanDelete)
                      #if "TFrame" in obj.GetName():
                      #    frame1 = obj
      
      
                  #h1 = p1.GetPrimitive("L_canon 2656")
              plot(h_list, var)
