import iris
import iriscubehandler as ich
import matplotlib.pyplot as plt
import iris.quickplot as qplt
from matplotlib.animation import FuncAnimation

from typing import List, Tuple

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


    def check_fig_dims(self) -> bool:
        """
        Check if the requested figure dimensions equals the requested plots from the cube handlers.
        """
        cube_list_fig_count = 0
        for cube in self.cube_list:
            cube_list_fig_count += cube.get_plot_count()

        assert cube_list_fig_count == self.fig_count, f"Expected plot count ({cube_list_fig_count}) does not equal requested figure count ({self.fig_count})."


    def _create_plotting_slices(self) -> None:
        """
        Generate the plotting slices for each cubehandler
        """
        for cube in self.cube_list:
            cube._create_slices()


    def _generate_plotting_sequence(self) -> None:
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


    def animate(self, path: str = None) -> None:
        """
        Run animation

        path : str (optional)
            new path is set if provided
        """
        if path != None:
            self.set_save_path(path)

        fig = plt.figure()

        # Create the plotting slices
        self._create_plotting_slices()
        self._generate_plotting_sequence()

        I = self.fig_dims[0]
        J = self.fig_dims[1]

        def update(frame=0):
            # clear the current figure
            plt.gcf().clf()

            # iterate over each subplot
            n = 0 # subplot number
            for i in range(I): #iterate over the rows
                for j in range(J): #iterate over the columns
                    n += 1
                    plt.subplot(I, J, n)

                    print(frame, n, self.plotting_sequence[n-1], 'HERE')

                    # qplt.contourf(self.cube_list[n-1]._get_next_slice(self.plotting_sequence[n-1]), 25)
                    qplt.contourf(self.cube_list[self.cube_selector_sequence[n-1]]._get_next_slice(self.plotting_sequence[n-1]), 25)
                    plt.gca().coastlines()
            
        # self.animation = FuncAnimation(fig, update, init_func=update, frames=self.frame_count-1, interval=100, blit=False, repeat=False)
        self.animation = FuncAnimation(fig, update, init_func=update, frames=31, interval=100, blit=False, repeat=False)


    def save_animation(self, path: str = None) -> None:
        """
        Save animation as gif

        path : str (optional)
            new path is set if provided
        """
        if not self.is_save_path_set(path):
            print('save_path not set. Provide a path or use set_save_path().')
            return 1

        if self.animation == None:
            print('No animation to save! Run animate()')
            return 2

        self.animation.save(self.save_path, writer='imagemagick')
        return 0
        


    def animate_and_save(self, path: str = None) -> None:
        """
        Run animation and save to path.

        path : str (optional)
            new path is set if provided        
        """
        self.animate()
        self.save_animation(path)