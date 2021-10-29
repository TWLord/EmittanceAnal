import os
import json
import ROOT
import matplotlib.pyplot as plt
import copy
import numpy

#example
#"plots_2017-02-6_3-140_ABS-LH2-EMPTY_tku_base/amplitude/amplitude.json"

sys_list = ["tkd_density_plus", "tkd_pos_plus", "tkd_rot_plus", "tkd_scale_C_plus", "tkd_scale_E1_plus", "tkd_scale_E2_plus", "tku_density_plus", "tku_pos_plus", "tku_rot_plus", "tku_scale_C_plus", "tku_scale_E1_plus", "tku_scale_E2_plus"]
#sys_list += ["tku_base_tkd_chi2_threshold", "tku_base_tkd_fiducial_radius"]

#sys_list = ["tkd_pos_plus", "tkd_rot_plus", "tkd_scale_C_plus", "tkd_scale_E1_plus", "tkd_scale_E2_plus", "tkd_density_plus"]
#sys_list = ["tku_pos_plus", "tku_scale_C_plus", "tku_scale_E1_plus", "tku_scale_E2_plus", "tku_density_plus", "tkd_scale_C_plus", "tkd_scale_E1_plus", "tkd_scale_E2_plus", "tkd_density_plus"]
###sys_list = ["tku_density_plus", "tkd_density_plus"]

#sys_list = ["tku_base_tkd_chi2_threshold", "tku_base_tkd_fiducial_radius"]
performance_list = ["tku_base_tkd_chi2_threshold", "tku_base_tkd_fiducial_radius"]

#beam_list = ["3-140_ABS-LH2-EMPTY", "4-140_ABS-SOLID-EMPTY", "6-140_ABS-LH2-EMPTY", "10-140_ABS-LH2-EMPTY"] # new
#beam_list = ["3-140_ABS-LH2-EMPTY", ] # tmp 
#beam_list = ["4-140_ABS-SOLID-EMPTY"] # tmp 
#beam_list = ["3-140_ABS-LH2-EMPTY", "4-140_ABS-SOLID-EMPTY"] # tmp 
#beam_list = ["3-140_ABS-LH2-EMPTY", "4-140_ABS-SOLID-EMPTY", "6-140_ABS-LH2-EMPTY"] # tmp 
beam_list = ["3-140_ABS-LH2-EMPTY", "4-140_ABS-SOLID-EMPTY", "6-140_ABS-LH2-EMPTY", "10-140_ABS-LH2-EMPTY"] # tmp 

#beam_list = ["3-140_ABS-LH2", "4-140_ABS-SOLID-EMPTY", "6-140_ABS-LH2", "10-140_ABS-LH2"] # old (v107)

#sys_path = "/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/output/c7/v107/" 
#sys_path = "/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/output/c7/v109/" 
#dest = "./v109_plots/"
#sys_path = "/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/output/c7/v110/" 
sys_path = "/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/output/c7/v111/" 
dest = "./v111_plots/"
#sys_path = "/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/output/c7/v333/" 
#dest = "./v333_plots/"
#sys_path = "/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/output/c7/v575/" 
#dest = "./v575_plots/"

#sys_path = "/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/output/c7/v575/v575_test/" 
#dest = "./v575_test1_plots/"
#sys_path = "/home/phumhf/MICE/maus--versions/MAUSv3.3.0/bin/user/first-observation-paper-scripts/output/c7/v575/v575_test2/" 
#dest = "./v575_test2_plots/"


base_sys = "tku_base"
#base_sys = "tku_scale_E2_plus"


def load_json(base_path):
    fullpath = os.path.join(sys_path, base_path)
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

