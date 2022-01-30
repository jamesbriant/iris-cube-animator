import irisdataloader as idl
import iriscubehandler as ich
import iriscubeanimator as icp
import iris
import matplotlib.pyplot as plt
import iris.quickplot as qplt

path = 'data/sresa1b_ncar_ccsm3-example.nc'

loader = idl.IrisDataLoader(path)
air_temp_cube = ich.Cube(loader, 'air_temperature')

#air_temp_cube.set_time_constraint(lambda t: t.point.day == 16) # 2000-05-16 12:00:00
#air_temp_cube.set_latitude_constraint(lambda lat: -30. < lat < 30.)
#air_temp_cube.set_constraint('latitude', lambda lat: -45. < lat < 45.)

new_cube = air_temp_cube.get_cube()

#print(new_cube)

#qplt.contour(new_cube)
#qplt.contourf(new_cube, 25)

# Add coastlines
#plt.gca().coastlines()

#plt.show()






anim = icp.Animator(air_temp_cube)
anim.set_iterator_coord('time')
anim.set_axes_coords(['longitude'], ['latitude'])
anim.set_save_path('gifs/test_gif.gif')
anim.animate()
#anim.save_animation()
plt.show()


del new_cube
del air_temp_cube
del loader