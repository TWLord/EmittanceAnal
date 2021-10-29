import os
import json
import ROOT
import matplotlib.pyplot as plt
import copy
import numpy

#example
#"plots_2017-02-6_3-140_ABS-LH2-EMPTY_tku_base/amplitude/amplitude.json"

#sys_list = ["tkd_density_plus", "tkd_pos_plus", "tkd_rot_plus", "tkd_scale_C_plus", "tkd_scale_E1_plus", "tkd_scale_E2_plus", "tku_density_plus", "tku_pos_plus", "tku_rot_plus", "tku_scale_C_plus", "tku_scale_E1_plus", "tku_scale_E2_plus"]
#sys_list += ["tku_base_tkd_chi2_threshold", "tku_base_tkd_fiducial_radius"]

#sys_list = ["tkd_pos_plus", "tkd_rot_plus", "tkd_scale_C_plus", "tkd_scale_E1_plus", "tkd_scale_E2_plus", "tkd_density_plus"]
#sys_list = ["tku_pos_plus", "tku_scale_C_plus", "tku_scale_E1_plus", "tku_scale_E2_plus", "tku_density_plus", "tkd_scale_C_plus", "tkd_scale_E1_plus", "tkd_scale_E2_plus", "tkd_density_plus"]
###sys_list = ["tku_density_plus", "tkd_density_plus"]

#sys_list = ["tku_base_tkd_chi2_threshold", "tku_base_tkd_fiducial_radius"]
#performance_list = ["tku_base_tkd_chi2_threshold", "tku_base_tkd_fiducial_radius"]

#beam_list = ["3-140_ABS-LH2-EMPTY", "4-140_ABS-SOLID-EMPTY", "6-140_ABS-LH2-EMPTY", "10-140_ABS-LH2-EMPTY"] # new
#beam_list = ["3-140_ABS-LH2-EMPTY", ] # tmp 
#beam_list = ["4-140_ABS-SOLID-EMPTY"] # tmp 
#beam_list = ["3-140_ABS-LH2-EMPTY", "4-140_ABS-SOLID-EMPTY"] # tmp 
#beam_list = ["3-140_ABS-LH2-EMPTY", "4-140_ABS-SOLID-EMPTY", "6-140_ABS-LH2-EMPTY"] # tmp 
beam_list = ["3-140_ABS-LH2-EMPTY", "3-140_ABS-LH2", "3-140_ABS-SOLID-EMPTY", "3-140_ABS-SOLID-LiH",
             "4-140_ABS-SOLID-EMPTY", "4-140_ABS-SOLID-LiH",
             "6-140_ABS-LH2-EMPTY", "6-140_ABS-LH2", "6-140_ABS-SOLID-EMPTY", "6-140_ABS-SOLID-LiH",
             "10-140_ABS-LH2-EMPTY", "10-140_ABS-LH2", "10-140_ABS-SOLID-EMPTY", ]
             #"4-140_ABS-SOLID-EMPTY", "6-140_ABS-LH2-EMPTY", "10-140_ABS-LH2-EMPTY"] # tmp 

#beam_list = ["3-140_ABS-LH2", "4-140_ABS-SOLID-EMPTY", "6-140_ABS-LH2", "10-140_ABS-LH2"] # old (v107)

#sys_path = "/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/output/c7/v111/" 

file_path = "/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/output/combinedMC+Data/officialMC/2017-02-6_fixed_sys/v4/" # plots_Simulated_2017-02-6_10-140_ABS-LH2/
dest = "./mc_v4_plots/"

base_sys = "tku_base"


def load_json(base_path):
    fullpath = os.path.join(file_path, base_path)
    print "opening", fullpath
    fin = open(fullpath+"/amplitude/amplitude.json")
    amp_str = fin.read()
    src_amplitudes = json.loads(amp_str)
    return src_amplitudes

def pull_pdfs(obj, us_ds):
    return obj["reco"]["all_"+us_ds]["pdf"]

def pull_migration_usds(obj):
    return obj["reco"]["migration_matrix"]

def get_pdf_err_dict(base_pdf, amplitudes_dict, us_ds):
    pdf_err_dict = {}
    b_norm = sum(base_pdf)
    base_pdf_norm = [val / b_norm for val in base_pdf]
    for sys in sys_list: 
        sys_pdf = pull_pdfs(amplitudes_dict[sys], us_ds)
        s_norm = sum(sys_pdf)
        sys_pdf_norm = [val / s_norm for val in sys_pdf]
        #err_pdf = [sysbin-base_pdf[i] for i, sysbin in enumerate(sys_pdf)]
        err_pdf = [(sysbin-base_pdf_norm[i])*b_norm for i, sysbin in enumerate(sys_pdf_norm)]
        pdf_err_dict[sys] = err_pdf
    return pdf_err_dict

def calc_sys_pdf(base_pdf, sys_dict, us_ds):
    b_norm = sum(base_pdf)
    #base_pdf_norm = [val / b_norm for val in base_pdf]
    sys_pdf = pull_pdfs(sys_dict, us_ds)
    s_norm = sum(sys_pdf) 
    rescaled_sys_pdf = [val * b_norm / s_norm for val in sys_pdf]
    return rescaled_sys_pdf

def pull_correction_matrix(obj, us_ds):
    return obj["crossing_probability"]["all_"+us_ds]["migration_matrix"]

def pull_inefficiency(obj, us_ds):
    return obj["inefficiency"]["all_"+us_ds]["pdf_ratio"]

def apply_correction_matrix(pdf, migr_mat, ineff_vec):
    reco_mc_matrix = numpy.transpose(numpy.array(migr_mat))
    pdf = numpy.dot(reco_mc_matrix, pdf)
    pdf*numpy.array(ineff_vec)
    return pdf

