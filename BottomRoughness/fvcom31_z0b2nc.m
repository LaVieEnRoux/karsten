function [ ierr ] = fvcom31_z0b2nc(path, z0, z0file)
%Converts file of bottom roughness values to an .nc file, to be
%read into fvcom31
%   A function with variables 'path', 'el_obc' and 'elevfile'.  
%   Enter in the path to the directory that contains the el_obc.dat 
%   file, the name of the el_obc.dat file and the name you wish to call 
%   the converted el_obc.dat file (i.e. the .nc file).  Each of path, 
%   el_obc and elevfile must be put in single quotes.  
%

%BOTTOM ROUGHNESS FILE
z0=load([path,z0]);
N=numel(z0);
ncid = netcdf.create([path, z0file], 'clobber');             

%DIMENSIONS
nele = netcdf.defDim(ncid,'nele',N);%numel(obcs));

%VARIABLES (& THEIR ATTRIBUTES)
z0b = netcdf.defVar(ncid,'z0b','float',nele);
netcdf.putAtt(ncid,z0b,'long_name','bottom roughness lengthscale');
netcdf.putAtt(ncid,z0b,'units','metres');

netcdf.endDef(ncid);

%DATA
netcdf.putVar(ncid,z0b,z0);

netcdf.close(ncid);

ierr = 0;

