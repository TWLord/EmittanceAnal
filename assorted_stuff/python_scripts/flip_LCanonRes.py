import math
import os
import ROOT
import json

def function(value):
    return value

def primitivesloop(obj, name):
    for new_obj in obj.GetListOfPrimitives():
        if 'pad' in new_obj.GetName():
            primitivesloop(new_obj, name)
        #if name in new_obj.GetName():
        if new_obj.GetName() == name:
            return new_obj

def check_plots():
  fpathlist = [
               "plots_2017-02-6_3-140_ABS-LH2-EMPTY",
               "plots_2017-02-6_3-140_ABS-LH2",
               "plots_2017-02-6_3-140_ABS-SOLID-EMPTY",
               "plots_2017-02-6_3-140_ABS-SOLID-LiH",
               "plots_2017-02-6_4-140_ABS-SOLID-EMPTY",
               "plots_2017-02-6_4-140_ABS-SOLID-LiH",
               "plots_2017-02-6_6-140_ABS-LH2-EMPTY",
               "plots_2017-02-6_6-140_ABS-LH2",
               "plots_2017-02-6_6-140_ABS-SOLID-EMPTY",
               "plots_2017-02-6_6-140_ABS-SOLID-LiH",
               "plots_2017-02-6_10-140_ABS-LH2-EMPTY",
               "plots_2017-02-6_10-140_ABS-LH2",
              ]

  for fpath in fpathlist:
    fpath += "/ang_mom/L_canon_ds_stat_sys_error.root"
    #fpath = "plots_2017-02-6_6-140_ABS-LH2/ang_mom/L_canon_ds_stat_sys_error.root"
    print fpath
    myfile = ROOT.TFile(fpath, "read")
    #myfile.ls()
    c1 = myfile.Get("L_canon_ds_stat_sys_error")
    #c1.Draw()
    ##c1.ls()
    for obj in c1.GetListOfPrimitives():
        #obj = primitivesloop(obj, 'L_canon_ds_stat_sys_error_source_tkd') # 'tku_tp')
        obj = primitivesloop(obj, 'L_canon_ds_stat_sys_error_errors') # 'tku_tp')
        #obj = primitivesloop(obj, 'error_errors') # 'tku_tp')
        #print obj.GetName()
    #obj.Print()
    y = obj.GetY()

    #print "tku 1", y[4]
    #print "tkd 1", y[5]
    #print "delta", y[5] - y[4]
    print "tku 1 error", obj.GetErrorY(4)
    print "tkd 1 error", obj.GetErrorY(5)
    #raw_input("WAIT..")

    #return obj


def pull_json_errors(beam, sys):
    systematics_dir = "/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/output/c7/v107"
    #"plots_2017-02-6_3-170_ABS-LH2",
    try:
        #beam_dir = "plots_2017-02-6_"+str(emittance)+"-"+str(mom)+"_"+absorber+"_"+sys
        beam_dir = "plots_2017-02-6_"+beam+"_"+sys
        fin = open( os.path.join(systematics_dir, beam_dir, "ang_mom/ang_mom.json") )
        angstr = fin.read()
        angmom_dict = json.loads(angstr) 
        return angmom_dict
        #print ang_mom_dict["tku_tp"]
    except:
        print "Failed on", "plots_2017-02-6_"+beam+"_"+sys

def combine_systematics():
    beam_list = ["3-140_ABS-LH2", "4-140_ABS-SOLID-EMPTY", "6-140_ABS-LH2", "10-140_ABS-LH2"]
    sys_list = ["tku_base_tkd_fiducial_radius",
                "tku_density_plus",
                "tku_pos_plus",
                "tku_rot_plus",
                "tku_scale_C_plus",
                "tku_scale_E1_plus",
                "tku_scale_E2_plus",
                "tkd_density_plus",
                "tkd_pos_plus",
                "tkd_rot_plus",
                "tkd_scale_C_plus",
                "tkd_scale_E1_plus",
                "tkd_scale_E2_plus",
               ]
    combined_errors = {}
    for beam in beam_list:
        #print "Doing", beam
        for det in ["tku_tp", "tkd_tp"]:
            combined_errors[beam] = {}
            sys_dicts = {}
            combined_error = 0.
            for sys in sys_list:
                base_dict = pull_json_errors(beam, "tku_base")
                sys_dicts[sys] = pull_json_errors(beam, sys)
                L_base = base_dict[det]['ds']['L_canon']
                L_sys = sys_dicts[sys][det]['ds']['L_canon']
                err = L_base - L_sys
                combined_error = (combined_error**2 + err**2)**0.5
                #print det
                #print err
                #print combined_error
            combined_errors[beam][det] = combined_error
            print beam, det, combined_errors[beam][det]


        combined_res_error = 0.
        for sys in sys_list:
            L_res_base = base_dict['tkd_tp']['ds']['L_canon'] - base_dict['tku_tp']['ds']['L_canon']
            L_res_sys = sys_dicts[sys]['tkd_tp']['ds']['L_canon'] - sys_dicts[sys]['tku_tp']['ds']['L_canon']
            res_err = L_res_base - L_res_sys
            combined_res_error = (combined_res_error**2 + res_err**2)**0.5
            #print res_err
            #print combined_res_error

        combined_errors[beam]['res'] = combined_res_error
        print beam, 'res', combined_errors[beam]['res']

    return combined_errors
                

