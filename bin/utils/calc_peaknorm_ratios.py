
def get_LH2():
    data_dict = {'LH2-EMPTY': {
                               '6-140':10368.0/98371.0,
                               '10-140':4403.0/52486.0
                              },
                 'LH2':       {
                               '6-140':14286.0/173716.0,
                               '10-140':7025.0/107051.0,
                              },
                }
    
    mc_dict = {'LH2-EMPTY': {
                             '6-140':4970.0/42350.0,
                             '10-140':2230.0/23007.0,
                            },
               'LH2':       {
                             '6-140':3673.0/42095.0,
                             '10-140':1714.0/23696.0,
                            },
              }
    
    print 'peak bin ratios'
    for key in data_dict.keys():
        print key
        for subkey in data_dict[key].keys():
            print subkey
            print 'data ratio:', data_dict[key][subkey]
            print 'mc ratio:', mc_dict[key][subkey]
    
    for beam in ['6-140', '10-140']:
        #print beam, 'empty/full ratio:', data_dict['LH2-EMPTY'][beam] / data_dict['LH2'][beam]
        print beam, 'full/empty data ratio:', data_dict['LH2'][beam] / data_dict['LH2-EMPTY'][beam]
        print beam, 'full/empty mc ratio:', mc_dict['LH2'][beam] / mc_dict['LH2-EMPTY'][beam]

def get_LiH():
    data_dict = {'EMPTY':{
                          '3-140':4966.0/34108.0,
                          '4-140':12045.0/79816.0,
                          '6-140':9484.0/67861.0,
                         },
                 'LiH':  {
                          '3-140':1759.0/21144.0,
                          '4-140':8342.0/98463.0,
                          '6-140':4819.0/58276.0,
                         },
                }
    
    mc_dict = {'EMPTY':{
                        '3-140':4269.0/19771.0,
                        '4-140':9288.0/46429.0,
                        '6-140':7465.0/42512.0,
                       },
               'LiH':  {
                        '3-140':1842.0/19416.0,
                        '4-140':4120.0/44076.0,
                        '6-140':3498.0/41385.0,
                       },
              }
    
    print 'peak bin ratios'
    for key in data_dict.keys():
        print key
        for subkey in data_dict[key].keys():
            print subkey
            print 'data ratio:', data_dict[key][subkey]
            print 'mc ratio:', mc_dict[key][subkey]
    
    for beam in ['3-140', '4-140', '6-140']:
        print beam, 'full/empty data ratio:', data_dict['LiH'][beam] / data_dict['EMPTY'][beam]
        print beam, 'full/empty mc ratio:', mc_dict['LiH'][beam] / mc_dict['EMPTY'][beam]



if __name__ == "__main__":
    #get_LH2()
    get_LiH()
