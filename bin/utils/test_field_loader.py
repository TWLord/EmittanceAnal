import os
import shutil
import ROOT

# memory testing
#from guppy import hpy
#h = hpy()
#print "Starting heapy"
#print h.heap()

import sys
import Configuration  # MAUS configuration (datacards) module
import maus_cpp.globals as maus_globals # MAUS C++ calls
import maus_cpp.field as field # MAUS field map calls
import xboa.common  # xboa post-processor library

LENGTH = 1000.
LEGEND_SPACE = 0.1



def initialise_maus():
    sys.argv.append('--simulation_geometry_filename')
    sys.argv.append('/data/mice/phumhf/Geometries/runnumber_09911/ParentGeometryFile.dat')
    print sys.argv
    configuration = Configuration.Configuration().\
                                          getConfigJSON(command_line_args=True)
    maus_globals.birth(configuration)


def plot_z_range(z_list, b_min_max, name, canvas):
    graph_list = []
    for r_pos, line_color in [(160., 8), (0., 1)]:
        #z_list = [float(z_pos) for z_pos in range(19000, 20001, 10)]
        btot_list = []
        for z_pos in z_list:
            (bx_field, by_field, bz_field, ex_field, ey_field, ez_field) = \
                                     field.get_field_value(r_pos, 0., z_pos, 0.)
            btot = bz_field#(bx_field**2+by_field**2+bz_field**2)**0.5
            #btot = (bx_field**2+by_field**2+bz_field**2)**0.5
            if (btot - bz_field) > 1E-4 :
              print "difference in Bt - Bz = " + str(btot - bz_field)
            if bz_field < 0:
                #btot *= -1
                btot *= +1
            btot_list.append(btot*1e3)  # btot in T
            #print 'z:', z_pos, ' ** b:', bx_field, by_field, bz_field, \
            #                       'e:', ex_field, ey_field, ez_field
        gz_list = [(z - Z_OFFSET)/LENGTH for z in z_list]
        [ymin, ymax] = [b_min_max[0], b_min_max[1]] # xboa.common.min_max(btot_list+[3.1])
        [xmin, xmax] = [min(gz_list), max(gz_list)]
        print xmax
        xmax += (xmax-xmin)*LEGEND_SPACE
        # now make a ROOT graph of bz against z
        hist, graph = xboa.common.make_root_graph("x="+str(r_pos/LENGTH)+" m", gz_list, "",
                                                  btot_list, "B_{z} [T]",
                                                  xmin=xmin, xmax=xmax,
                                                  ymin=ymin, ymax=ymax)
        graph.SetLineColor(line_color)
        graph.SetLineStyle(2)
        if (abs(r_pos-160.) < 1e-9):
            prep_narrow_plot(hist, name)
        graph_list.append(graph)
        graph.Draw('l same')
        canvas.Update()
    graph_list += plot_hps(z_list, False, flip_z=17000)
    #graph_list += plot_hps(z_list, False, flip_z=None)
    plot_tracker_stations(z_list, btot_list)
    text_box(graph_list)
    canvas.Update()
    return canvas

def load_field_map():
    for r_pos, z_pos in [ (0.0, 11000.), (15.0, 11000.)]:
        (bx_field, by_field, bz_field, ex_field, ey_field, ez_field) = \
                            field.get_field_value(r_pos, 0., z_pos, 0.)
        print bx_field, by_field, bz_field

def schematics_plot(my_dir):
    #canvas = ROOT.TCanvas("canvas", "canvas", 1200, 500) # Original width
    #canvas = ROOT.TCanvas("canvas", "canvas", 1800, 500) # 3/2 * width
    canvas = ROOT.TCanvas("canvas", "canvas", 1500, 500) # half n half
    canvas.Divide(1, 1, 0.01, 0.1)
    canvas_plot = canvas.cd(1)
    canvas_plot.Divide(1, 2, 0.01, 0.0)
    plot_z_range(range(13000, 21001, 1), [None, None], my_dir+"bfield_vs_z", canvas_plot.cd(1))
    plot_sigma_x(13000, 21001, my_dir, canvas_plot.cd(2))
    canvas_plot.Update()
    canvas.cd()
    text_box = ROOT.TPaveText(0.8, 0.04, 0.9, 0.12, "NDC")
    text_box.SetFillColor(0)
    text_box.SetBorderSize(0)
    text_box.SetTextSize(0.05)
    text_box.SetTextAlign(12)
    text_box.AddText("z [m]")
    text_box.Draw()

    canvas.Update()
    for fmt in "png", "pdf", "root":
        canvas.Print(my_dir+"/schematics_plot."+fmt)


def main():
    """
    Get the field and check things are working
    """
    # set up datacards (geometry specified e.g. on command line using --simulation_geometry_filename)
    #my_dir = "field_loader/"
    #if os.path.exists(my_dir):
    #    shutil.rmtree(my_dir)
    #os.makedirs(my_dir)
    print "before initialising maus"
    #print h.heap()
    raw_input("waiting..")
    initialise_maus()
    print "after initialising maus"
    #print h.heap()
    raw_input("waiting..")

    #schematics_plot(my_dir)
    load_field_map()
    print "after calling field map"
    #print h.heap()
    raw_input("waiting..")
    # Clean up
    maus_globals.death()
    print "Called death. Freed memory?"
    raw_input("waiting..")
    #field.death()
    # Finished

if __name__ == "__main__":
    main()
    #raw_input()
    print "Finished - press <CR> to end"
    
