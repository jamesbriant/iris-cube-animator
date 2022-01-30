from statistics import mean
import irisdataloader as idl
import iriscubehandler as ich
import iriscubeanimator as icp
import iris
import matplotlib.pyplot as plt
import iris.quickplot as qplt

path = 'data/ECMWF_ERA-40_subset.nc'

loader = idl.IrisDataLoader(path)
mean_sea_level_pressure = ich.Cube(loader, 'Mean sea level pressure')


mean_sea_level_pressure.set_time_constraint(lambda t: t.point.hour == 12)
# #mean_sea_level_pressure.set_latitude_constraint(lambda lat: -30. < lat < 30.)
# #mean_sea_level_pressure.set_constraint('latitude', lambda lat: -45. < lat < 45.)




mean_sea_level_pressure.set_iterator_coord('time')
mean_sea_level_pressure.set_axes_coords(['longitude', 'longitude'], ['latitude', 'latitude'])

anim = icp.Animator([mean_sea_level_pressure], (1,2))
# anim.set_iterator_coord('time')
# anim.set_axes_coords(['longitude', 'longitude'], ['latitude', 'latitude'])
anim.set_save_path('gifs/test_subplots2.gif')
anim.animate()
#plt.show()
anim.save_animation()


del mean_sea_level_pressure
del loader