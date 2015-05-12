%Creating variable z0 file
%May 5 2015: 
%for 2d z0 is constant in depths between 3 and 100 m, 
%and equal to Cd = 0.0025 at user defined depth
%Outside of these depths, z0 is set so that Cd = 0.0025

clear

%% Parameters
kappa = 0.4;

%% User input
% For 2d model
Cd = 0.0025;
H = 100; % Height for calculating z0 for given Cd
mindepth = 3;
maxdepth = H;
% FORCE
%path='/EcoII/force/runs/smallcape_force/2011-10-30_2011-12-11/output/';
%path='/EcoII/force/force_acadia_project/work/simulations/acadia_force_numerical_model_r20_v01/2008-08-17_2008-09-24/output/';
%filenc='smallcape_force_0001.nc';
%pathsave = '/EcoII/force/Misc/';
%Digby NEck
%path='/EcoII/acadia_uni/workspace/simulated/FVCOM/dngridCSR/2014_to_2010_run/2010_month_1/output/';
%pathsave = '/EcoII/acadia_uni/';
%filenc='dngridCSR_0001.nc';
%Voucher
path='/EcoII/acadia_uni/projects/voucher_program/work/simulations/acadia_bay_of_fundy_numerical_model_r50_v01/voucher_3d_repmonth/output/';
%pathsave = '/EcoII/acadia_uni/projects/voucher_program/work/';
pathsave = '/EcoII/acadia_uni/code/jonCode/BottomRoughness/';
filenc='voucher_0001.nc';
filesave = 'z0_depth100';

%% Load
ncid = netcdf.open([path, filenc],'NC_NOWRITE');
trinodes = netcdf.getVar(ncid,netcdf.inqVarID(ncid,'nv'));
x = netcdf.getVar(ncid,netcdf.inqVarID(ncid,'x'));
y = netcdf.getVar(ncid,netcdf.inqVarID(ncid,'y'));
h = netcdf.getVar(ncid,netcdf.inqVarID(ncid,'h'));
h = double(h);

htri=(h(trinodes(:,1))+...
       h(trinodes(:,2))+...
       h(trinodes(:,3)))/3;

%% Calculate z0
z0 = htri; %Initialize
z0( logical((htri>mindepth) .* (htri<maxdepth)) ) = ...
    H * exp(-(kappa*Cd^(-1/2)+1));
z0( (htri<=mindepth) ) = ...
    H.* exp(-(kappa*Cd^(-1/2)+1));
z0( (htri>=maxdepth) ) = ...
    htri( (htri>=maxdepth) ) .* exp(-(kappa*Cd^(-1/2)+1));    

z0 = double(z0);

save([pathsave,filesave,'.dat'],'z0','-ASCII')

fvcom31_z0b2nc(pathsave, [filesave,'.dat'], [filesave,'.nc'])

cbc=kappa^2./(log(htri./(z0*exp(1)))).^2;
cbc(htri<=3)=kappa^2./(log(3./(z0(htri<=3)*exp(1)))).^2;

figure
patch('Vertices',[x,y],'Faces',trinodes,'FaceVertexCdata',cbc)
shading flat
colorbar