def detector_errors():
    """ 
    Gets pdf distributionss from each sys,
    only using uncorrected pdfs,
    and renormalises wrt nominal pdf. 
    Then plots difference and ratios
    """
    print 'dest:', dest
    plot_dir = os.path.join(dest, "detector_error_plots1/")
    print plot_dir
    #if os.path.exists(plot_dir):
    #    os.rmdir(plot_dir)
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)
    amplitudes_dict = {}
    #us_ds = "upstream"
    #figs = {}
    for us_ds in ["upstream", "downstream"]:
        usds_col = {'upstream':'red',
                    'downstream':'green',
                   }[us_ds]
        for beam in beam_list:
            #base_path = "plots_2017-02-6_"+beam+"_tku_base"
            #base_path = "plots_2017-02-6_"+beam+"_tku_scale_E1_plus"
            base_path = "plots_2017-02-6_"+beam+"_"+base_sys
            base_amp = load_json(base_path)
            base_pdf = pull_pdfs(base_amp, us_ds)
        
            #for sys in ["tku_pos_plus", "tku_rot_plus"]:
            for sys in sys_list:
                sys_dir = "plots_2017-02-6_"+beam+"_"+sys
        
                #fin = open(sys_dir+"/amplitude.json")
                #amp_str = fin.read()
                #src_amplitudes = json.loads(amp_str)
                #src_amplitudes["source"]
        
                src_amplitudes = load_json(sys_dir)
                amplitudes_dict[sys] = src_amplitudes
                #print src_amplitudes
        
            #plt.plot(base_pdf)    
            #for sys in sys_list: 
            #    sys_pdf = pull_pdfs(amplitudes_dict[sys], "upstream")
            #    plt.plot(sys_pdf)
        
            pdf_err_dict = get_pdf_err_dict(base_pdf, amplitudes_dict, us_ds)
            pdf_err_tot = get_pdf_err_tot(base_pdf, amplitudes_dict, us_ds)
        
            #if beam in figs.keys(): 
            #    fig = figs[beam]['fig']
            #    ax  = figs[beam]['ax']
            #else:
            #    fig,ax = plt.subplots(1,3)
            #    fig.tight_layout()
            #    fig.subplots_adjust(wspace=0, hspace=0)
            #    fig.set_figheight(10)
            #    fig.set_figwidth(18)
            #    figs[beam] = {}
            #    figs[beam]['fig'] = fig
            #    figs[beam]['ax']  = ax
            fig,ax = plt.subplots(1,3)
            fig.tight_layout()
            fig.subplots_adjust(wspace=0, hspace=0)
            fig.set_figheight(10)
            fig.set_figwidth(18)
    
            ax[0].plot(range(len(base_pdf)), base_pdf, 'o', color=usds_col)
            ax[0].set_title("Uncorr Base PDF")
            #for sys, pdf_err in sorted(pdf_err_dict.items(), key=lambda x:x[0]):
            for sys in sys_list:
                pdf_err = pdf_err_dict[sys]
                if "tkd" in sys:
                    alpha=0.5
                    lstyle='--'
                else:
                    alpha=0.5
                    lstyle=':'
                ax[1].plot(pdf_err, label=sys, alpha=alpha, linestyle=lstyle)
            ax[1].plot(pdf_err_tot, label='Combined')
            ax[1].set_title("Sys PDF - Ref PDF")
            ax[1].legend()
            for sys in sys_list:
                sys_ratio_err = [0]*len(base_pdf)
                #sys_pdf = pull_pdfs(amplitudes_dict[sys], us_ds)
                sys_pdf = calc_sys_pdf(base_pdf, amplitudes_dict[sys], us_ds)
                for i, val in enumerate(sys_pdf):
                    if base_pdf[i] == 0:
                        sys_ratio_err[i] = 0
                    else:
                        sys_ratio_err[i] = val / base_pdf[i]
                if "tkd" in sys:
                    alpha=0.5
                    lstyle='--'
                else:
                    alpha=0.5
                    lstyle=':'
                ax[2].plot(sys_ratio_err, label=sys, alpha=alpha, linestyle=lstyle)
                ax[2].set_title("Sys PDF / Base PDF")
                ax[2].set_ylim(0.8, 1.2)
            base_min = [val - pdf_err_tot[i] for i, val in enumerate(base_pdf)]
            base_max = [val + pdf_err_tot[i] for i, val in enumerate(base_pdf)]
            ax[0].fill_between(range(len(base_pdf)), base_min, base_max, alpha=0.2, edgecolor=usds_col, facecolor=usds_col)
        
            fig.savefig(plot_dir+"sys_errors_"+us_ds+"_"+beam+".png")

