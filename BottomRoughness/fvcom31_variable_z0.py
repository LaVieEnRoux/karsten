import netCDF4 as nc
import numpy as np

# parameters
kappa = 0.4
min_d = 3


def variableBR(cd, H, grid, outfile):
    '''
    Create a variable bottom roughness data file given user inputs of the
    cd and H parameters, and the grid on which we're building the file.
    Creates an nc file readable by FVCOM.
    '''

    min_depth, max_depth = min_d, H

    # read in the grid nc file variables
    grid_file = nc.Dataset(grid)
    trinodes = grid_file.variables['nv']
    h = grid_file.variables['h']
    h = np.array(h)
    htri = (h[trinodes[0, :] - 1] + h[trinodes[1, :] - 1] + h[trinodes[2, :] - 1]) / 3

    print h.size

    # calculate z0
    z0 = htri
    print np.where(htri > min_depth)
    z0[np.where((htri > min_depth) & (htri < max_depth))[0]] = \
        max_depth * np.exp(-(kappa * cd**(-0.5) + 1))
    z0[np.where(htri <= min_depth)[0]] = \
        max_depth * np.exp(-(kappa * cd**(-0.5) + 1))
    z0[np.where(htri >= max_depth)[0]] = \
        htri[np.where(htri >= max_depth)] * np.exp(-(kappa * cd**(-0.5) + 1))
    z0 = z0.astype(np.float64)

    # pass the data onto an nc file
    br2nc(z0, outfile)


def br2nc(z0, outfile):
    '''
    Converts a bottom roughness array to a netcdf4 file, readable
    by FVCOM.
    '''

    # create netcdf4 file
    n = z0.size
    nc_id = nc.Dataset(outfile, 'w', format='NETCDF4')

    # set up the nc file and put all the data into it
    nc_id.createDimension('nele', n)
    z0b = nc_id.createVariable('z0b', 'f8', ('nele'))
    z0b.name = 'bottom roughness lengthscale'
    z0b.units = 'metres'
    z0b[:] = z0

    nc_id.close()


if __name__ == "__main__":

    path = '/EcoII/acadia_uni/projects/voucher_program/work/simulations/' \
        + 'acadia_bay_of_fundy_numerical_model_r50_v01/' \
        + 'voucher_3d_repmonth/output/voucher_0001.nc'
    output = "py_br_test.nc"
    variableBR(0.0025, 100, path, output)