def get_pdf_err_tot(base_pdf, amplitudes_dict, us_ds):
    pdf_err_tot = [0]*len(base_pdf)
    pdf_err_dict = get_pdf_err_dict(base_pdf, amplitudes_dict, us_ds)
    for sys, err_pdf in pdf_err_dict.items(): 
        for i, val in enumerate(err_pdf):
            pdf_err_tot[i] = (pdf_err_tot[i]**2 + val**2)**0.5 
    return pdf_err_tot
    #plt.plot(pdf_err_tot)

#def get_migration_err_dict(base_pdf, base_mat, mat_dict):
#    migration_err_dict = {}
#    for sys in sys_list:
#        sys_mat = pull_migration_usds(

def row_normalise(m_orig):
    m = copy.deepcopy(m_orig)
    for i, row in enumerate(m):
        rowsum = float(sum(row))
        for j, val in enumerate(row):
            if rowsum < 1e-5:
                if i == j:
                    m[i][j] = 0
                else:
                    m[i][j] = 0
            else:
                m[i][j] /= rowsum
    return m

def get_error_mat_tot(base_pdf_us, base_mat, mat_dict): 
    bins = len(base_mat)
    base_mat_rn = row_normalise(base_mat)
    err_mat = []
    for i in range(bins):
        err_mat.append([0]*bins)
    for sys, sys_mat in mat_dict.items():
        sys_mat_rn = row_normalise(sys_mat)
        for i in range(bins):
            for j in range(bins):
                err_mat[i][j] += (sys_mat_rn[i][j] - base_mat_rn[i][j])**2
    for i in range(bins):
        for j in range(bins):
            err_mat[i][j] = err_mat[i][j]**0.5
    return err_mat 


def get_migration_mat_errs(base_pdf_us, base_mat, mat_dict): 
    pdf_err_dict = {}
    base_mat_rn = row_normalise(base_mat)
    for sys, sys_mat in mat_dict.items():
        pdf_err = [0]*len(base_pdf_us)
        bins = len(base_mat)
        err_mat = []
        sys_mat_rn = row_normalise(sys_mat)
        for i in range(bins):
            err_mat.append([0]*bins)
        # get this err
        for i in range(bins):
            for j in range(bins):
                err_mat[i][j] += (sys_mat_rn[i][j] - base_mat_rn[i][j])**2
        # unsquare err
        for i in range(bins):
            for j in range(bins):
                err_mat[i][j] = err_mat[i][j]**0.5

        for i in range(bins):
            for j in range(bins):
                pdf_err[j] += err_mat[i][j] * base_pdf_us[i]
        pdf_err_dict[sys] = pdf_err

    return pdf_err_dict


def get_migration_mat_err_tot(base_pdf_us, base_mat, mat_dict): 
    pdf_err_tot = [0]*len(base_pdf_us)
    bins = len(base_mat)
    base_mat_rn = row_normalise(base_mat)
    err_mat = []
    for i in range(bins):
        err_mat.append([0]*bins)
    for sys, sys_mat in mat_dict.items():
        sys_mat_rn = row_normalise(sys_mat)
        for i in range(bins):
            for j in range(bins):
                err_mat[i][j] += (sys_mat_rn[i][j] - base_mat_rn[i][j])**2
        
    for i in range(bins):
        for j in range(bins):
            err_mat[i][j] = err_mat[i][j]**0.5

    for i in range(bins):
        for j in range(bins):
            pdf_err_tot[j] += err_mat[i][j] * base_pdf_us[i]

    return pdf_err_tot


def migration_matrices():
    plot_dir = os.path.join(dest, "migration_matrix_plots/")
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)
    amplitudes_dict = {}
    mat_dict = {}
    #us_ds = "upstream"
    #figs = {}
    for us_ds in ["upstream", "downstream"]:
        for beam in beam_list:
            base_path = "plots_Simulated_2017-02-6_"+beam
            base_amp = load_json(base_path)
            base_pdf = pull_pdfs(base_amp, us_ds)
            base_pdf_us = pull_pdfs(base_amp, "upstream")
            #base_mat = pull_migration_usds(base_amp)
            base_mat = pull_correction_matrix(base_amp, us_ds)

            rn_base_mat = row_normalise(base_mat)
        
            #sys_dir = "plots_2017-02-6_"+beam+"_"+sys
        
            #src_amplitudes = load_json(sys_dir)
            #amplitudes_dict[sys] = src_amplitudes
            #mat = pull_migration_usds(src_amplitudes)
            #mat_dict[sys] = pull_migration_usds(src_amplitudes)
        
            #pdf_err_dict = get_migration_mat_errs(base_pdf_us, base_mat, mat_dict)
            #pdf_err_tot = get_migration_mat_err_tot(base_pdf_us, base_mat, mat_dict)

            #err_mat_tot = get_error_mat_tot(base_pdf_us, base_mat, mat_dict)
            
            fig,ax = plt.subplots(1,3)
            fig.tight_layout()
            fig.subplots_adjust(wspace=0, hspace=0)
            fig.set_figheight(10)
            fig.set_figwidth(18)

            fig,axis = plt.subplots(1,1)
            fig.tight_layout()
            fig.subplots_adjust(wspace=0, hspace=0)
            fig.set_figheight(10)
            fig.set_figwidth(18)
            im1 = axis.imshow(base_mat)
            fig.colorbar(im1, ax=axis)
            #axis.set_title('Row-Normalised Migration Matrix')
            axis.set_title('Migration Matrix')
            axis.set_xlabel("Reconstructed amplitude")
            axis.set_ylabel("MC Truth amplitude")

            fig.savefig(plot_dir+"errormat_"+beam+"_"+us_ds+".png")
            #plt.close()



if __name__ == "__main__":
    migration_matrices()

