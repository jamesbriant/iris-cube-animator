import iriscubehandler as ich
import matplotlib.pyplot as plt
import iris.plot as iplt
import numpy as np
from matplotlib.animation import FuncAnimation, FFMpegWriter

from typing import List, Tuple, Union

class Animator():
    """
    For creating animations from a set of cubes.
    """
    def __init__(self, cube_list: List[ich.Cube], fig_dims: Tuple[int, int] = (1,1)) -> None:
        """
        cube_list : list
            list of iriscubehandler objects
        fig_dims : 2-tuple (optional)
            desired dimensions of plots in final figure, (nrow, ncol)
        """
        self.cube_list = cube_list
        self.set_fig_dims(fig_dims)
        self.save_path = None
        self.animation = None
        self.coord_points = {}
        self.frame_count = 0
        self.animation_interval = 100
        self.coastlines = False
        self.plot_color_steps = 25
        self.pause = False
        self.pause_frames = []
        self.pause_start_frames = [0]
        self.pause_end_frames = [1]
        self.total_paused_frames = 0

    
    def add_cubes(self, new_cubes: List[ich.Cube]) -> None:
        """
        Add additional cubes for plotting

        new_cubes : List[ich.Cube]
            list of iriscubehandler objects
        """
        for new_cube in new_cubes:
            self.cube_list.append(new_cube)


    def set_fig_dims(self, fig_dims: Tuple[int, int]) -> None:
        """
        Set the desired dimensions of plots in final figure.

        fig_dims : Tuple[int, int]
            desired dimensions of plots in final figure, (nrow, ncol)
        """
        assert type(fig_dims) is tuple and len(fig_dims) == 2, f'fig_dims must be 2-tuple of integers. Received {fig_dims}.'

        self.fig_dims = fig_dims
        self.fig_count = fig_dims[0] * fig_dims[1]


    def set_animation_interval(self, interval: int = 100) -> None:
        """
        Set animation_interval

        interval : int
            new animation interval to be set
        """
        self.animation_interval = interval


    def include_coastlines(self) -> None:
        """
        Include coastlines in final animation figure.
        """
        self.coastlines = True


    def set_plot_color_steps(self, steps: int) -> None:
        """
        Set the number of colour steps for the animation
        """
        self.plot_color_steps = steps


    def set_pause_frames(self, pause_frames: List[Tuple[Union[int, str], int]]) -> None:
        """
        Set of the frames on which to pause the animation. Also provide the number of frames to pause for.

        pause_frames : List[Tuple[int, int]]
            list of 2-tuples of the form (pause_location, pause duration)
        """
        self.pause_frames = pause_frames

    
    def __calculate_pause_frame_locations(self) -> None:
        """
        Calculate the frames at which pauses start and finish.
        """
        buffer = 0
        for start, duration in self.pause_frames:
            if start == 0 or start == 1:
                raise Exception(f'For reasons that are too complicated to explain, please don\'t add a pause at frame 0 or frame 1.')
            # elif start == 'start':
            #     start = 0
            elif start == 'end':
                start = self.smallest_frame_count - 1
            elif start < 0:
                start += self.smallest_frame_count

            self.pause_start_frames.append(start + buffer)
            self.pause_end_frames.append(start + buffer + duration)
            buffer += duration

        self.total_paused_frames = buffer + 1


    def __check_plotting_dimensions(self) -> None:
        """
        Check if the requested figure dimensions equals the requested plots from the cube handlers.
        """
        cube_list_fig_count = 0
        for cube in self.cube_list:
            cube_list_fig_count += cube.get_plot_count()

        assert cube_list_fig_count == self.fig_count, f"Expected plot count ({cube_list_fig_count}) does not equal requested figure count ({self.fig_count})."


    def __set_iterator_frame_count(self) -> None:
        """
        Set smallest iterator dimension size
        """
        smallest_frame_count = self.cube_list[0].get_frame_count()
        for cube in self.cube_list[1:]:
            frame_count = cube.get_frame_count()
            if frame_count < smallest_frame_count:
                smallest_frame_count = frame_count

        self.smallest_frame_count = smallest_frame_count
            

    def __create_plotting_slices(self) -> None:
        """
        Generate the plotting slices for each cubehandler
        """
        for cube in self.cube_list:
            cube.create_slices()


    def __generate_plotting_sequence(self) -> None:
        """
        Builds plotting sequence accounting for multiple plots from a single cube.
        """
        self.plotting_sequence = []
        self.cube_selector_sequence = []
        n = 0
        for cube in self.cube_list:
            for i in range(cube.get_plot_count()):
                self.plotting_sequence.append(i)
                self.cube_selector_sequence.append(n)
            n += 1

    
    def __create_subplot_titles(self) -> None:
        """
        Create the titles for each subplot
        """
        self.subplot_titles = []
        for cube in self.cube_list:
            title = cube.get_cube_name()
            units = cube.get_cube_units()
            self.subplot_titles.append(f'{title} / {units}')


    def __set_min_max_vals(self) -> None:
        """
        
        """
        self.max_vals = []
        self.min_vals = []
        for cube in self.cube_list:
            vals = cube.get_cube_min_max()
            self.min_vals.append(vals[0])
            self.max_vals.append(vals[1])


    def set_save_path(self, path: str) -> None:
        """
        sets a new save path

        path : str
            new path to be set
        """
        self.save_path = path


    def is_save_path_set(self, path: str = None) -> bool:
        """
        checks if path is set. Returns boolean

        path : str (optional)
            new path is set if provided
        """
        if path == None:
            # no path given

            if self.save_path == None:
                # no path set
                return False
            
            # path is set
            return True
        
        # new path given and set
        self.set_save_path(path)
        return True


    def __get_master_title(self) -> None:
        """
        
        """
        cube = self.cube_list[0]
        output = f'{cube.iterator_coord}: {cube.get_coord_point(cube.iterator_coord, self.pseudo_frame - 1)}'
        return output


    def animate(self, path: str = None) -> None:
        """
        Run animation
        
        path : str (optional)
            new path is set if provided
        """
        if path != None:
            self.set_save_path(path)

        # Check the requested dimensions match the total number of cubes for plotting
        self.__check_plotting_dimensions()

        # Set smallest iterator dimension size
        self.__set_iterator_frame_count()

        # Calculate pause locations
        self.__calculate_pause_frame_locations()

        # Create the figure for plotting
        fig = plt.figure()

        # Create the plotting slices
        self.__create_plotting_slices()
        self.__generate_plotting_sequence()

        # Create subplot titles
        self.__create_subplot_titles()

        # Find the min and max values for the cubes
        self.__set_min_max_vals()

        I = self.fig_dims[0]
        J = self.fig_dims[1]

        self.pause = [False]*self.fig_count
        self.paused_frame_data = []
        self.pseudo_frame = 1

        self.init_plot = True

        def update(frame=0):
            # clear the current figure
            plt.gcf().clf()

            # iterate over each subplot
            n = 0 # subplot number
            for i in range(I): #iterate over the rows
                for j in range(J): #iterate over the columns
                    # select the n'th subplot
                    n += 1
                    # plt.subplot(I, J, n)

                    # plt.axes(projection=ccrs.Orthographic(central_longitude=0.0, central_latitude=90.0))

                    cube_selector = self.cube_selector_sequence[n-1]
                    cube = self.cube_list[cube_selector]

                    plt.subplot(I, J, n, projection=cube.get_projection())

                    # Check if pause is requested
                    if self.pause[cube_selector] == False:
                        data_to_plot = cube.get_next_slice(self.plotting_sequence[n-1])
                        if self.init_plot == False and n == 1:
                            self.pseudo_frame += 1
                        self.init_plot = False
                        if frame in self.pause_start_frames:
                            # Start of a pause!
                            self.pause[cube_selector] = True
                            # save the data
                            self.paused_frame_data.append(data_to_plot)
                    else:
                        # get paused data
                        data_to_plot = self.paused_frame_data[n-1]
                        # check for the end of the pause on the final subplot
                        if frame in self.pause_end_frames and n == self.fig_count:
                            # end the 'pause', delete the saved data and reset paused_frame_data
                            self.pause = [False]*self.fig_count
                            del self.paused_frame_data
                            self.paused_frame_data = []
                        

                    # plot the data
                    iplt.contourf(
                        data_to_plot, 
                        self.plot_color_steps,
                        levels=np.linspace(
                            self.min_vals[cube_selector], 
                            self.max_vals[cube_selector], 
                            self.plot_color_steps
                        )
                    )

                    # add title
                    plt.gca().set_title(self.subplot_titles[cube_selector])

                    # Add the colorbar
                    # ticklist = np.linspace(self.min_vals[cube_selector], self.max_vals[cube_selector], 8)
                    plt.colorbar(orientation="horizontal")#, ticks=ticklist)

                    # Add coastlines if requested
                    if self.coastlines == True:
                        plt.gca().coastlines()
                
            plt.suptitle(self.__get_master_title())

        self.animation = FuncAnimation(
            fig, 
            update,
            frames=self.smallest_frame_count + self.total_paused_frames,
            interval=self.animation_interval, 
            blit=False, 
            repeat=False
        )


    def save_animation(self, path: str = None, format: str = 'gif') -> None:
        """
        Save animation as gif

        path : str (optional)
            new path is set if provided
        format : str (optional)
            save as 'gif' or 'mp4'   
        """
        if not self.is_save_path_set(path):
            raise Exception('save_path not set. Provide a path or use set_save_path().')

        if self.animation == None:
            raise Exception('No animation to save! Run animate()')

        if format == 'gif':
            self.animation.save(self.save_path, writer='imagemagick')
        elif format == 'mp4':
            self.animation.save(self.save_path, writer=FFMpegWriter(fps=1000/self.animation_interval, bitrate=100000), dpi=200)
        


    def animate_and_save(self, path: str = None, format: str = 'gif') -> None:
        """
        Run animation and save to path.

        path : str (optional)
            new path is set if provided
        format : str (optional)
            save as 'gif' or 'mp4'   
        """
        self.animate()
        self.save_animation(path, format)