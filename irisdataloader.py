import iris

class IrisDataLoader():
    """
    Loads Iris cubes from file and reads phenomenon names
    """
    def __init__(self, path: str) -> None:
        self.__set_path(path)
        self.__read_cubes()
        self.__find_cube_standard_names()
        self.__find_cube_long_names()


    def __set_path(self, path: str) -> None:
        """
        Set path to the data file

        path : str
            path to file
        """
        self.path = path


    def __read_cubes(self) -> None:
        "Load the data at the path location"
        self.cube_list = iris.load(self.path)


    def __find_cube_standard_names(self) -> None:
        "Collect the standard names and count of the cubes"
        self.cube_standard_names = []
        self.cube_count = 0
        for cube in self.cube_list:
            self.cube_standard_names.append(cube.standard_name)
            self.cube_count += 1


    def __find_cube_long_names(self) -> None:
        "Collect the long names"
        self.cube_long_names = []
        for cube in self.cube_list:
            self.cube_long_names.append(cube.long_name)

        
    def get_cube_list(self) -> list:
        return self.cube_list


    def get_cube_names(self) -> dict:
        return {"standard_names":self.cube_standard_names, "long_names" : self.cube_long_names}


    def get_cube_count(self) -> int:
        return self.cube_count