def detector_errors2():
    """
    Gets correction from each sys
    and applies each to nominal pdf.
    Then plots differences and ratios
    """
    print 'dest:', dest
    plot_dir = os.path.join(dest, "detector_error_plots2/")
    print plot_dir
    #if os.path.exists(plot_dir):
    #    os.rmdir(plot_dir)
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)
    amplitudes_dict = {}
    #us_ds = "upstream"
    #figs = {}
    for us_ds in ["upstream", "downstream"]:
        usds_col = {'upstream':'red',
                    'downstream':'green',
                   }[us_ds]
        for beam in beam_list:
            #base_path = "plots_2017-02-6_"+beam+"_tku_base"
            #base_path = "plots_2017-02-6_"+beam+"_tku_scale_E1_plus"
            base_path = "plots_2017-02-6_"+beam+"_"+base_sys
            base_amp = load_json(base_path)
            base_pdf = pull_pdfs(base_amp, us_ds)
            base_migrations = pull_correction_matrix(base_amp, us_ds)
            base_ineff = pull_inefficiency(base_amp, us_ds)
            base_corr_pdf = apply_correction_matrix(base_pdf, base_migrations, base_ineff)

        
            sys_pdf_dict = {}
            sys_err_dict = {}
            #for sys in ["tku_pos_plus", "tku_rot_plus"]:
            for sys in sys_list:
                sys_dir = "plots_2017-02-6_"+beam+"_"+sys
        
                #fin = open(sys_dir+"/amplitude.json")
                #amp_str = fin.read()
                #src_amplitudes = json.loads(amp_str)
                #src_amplitudes["source"]
        
                src_amplitudes = load_json(sys_dir)
                amplitudes_dict[sys] = src_amplitudes
                sys_migrations = pull_correction_matrix(src_amplitudes, us_ds)
                sys_ineff = pull_inefficiency(src_amplitudes, us_ds)
                sys_corr_pdf = apply_correction_matrix(base_pdf, sys_migrations, sys_ineff)
                sys_pdf_dict[sys] = sys_corr_pdf
                sys_err_dict[sys] = (base_corr_pdf - sys_corr_pdf)
            sys_err_tot = 0
            for sys in sys_list:
                sys_err_tot += sys_err_dict[sys]**2
            sys_err_tot = sys_err_tot**0.5
        
            fig,ax = plt.subplots(1,3)
            fig.tight_layout()
            fig.subplots_adjust(wspace=0, hspace=0)
            fig.set_figheight(10)
            fig.set_figwidth(18)
    
            ax[0].plot(range(len(base_corr_pdf)), base_corr_pdf, 'o', color=usds_col)
            ax[0].set_title("Base PDF")
            #for sys, pdf_err in sorted(sys_err_dict.items(), key=lambda x:x[0]):
            for sys in sys_list:
                pdf_err = sys_err_dict[sys]
                if "tkd" in sys:
                    alpha=0.5
                    lstyle='--'
                else:
                    alpha=0.5
                    lstyle=':'
                ax[1].plot(pdf_err, label=sys, alpha=alpha, linestyle=lstyle)
            ax[1].plot(sys_err_tot, label='Combined')
            ax[1].set_title("Sys PDF - Ref PDF")
            ax[1].legend()
            for sys in sys_list:
                sys_ratio_err = [0]*len(base_corr_pdf)
                sys_corr_pdf = sys_pdf_dict[sys]
                for i, val in enumerate(sys_corr_pdf):
                    if base_corr_pdf[i] == 0:
                        sys_ratio_err[i] = 0
                    else:
                        sys_ratio_err[i] = val / base_corr_pdf[i]
                if "tkd" in sys:
                    alpha=0.5
                    lstyle='--'
                else:
                    alpha=0.5
                    lstyle=':'
                ax[2].plot(sys_ratio_err, label=sys, alpha=alpha, linestyle=lstyle)
                ax[2].set_title("Sys PDF / Base PDF")
                #ax[2].set_ylim(0.8, 1.2)
                ax[2].set_ylim(0.95, 1.05)
            base_min = [val - sys_err_tot[i] for i, val in enumerate(base_pdf)]
            base_max = [val + sys_err_tot[i] for i, val in enumerate(base_pdf)]
            ax[0].fill_between(range(len(base_pdf)), base_min, base_max, alpha=0.2, edgecolor=usds_col, facecolor=usds_col)
        
            fig.savefig(plot_dir+"sys_errors_"+us_ds+"_"+beam+".png")


        
