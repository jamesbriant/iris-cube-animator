import iris
import numpy as np
from datetime import date, timedelta
import cartopy.crs as ccrs

from typing import List, Tuple, Union
import warnings

class Cube():
    """
    Handler for a single cube. Can apply constraints and retrieve 
    """
    def __init__(self, *args, **kwargs) -> None:
        """
        Either supply a loader and a cube_name or just a cube.

        loader : object
            irisdataloader object
        cube_name : str
            desired cube from the loader object
        cube : object
            a single iris.cube.Cube object
        """

        self.cube = None
        self.dim_coord_names = []
        self.iterator_coord = None
        self.coord_points = {}
        self.frame_count = 0
        self.plot_count = 0
        self.x_plotting_coords = []
        self.y_plotting_coords = []
        self.make_iterator_prettier = False
        self.projection = None

        # Overloaded constructor. 1 arg => cube provided. 2 args => loader and cube_name provided.
        if len(args) == 1:
            loader = None
            cube_name = None
            cube = args[0]
        elif len(args) == 2:
            loader = args[0]
            cube_name = args[1]
            cube = None
        else:
            loader=None; cube_name=None; cube=None

        # Check the inputs
        if loader != None and cube_name != None and cube != None:
            warnings.warn("Please provide only a loader and cube_name or a single cube, not all three! Using the loader and cube_name.")
            # Use the loader, not the provided cube
            cube = None

        # if a loader and cube_name is provided
        if loader != None and cube_name != None:
            self.cube = [cube for cube in loader.get_cube_list() if cube.standard_name == cube_name or cube.long_name == cube_name]

            # check the number of cubes
            if len(self.cube) == 1:
                self.cube = self.cube[0]
            elif len(self.cube) > 1:
                warnings.warn("Multiple cubes with this name, taking the first one.")
            else:
                raise Exception(f"No cubes found with this name: {cube_name}")

        elif cube != None:
            # save the provided cube
            self.cube = cube
        else:
            raise Exception("Please provide either a loader and valid cube_name or a single iris cube.")

        # get names of all the dim-coordinates
        self.dim_coord_names = []
        for coord in self.cube.coords():
            self.dim_coord_names.append(coord.name())


    def concatenate(self, new_cubes: List) -> None:
        """
        Concatenate additional cubes onto this object

        new_cubes : List[iris.cube.Cube, Cube]
            list of cubes to concatenate on to the original cube in this object.
        """
        # Convert all provides cubes to iris.cube.Cube
        dummy_list = [self.cube]
        for new_cube in new_cubes:
            if isinstance(new_cube, Cube):
                dummy_list.append(new_cube.get_cube())
            else:
                dummy_list.append(new_cube)

        # Try the concatenation procedure
        try:
            self.cube = iris.cube.CubeList(dummy_list).concatenate()[0]
            del dummy_list
        except:
            warnings.warn("Concatenation failed. Retaining the original cube.")


    def __repr__(self) -> str:
        return str(self.cube)


    def __str__(self) -> str:
        return str(self.cube)


    def __apply_constraint(self, constraint: iris.Constraint) -> None:
        """
        Private method for applying constraints to the cube

        constraint : object
            iris.Constraint object
        """
        self.cube = self.cube.extract(constraint)


    def coord(self, coord_name: str) -> str:
        return self.cube.coord(coord_name)


    def is_coord(self, coord_name: str) -> bool:
        """
        Test if coord_name is a coordinate of the cube
        """
        if coord_name in self.dim_coord_names:
            return True

        raise Exception(f'{coord_name} is not a valid coodinate of the cube.')

    __is_coord = is_coord


    def get_cube_name(self) -> str:
        """
        Return either standard name or long name
        """
        if self.cube.standard_name != None:
            return self.cube.standard_name
        elif self.cube.long_name != None:
            return self.cube.long_name
        
        return None


    def get_cube_units(self) -> str:
        """
        Return cube units
        """
        if self.cube.units != None:
            return self.cube.units
        
        return None


    def set_constraint(self, variable: str, condition) -> None:
        """
        Method for setting constraint against arbitrary valid coordinate of the cube.

        variable : str
            valid coordinate of the cube
        condition : lambda function
            lambda function
        """
        assert self.__is_coord(variable), f'{variable} is not a valid dimension coordinate. Requested constraint not applied.'

        constraint = iris.Constraint(coord_values={variable:condition})
        self.__apply_constraint(constraint)


    def set_longtidude_constraint(self, condition) -> None:
        variable = 'longitude'

        assert self.__is_coord(variable), f'{variable} is not a valid dimension coordinate. Requested constraint not applied.'

        constraint = iris.Constraint(longitude=condition)
        self.__apply_constraint(constraint)


    def set_latitude_constraint(self, condition):
        variable = 'latitude'
        
        assert self.__is_coord(variable), f'{variable} is not a valid dimension coordinate. Requested constraint not applied.'

        constraint = iris.Constraint(latitude=condition)
        self.__apply_constraint(constraint)


    def set_altitude_constraint(self, condition):
        variable = 'altitude'

        assert self.__is_coord(variable), f'{variable} is not a valid dimension coordinate. Requested constraint not applied.'

        constraint = iris.Constraint(altitude=condition)
        self.__apply_constraint(constraint)


    
    def set_model_level_constraint(self, condition):
        variable = 'model_level'
        
        assert self.__is_coord(variable), f'{variable} is not a valid dimension coordinate. Requested constraint not applied.'

        constraint = iris.Constraint(model_level=condition)
        self.__apply_constraint(constraint)


    def set_model_level_number_constraint(self, condition):
        variable = 'model_level_number'
        
        assert self.__is_coord(variable), f'{variable} is not a valid dimension coordinate. Requested constraint not applied.'

        constraint = iris.Constraint(model_level_number=condition)
        self.__apply_constraint(constraint)


    def set_time_constraint(self, condition):
        variable = 'time'
        
        assert self.__is_coord(variable), f'{variable} is not a valid dimension coordinate. Requested constraint not applied.'

        constraint = iris.Constraint(time=condition)
        self.__apply_constraint(constraint)


    def get_cube(self):
        return self.cube


    def __find_cube_min_max(self) -> None:
        """
        Find and set the maximum and minimum values in the cube
        """
        self.max_val = np.max(self.cube.data)
        self.min_val = np.min(self.cube.data)

    def get_cube_min_max(self) -> Tuple[int, int]:
        """
        Return a tuple of the min and max values of the cube's data.
        """
        if not hasattr(self, 'max_val'):
            self.__find_cube_min_max()
            
        return (self.min_val, self.max_val)
        
    
    ############################################################################
    ####        The following methods are used for the Animator class       ####
    ############################################################################

    def set_iterator_coord(self, coord: str, make_iterator_prettier: Union[bool, List]=False) -> None:
        """
        Set the cube coordinate over which the animation will iterate.

        coord : str
            iterator cube coordinate
        make_iterator_prettier : Union[bool, List]
            Set to true to convert 'days since...' format into prettier year-month-day format,
            alternatively provide a custom list of items to display instead.
        """
        if self.__is_coord(coord):
            self.iterator_coord = coord
            self.__set_coord_points(coord)
            self.frame_count = len(self.coord_points[coord])

            # Check the prettier iterator is the right length
            if isinstance(make_iterator_prettier, list):
                n = len(self.coord_points[coord])
                assert n == self.frame_count, f"Length of 'prettier iterator' ({n}) does not equal length of the requested iterator ({coord}, {self.frame_count})"
            self.make_iterator_prettier = make_iterator_prettier

    
    def get_frame_count(self) -> int:
        """return frame count"""
        return self.frame_count


    def __set_coord_points(self, coord_name: str) -> None:
        """
        get iris.cube.Cube.coord.points that are used in the plot. The points are saved to a dictionary.

        coord_name : str
            valid coordinate name of the provided cube.
        """
        self.coord_points[coord_name] = self.coord(coord_name).points

    
    def get_coord_point(self, coord_name: str, index: int) -> str:
        """
        Returns the value at the index located in the requested coordinate as a str

        coord_name : str
            requested coordinate
        index : int
            index of the requested point requested
        """

        if self.__is_coord(coord_name):
            if isinstance(self.make_iterator_prettier, list):
                return self.make_iterator_prettier[index]
            elif self.make_iterator_prettier == True:
                return self.coord('time').cell(index)
                
            return str(self.coord_points[coord_name][index])


    def set_axes_coords(self, x_coords: List[str] , y_coords: List[str]) -> None:
        """
        Set the cubes coordinates to plot on the axes

        x_coords : List[str]
            list of desired x-axis cube coordinates for the plots
        y_coords : List[str]
            list of desired y-axis cube coordinates for the plots
        """
        
        # check the number of coords match the requested number of plots
        x_coords_length = len(x_coords)
        y_coords_length = len(y_coords)

        if x_coords_length == y_coords_length:
            self.plot_count = x_coords_length
            # iterate over each requested plot
            for i in range(x_coords_length):
                if self.__is_coord(x_coords[i]) and self.__is_coord(y_coords[i]):
                    # add each coord to the valid list
                    self.x_plotting_coords.append(x_coords[i])
                    self.y_plotting_coords.append(y_coords[i])
                else:
                    print(f'Either {x_coords[i]} or {y_coords[i]} is not a valid coordinate of the cube.')
                    break
        else:
            print(f"Length of plotting variables in horizontal ({x_coords_length}) and vertical ({y_coords_length}) axes are not equal.")


    def get_plot_count(self) -> int:
        """
        Return the requested plot count from this cube
        """
        return self.plot_count


    def create_slices(self) -> None:
        """
        Create slices for the animator class
        """
        self.slices = []
        for i in range(self.plot_count):
            self.slices.append(self.cube.slices([self.x_plotting_coords[i], self.y_plotting_coords[i]]))

    
    def get_next_slice(self, plot_counter: int):
        """
        Return the next slice from the requested slice list.

        plot_counter : int
            0 <= plot_counter < plot_count
        """
        return next(self.slices[plot_counter])


    def set_projection(self, projection: ccrs.Projection) -> None:
        """
        Set a desired cartopy projection

        projection : ccrs.Projection
            the desired projection to be used when plotting
        """
        self.projection = projection

    
    def get_projection(self) -> Union[ccrs.Projection, None]:
        """
        Returns the projection. Used only by the Animator class.
        """
        return self.projection