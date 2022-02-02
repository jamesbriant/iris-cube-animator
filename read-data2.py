import irisdataloader as idl
import iriscubehandler as ich
import iriscubeanimator as icp

path = 'data/ECMWF_ERA-40_subset.nc'

loader = idl.IrisDataLoader(path)
mean_sea_level_pressure = ich.Cube(loader, 'Mean sea level pressure')


mean_sea_level_pressure.set_time_constraint(lambda t: t.point.hour == 12)
# #mean_sea_level_pressure.set_latitude_constraint(lambda lat: -30. < lat < 30.)
# #mean_sea_level_pressure.set_constraint('latitude', lambda lat: -45. < lat < 45.)




mean_sea_level_pressure.set_iterator_coord('time')
mean_sea_level_pressure.set_axes_coords(['longitude'], ['latitude'])

anim = icp.Animator([mean_sea_level_pressure], (1,1))
anim.set_save_path('mp4s/test1.mp4')        # required
anim.include_coastlines()                   # default is off
anim.set_plot_color_steps(30)               # default is 25
anim.set_pause_frames([('end', 12)])        # pause for 15 frames at the end of animation
anim.set_animation_interval(120)            # default is 100ms
anim.animate()                              # run animation
#plt.show()
#anim.save_animation()                       # save to file
anim.save_animation_mp4()


del mean_sea_level_pressure
del loader