def performance_errors():
    plot_dir = os.path.join(dest, "performance_plots/")
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)
    amplitudes_dict = {}
    mat_dict = {}
    #us_ds = "upstream"
    #figs = {}
    for us_ds in ["downstream"]:
        usds_col = {'upstream':'red',
                    'downstream':'green',
                   }[us_ds]
        for beam in beam_list:
            #base_path = "plots_2017-02-6_"+beam+"_tku_base"
            #base_path = "plots_2017-02-6_"+beam+"_tku_scale_E1_plus"
            base_path = "plots_2017-02-6_"+beam+"_"+base_sys
            base_amp = load_json(base_path)
            base_pdf = pull_pdfs(base_amp, us_ds)
            base_pdf_us = pull_pdfs(base_amp, "upstream")
            base_mat = pull_migration_usds(base_amp)
            #print migration_mat
        
            #for sys in sys_list:
            for sys in performance_list:
                sys_dir = "plots_2017-02-6_"+beam+"_"+sys
        
                #fin = open(sys_dir+"/amplitude.json")
                #amp_str = fin.read()
                #src_amplitudes = json.loads(amp_str)
                #src_amplitudes["source"]
        
                src_amplitudes = load_json(sys_dir)
                amplitudes_dict[sys] = src_amplitudes
                mat_dict[sys] = pull_migration_usds(src_amplitudes)
                #print src_amplitudes['reco'].keys()
        
            #plt.plot(base_pdf)    
            #for sys in sys_list: 
            #    sys_pdf = pull_pdfs(amplitudes_dict[sys], "upstream")
            #    plt.plot(sys_pdf)
        
            #pdf_err_dict = get_pdf_err_dict(base_pdf, amplitudes_dict, us_ds)
            #pdf_err_tot = get_pdf_err_tot(base_pdf, amplitudes_dict, us_ds)
        
            pdf_err_dict = get_migration_mat_errs(base_pdf_us, base_mat, mat_dict)
            pdf_err_tot = get_migration_mat_err_tot(base_pdf_us, base_mat, mat_dict)

            err_mat_tot = get_error_mat_tot(base_pdf_us, base_mat, mat_dict)
            
            #(base_pdf, migration_mat, amplitudes_dict, us_ds)
          

            #if beam in figs.keys(): 
            #    fig = figs[beam]['fig']
            #    ax  = figs[beam]['ax']
            #else:
            #    fig,ax = plt.subplots(1,3)
            #    fig.tight_layout()
            #    fig.subplots_adjust(wspace=0, hspace=0)
            #    fig.set_figheight(10)
            #    fig.set_figwidth(18)
            #    figs[beam] = {}
            #    figs[beam]['fig'] = fig
            #    figs[beam]['ax']  = ax
            fig,ax = plt.subplots(1,3)
            fig.tight_layout()
            fig.subplots_adjust(wspace=0, hspace=0)
            fig.set_figheight(10)
            fig.set_figwidth(18)
    
            ax[0].plot(range(len(base_pdf)), base_pdf, 'o', color=usds_col)
            ax[0].set_title("Base PDF")
            for sys, pdf_err in sorted(pdf_err_dict.items(), key=lambda x:x[0]):
                if "tkd" in sys:
                    alpha=0.5
                    lstyle='--'
                else:
                    alpha=0.5
                    lstyle=':'
                ax[1].plot(pdf_err, label=sys, alpha=alpha, linestyle=lstyle)
            ax[1].plot(pdf_err_tot, label='Combined')
            ax[1].set_title("Sys Migration Errors on PDF")
            ax[1].legend()
            #for sys in sys_list:
            for sys in performance_list:
                sys_ratio_err = [0]*len(base_pdf)
                sys_pdf = pull_pdfs(amplitudes_dict[sys], us_ds)
                for i, val in enumerate(sys_pdf):
                    if base_pdf[i] == 0:
                        sys_ratio_err[i] = 0
                    else:
                        sys_ratio_err[i] = val / base_pdf[i]
                if "tkd" in sys:
                    alpha=1.#0.5
                    lstyle='--'
                else:
                    alpha=1.#0.5
                    lstyle=':'
                ax[2].plot(sys_ratio_err, label=sys, alpha=alpha, linestyle=lstyle)
                ax[2].set_title("Sys PDF / Base PDF")
            base_min = [val - pdf_err_tot[i] for i, val in enumerate(base_pdf)]
            base_max = [val + pdf_err_tot[i] for i, val in enumerate(base_pdf)]
            ax[0].fill_between(range(len(base_pdf)), base_min, base_max, alpha=0.2, edgecolor=usds_col, facecolor=usds_col)
        
            fig.savefig(plot_dir+"sys_errors_"+us_ds+"_"+beam+".png")
            plt.close()

            fig,axis = plt.subplots(1,1)
            fig.tight_layout()
            fig.subplots_adjust(wspace=0, hspace=0)
            fig.set_figheight(10)
            fig.set_figwidth(18)
            im1 = axis.imshow(err_mat_tot)
            fig.colorbar(im1, ax=axis)
            axis.set_title('Performance Error Matrix')

            fig.savefig(plot_dir+"errormat_"+beam+".png")

def migration_matrices():
    plot_dir = os.path.join(dest, "migration_matrix_plots/")
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)
    amplitudes_dict = {}
    mat_dict = {}
    #us_ds = "upstream"
    #figs = {}
    for us_ds in ["downstream"]:
        for beam in beam_list:
            base_path = "plots_2017-02-6_"+beam+"_"+base_sys
            base_amp = load_json(base_path)
            base_pdf = pull_pdfs(base_amp, us_ds)
            base_pdf_us = pull_pdfs(base_amp, "upstream")
            base_mat = pull_migration_usds(base_amp)
        
            for sys in sys_list+["tku_base"]:
            #for sys in performance_list:
                sys_dir = "plots_2017-02-6_"+beam+"_"+sys
        
                src_amplitudes = load_json(sys_dir)
                amplitudes_dict[sys] = src_amplitudes
                mat = pull_migration_usds(src_amplitudes)
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
                im1 = axis.imshow(mat)
                fig.colorbar(im1, ax=axis)
                axis.set_title('Performance Error Matrix')

                fig.savefig(plot_dir+"errormat_"+beam+"_"+sys+".png")
                fig.close()



if __name__ == "__main__":
    #detector_errors()
    #detector_errors2()
    #performance_errors()
    migration_matrices()

