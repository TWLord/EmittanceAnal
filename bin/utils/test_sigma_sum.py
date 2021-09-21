def update_lists(means, sigma, events, data_list):
    for i in range(len(data_list[0])):
        sigma[i] = (sigma[i]**2 + means[i]**2)*events
        means[i] *= events

    print sigma
    events += len(data_list)
    print events, 'events'

    for data in data_list:
        for var in range(len(data)):
            means[var] += data[var]
            sigma[var] += data[var]**2
    print sigma

    for i in range(len(data_list[0])):
        means[i] = means[i]/events
        sigma[i] = sigma[i]/events
        sigma[i] -= means[i]**2
        sigma[i] = abs(sigma[i])**0.5
        
    return means, sigma, events


if __name__ == "__main__":
    nvars = 5
    events = 0
    vals_1 = [[1.,2.,3.,4.,5.], [1.,2.,3.,4.,5.], [1.,2.,3.,4.,5.], [1.,2.,3.,4.,5.], [1.,2.,3.,4.,5.]]
    vals_2 = [[1.,2.,3.,4.,5.], [1.,6.,2.,3.,6.], [1.,25.,2.,1.,5.], [1.,4.,18.,5.,7.], [1.,9.,12.,3.,4.]]
    vals_3 = [[1.,22.,23.,24.,25.], [1.,26.,22.,23.,26.], [1.,25.,22.,31.,15.], [1.,14.,18.,35.,27.], [1.,29.,12.,23.,14.]]
    means = [0. for i in range(nvars)]
    sigma = [0. for i in range(nvars)]

    means, sigma, events = update_lists(means, sigma, events, vals_1)
    print '1'
    print 'means', means
    print 'sigma', sigma

    means, sigma, events = update_lists(means, sigma, events, vals_2)
    print '2'
    print 'means', means
    print 'sigma', sigma

    means, sigma, events = update_lists(means, sigma, events, vals_3)
    print '3'
    print 'means', means
    print 'sigma', sigma


    events = 0
    means = [0. for i in range(nvars)]
    sigma = [0. for i in range(nvars)]

    means, sigma, events = update_lists(means, sigma, events, vals_1+vals_2+vals_3)

    print '1+2+3'
    print 'means', means
    print 'sigma', sigma