def load_file(beam, fpath):
    #print fpath
    fpath = os.path.join(fpath, beam, "ang_mom/L_canon_res.root") 
    #fpath = "plots_2017-02-6_6-140_ABS-LH2/ang_mom/L_canon_ds_stat_sys_error.root"
    print fpath
    myfile = ROOT.TFile(fpath, "read")
    return myfile

def get_pad(rfile):
    #rfile.Print()
    c1 = rfile.Get("L_canon_res")
    for obj in c1.GetListOfPrimitives():
        print 'top level:', obj.GetName()
        if 'pad' in obj.GetName():
            pad = obj

        #for new_obj in obj.GetListOfPrimitives():
        #    print 'sub level:', new_obj.GetName()
                #primitivesloop(new_obj, name)
    return c1, pad

def get_subobjs(rfile, name):
    c1 = rfile.Get("L_canon_res")
    for obj in c1.GetListOfPrimitives():
        print 'top level:', obj.GetName()
        for new_obj in obj.GetListOfPrimitives():
            print 'sub level:', new_obj.GetName()
            print new_obj
            if name in new_obj.GetName():
                return new_obj


def get_hist(pad, name):
    for obj in c1.GetListOfPrimitives():
        for new_obj in obj.GetListOfPrimitives():
            if new_obj.GetName() == name:
                return new_obj

def flip_bins(hist):
    nbins = hist.GetNbinsX()
    print nbins, "bins"
    b_array = []
    for i_bin in range(nbins+2):
        b_array.append(hist.GetBinContent(i_bin))

    for i_bin in range(nbins+2):
        #print i_bin,':', b_array[nbins+1-i_bin]
        hist.SetBinContent(i_bin, b_array[nbins+1-i_bin])
    return hist

def save_new_hist(c1, pad, allhist, ushist, dshist, name):
    if not os.path.exists("flipped_hists/"):
        os.mkdir("flipped_hists/")
    if not os.path.exists("flipped_hists/"+str(name)):
        os.mkdir("flipped_hists/"+str(name))
    if not os.path.exists("flipped_hists/"+str(name)+"/ang_mom"):
        os.mkdir("flipped_hists/"+str(name)+"/ang_mom")
    print "Made dirs"
    #c1.cd()
    #pad.cd()
    newname = os.path.join("flipped_hists/"+str(name)+"/ang_mom", "L_canon_res.root")
    newfile = ROOT.TFile(newname, "RECREATE")
    c1.Draw()
    allhist.Draw()
    ushist.Draw("SAME")
    dshist.Draw("SAME")
    newname = os.path.join("flipped_hists/"+str(name)+"/ang_mom", "L_canon_res.root")
    newfile = ROOT.TFile(newname, "RECREATE")
    newfile.cd()
    c1.Write()



