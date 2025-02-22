from __future__ import print_function

from landlab.components.craters import impactor
from landlab import ModelParameterDictionary

from landlab import RasterModelGrid
import numpy as np
import pylab
from scipy.optimize import curve_fit

#get the needed properties to build the grid:
input_file = './craters_params_init.txt'
inputs = ModelParameterDictionary(input_file)
nrows = inputs.read_int('nrows')
ncols = inputs.read_int('ncols')
dx = inputs.read_float('dx')
leftmost_elev = inputs.read_float('leftmost_elevation')
initial_slope = inputs.read_float('initial_slope')
nt = inputs.read_int('number_of_craters_per_loop')
loops = inputs.read_int('number_of_loops')

mg = RasterModelGrid(nrows, ncols, dx)
mg.set_looped_boundaries(True, True)
mg.add_zeros('topographic__elevation', at='node')

def fitFunc(t, a,b,c,d,e,f,g):
    return a*t**6. + b*t**5. +c*t**4. + d*t**3. + e*t**2. + f*t + g



#instantiate the component:
craters_component = impactor(mg, input_file)

params_from_first_try = np.array([ -2.10972667e+02,   3.23669793e+02,  -2.01070114e+02,
                                    7.40429578e+01,  -1.77124298e+01,   2.03540786e-01,
                                   -1.01168519e-01])
list_of_mass_bals = []
param_collection = np.empty_like(params_from_first_try)

slope_values = np.arange(0., 51.)/100.
beta = []

print('Beginning loop...')

repeats = 1
work_with = slope_values

counter = 0
for i in range(repeats):
    mass_balance = []
    for k in work_with:
        #print 'Slope is ', k
        #create the fields in the grid
        initial_slope = k
        z = mg.zeros(at='node') + leftmost_elev
        z += initial_slope*np.amax(mg.node_y) - initial_slope*mg.node_y
        mg.at_node[ 'topographic__elevation'] = z

        #craters_component.grid = mg

        mg = craters_component.excavate_a_crater_furbish(mg)
        mass_balance.append(craters_component.mass_balance)
        beta.append(craters_component.impact_angle_to_normal)

        elev_r = mg.node_vector_to_raster(mg.at_node['topographic__elevation'])
        pylab.figure(1)
        pylab.imshow(elev_r)
        pylab.colorbar()
        pylab.show()
        if counter == 1:
            break
        counter += 1

    list_of_mass_bals += list(mass_balance)

    fitParams, fitCovariances = curve_fit(fitFunc, work_with, mass_balance)

    param_collection = np.vstack((param_collection, fitParams))

    synthetic_solution = fitFunc(work_with, fitParams[0], fitParams[1], fitParams[2], fitParams[3], fitParams[4], fitParams[5], fitParams[6])
    #first_synthetic_solution = fitFunc(slope_values, params_from_first_try[0], params_from_first_try[1], params_from_first_try[2], params_from_first_try[3], params_from_first_try[4], params_from_first_try[5], params_from_first_try[6])

    print(('Done ', i))

    pylab.figure(2)
    pylab.plot(mass_balance)
    pylab.plot(synthetic_solution)
    #pylab.show()

fitParams, fitCovariances = curve_fit(fitFunc, np.tile(work_with, repeats), list_of_mass_bals)

#fitParams = np.mean(param_collection, axis=0)

aggregate_solution = fitFunc(work_with, fitParams[0], fitParams[1], fitParams[2], fitParams[3], fitParams[4], fitParams[5], fitParams[6])

pylab.figure(2)
pylab.plot(aggregate_solution, 'x')
