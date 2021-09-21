import glob
import ROOT
import os

if __name__ == "__main__":
    for a_dir in glob.glob("output/combinedMC+Data/officialMC/2017-02-6_amp/v4/compare_amplitude_mc/2017-02-6_*"):
    #for a_dir in glob.glob("output/combinedMC+Data/officialMC/2017-02-6_amp/v4_v107/compare_amplitude_mc/2017-02-6_*"):
        rfname = a_dir+"/amplitude_pdf_reco.root"
        rfile = ROOT.TFile(rfname, "READ")
        #rfile.ls()
        #for canvas in rfile.GetListOfPrimitives(): 
        a_list = rfile.GetListOfKeys()
        the_graph = None
        for key in a_list:
            old_canvas = key.ReadObj()
            #print old_canvas
            target_name = "amplitude_pdf_reco" #self.options["canvas_name"].replace(" ", "_")
            #target_name = target_name.replace("*", "").replace("?", "")
            canvas_name = (old_canvas.GetName()).replace(" ", "_")
            if target_name in canvas_name:
                for canvas_subobj in old_canvas.GetListOfPrimitives():
                    if "-pad" in canvas_subobj.GetName():
                        pad = canvas_subobj
                        print "PAD:", pad.GetName()
                    for pad_subobj in pad.GetListOfPrimitives():
                        #print "PAD subobj:", pad_subobj.GetName()
                        if "Upstream stats" in pad_subobj.GetName():
                            print "PAD subobj:"
                            the_graph = pad_subobj
        if the_graph is None:
            print "DIDNT FIND THE THING for", a_dir

                    #print thing.GetName()

                #print "OK"
                #return old_canvas

            #canvas.ls()
        #if "amplitude_pdf_reco" in 