def flip_L_canon_res():
    #fpath = "/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/output/c18/"
    #beam_list = [
    #    'plots_10243_10248_10253_10254_10255_10256_2017-02-6_3-140_ABS-LH2-EMPTY',
    #    'plots_10245_10247_10249_2017-02-6_6-140_ABS-LH2-EMPTY',
    #    'plots_10246_10250_10251_10252_10257_10258_10259_10260_2017-02-6_10-140_ABS-LH2-EMPTY',
    #    'plots_9883_9888_9893_9897_9903_9906_2017-02-6_3-140_ABS-LH2',
    #    'plots_9884_9885_9889_9894_9898_9904_9905_2017-02-6_6-140_ABS-LH2',
    #    'plots_9886_9887_9890_9891_9892_9895_9896_9899_9900_9901_9902_2017-02-6_10-140_ABS-LH2',
    #    'plots_10313_10314_10323_10327_10333_2017-02-6_3-140_ABS-SOLID-EMPTY',
    #    'plots_10315_10317_10322_10328_10334_2017-02-6_4-140_ABS-SOLID-EMPTY',
    #    'plots_10318_10324_10329_10335_2017-02-6_6-140_ABS-SOLID-EMPTY',
    #    'plots_10319_10321_10325_10326_10330_10331_10332_2017-02-6_10-140_ABS-SOLID-EMPTY',
    #    'plots_10509_10510_2017-02-6_6-140_ABS-SOLID-LiH',
    #    'plots_10504_10505_10506_10507_2017-02-6_4-140_ABS-SOLID-LiH',
    #    'plots_10508_10511_2017-02-6_3-140_ABS-SOLID-LiH',
    #    ##'plots_9911_2017-02-6_3-170_ABS-LH2',
    #    ##'plots_10262_10266_10267_10275_2017-02-6_3-200_ABS-LH2-EMPTY',
    #    ##'plots_10261_10264_10265_10270_10271_10272_10273_10274_2017-02-6_3-240_ABS-LH2-EMPTY',
    #    ##'plots_9910_9915_2017-02-6_3-200_ABS-LH2',
    #    ##'plots_10268_10269_2017-02-6_3-170_ABS-LH2-EMPTY',
    #    ##'plots_9907_9908_9909_9912_9913_9914_2017-02-6_3-240_ABS-LH2',
    #]

    fpath = "/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/output/c19/v3/"
    beam_list = [
        'plots_Simulated_2017-02-6_3-140_ABS-LH2-EMPTY',
        'plots_Simulated_2017-02-6_6-140_ABS-LH2-EMPTY',
        'plots_Simulated_2017-02-6_10-140_ABS-LH2-EMPTY',
        'plots_Simulated_2017-02-6_3-140_ABS-LH2',
        'plots_Simulated_2017-02-6_6-140_ABS-LH2',
        'plots_Simulated_2017-02-6_10-140_ABS-LH2',
        'plots_Simulated_2017-02-6_3-140_ABS-SOLID-EMPTY',
        'plots_Simulated_2017-02-6_4-140_ABS-SOLID-EMPTY',
        'plots_Simulated_2017-02-6_6-140_ABS-SOLID-EMPTY',
        'plots_Simulated_2017-02-6_10-140_ABS-SOLID-EMPTY',
        'plots_Simulated_2017-02-6_6-140_ABS-SOLID-LiH',
        'plots_Simulated_2017-02-6_4-140_ABS-SOLID-LiH',
        'plots_Simulated_2017-02-6_3-140_ABS-SOLID-LiH',
        ##'plots_9911_2017-02-6_3-170_ABS-LH2',
        ##'plots_10262_10266_10267_10275_2017-02-6_3-200_ABS-LH2-EMPTY',
        ##'plots_10261_10264_10265_10270_10271_10272_10273_10274_2017-02-6_3-240_ABS-LH2-EMPTY',
        ##'plots_9910_9915_2017-02-6_3-200_ABS-LH2',
        ##'plots_10268_10269_2017-02-6_3-170_ABS-LH2-EMPTY',
        ##'plots_9907_9908_9909_9912_9913_9914_2017-02-6_3-240_ABS-LH2',
    ]


    # "plots_10313_10314_10323_10327_10333_2017-02-6_3-140_ABS-SOLID-EMPTY/ang_mom/L_canon_res.root"
    for beam in beam_list:
        try:
            # need to add..
            rfile = load_file(beam, fpath)
            c1, pad = get_pad(rfile)
            #hist = get_hist(pad, "L_canon_res ds")
            allhist = get_subobjs(rfile, "L_canon_res all")
            ushist = get_subobjs(rfile, "L_canon_res us cut")
            dshist = get_subobjs(rfile, "L_canon_res ds cut")
            pad.cd()
            flip_bins(allhist)
            flip_bins(ushist)
            flip_bins(dshist)
            save_new_hist(c1, pad, allhist, ushist, dshist, beam)
            #save_new_hist()
        except Exception as e:
            print "Failed on", beam
            print e



if __name__ == "__main__":

    #check_plots()
    #pull_json_errors("tku_base")

    flip_L_canon_res()

    #combined_errors = combine_systematics()
  
