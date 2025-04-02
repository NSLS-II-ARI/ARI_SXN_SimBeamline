import numpy as np
import random
import xrt.backends.raycing.sources as xrt_source
import xrt.backends.raycing.apertures as xrt_aperture
import xrt.backends.raycing.screens as xrt_screen
import xrt.backends.raycing.oes as xrt_oes


class TestBase:
    """Base class that provides input values needed for XRT models.

    This is used to construct test variables so that the XRT model can be run
    without the caproto IOC.

    Parameters
    ----------
    inputs : dict
        A dictionary mapping names for each 'input' attribute required to an
        initial 'value' for the attribute.
    """
    def __init__(self, inputs):
        for name, value in inputs.items():
            setattr(self, name, value)


class Test4Slit(TestBase):
    """A class that provides input/output values needed for XRT slit models.

    This is used to construct test variables so that the slits in the XRT model
    can be run without the caproto IOC.

    """

    def __init__(self):
        super().__init__({'top': 20, 'bottom': -20,
                          'inboard': -20, 'outboard': 20})

        self.currents = [random.uniform(0.0, 1E-6),
                         random.uniform(0.0, 1E-6),
                         random.uniform(0.0, 1E-6),
                         random.uniform(0.0, 1E-6)]


class TestDiagnostic(TestBase):
    """A class that provides input/output values needed for XRT diag models.

    This is used to construct test variables so that the diagnostics in the XRT
    model can be run without the caproto IOC.

    """
    def __init__(self):
        super().__init__({'multi_trans': 50, 'yag_trans': 0})
        # provides the array_size values that define the output image array
        self.array_size0 = 1280
        self.array_size1 = 960
        # provides the output array as a random np array.
        self.camera = np.random.rand(self.array_size0, self.array_size1)
        self.currents = [random.uniform(0.0, 1E-6),
                         0, 0, 0]


class TestMirror(TestBase):
    """A class that provides input/output values needed for XRT mirror models.

    This is used to construct test variables so that the Mirrors in the XRT
    model can be run without the caproto IOC.

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    baffles = Test4Slit()
    diagnostic = TestDiagnostic()


class TestM1(TestMirror):
    """
    Adds a function that converts the coarse and fine Ry angles into a single
    angle.
    """

    @property
    def Ry(self):  # function used to calculate the combined M1 Ry
        calculated_Ry = self.Ry_coarse + self.Ry_fine
        return calculated_Ry

    @Ry.setter
    def Ry(self, set_point): # function used to take input from command line
        self.Ry_fine = set_point
        self.Ry_coarse = 0 # Make sure the Ry is the total value


# Transformation of coordinates between XRT and NSLS-II.
transform_NSLS2XRT = {'inboard': np.array([[0, -1.0, 0], [0, 0, 1.0],
                                           [-1.0, 0, 0]]),
                      'outboard': np.array([[0, 1.0, 0], [0, 0, 1.0],
                                            [1.0, 0, 0]]),
                      'downward': np.array([[1.0, 0, 0], [0, 0, 1.0],
                                            [0, -1.0, 0]]),
                      'upward': np.array([[-1.0, 0, 0], [0, 0, 1.0],
                                          [0, 1.0, 0]])}


def _update_parameters(obj, updated=False):
    """
    A generic method that updates the XRT model parameters.

    Used in most of the custom XRT components below to update the parameters
    in the model based on the links in the objects parameter_map dictionary.

    Parameters
    ----------
    obj : object
        The custom XRT object whose parameters are to be updated.
    updated: a boolean, i.e., False (by default) or True.
        Boolean that indicates if any of the parameters where updated,
        Potentially modified and returned.

    Returns
    -------
    updated : Boolean
        Potentially modified the input parameter updated if the update
        indicates a re-activation required.

    """
    for parameter, origin in obj._parameter_map.items():
        if parameter == 'center':
            origin = np.dot(obj._transform_matrix, origin)
            origin[1] += obj._y_offset
            origin = tuple(origin)
            current = getattr(obj, 'center')
            if origin != current:
                updated = True
                setattr(obj, 'center', origin)
        elif parameter == 'angles':
            current = tuple([getattr(obj, angle)
                             for angle in ['pitch', 'roll', 'yaw']])
            if origin != current:
                updated = True
                for i, angle in enumerate(['pitch', 'roll', 'yaw']):
                    setattr(obj, angle, origin[i])
        else:
            if getattr(obj, parameter) != origin:
                updated = True
                setattr(obj, parameter, origin)

    return updated


def _parse_parameter_map(default_map):
    """
    A method that parses the default parameter map into a parameter map.

    Parameters
    ----------
    default_map : dict
        The default parameter map to parse
    """
    out = {}
    for key, value in default_map.items():
        if type(value) is dict:  # value is a dictionary
            temp_out = []
            for axis, val in value.items():
                if type(val) is float or type(val) is int:
                    temp_out.append(val)
                elif type(val) in [list, tuple] and len(val) == 2:
                    temp_out.append(getattr(val[0], val[1]))
                else:
                    raise ValueError(f'Invalid value for {key} in '
                                     f'{default_map}')
            out[key] = tuple(temp_out)
        elif type(value) is float or type(value) is int:
            out[key] = value
        elif type(value) in [list, tuple] and len(value) == 2:
            out[key] = getattr(value[0], value[1])
        else:
            raise ValueError(f'Invalid value for {key} in '
                             f'{default_map}')

    return out


class ID29Source(xrt_source.GeometricSource):
    """
    A Geometric Source inherited from XRT.

    Update the xrt.backends.raycing.sources.GeometricSource with an activate
    method and beamOut, transform_matrix and parameter_map attributes. All are
    described below.

    Parameters
    ----------
    parameter_map : dict
        A dictionary mapping xrt parameters to python objects that return the
        parameters values. As an example, assuming the use of the TestMirror
        class in this package as the way to update parameters for an ID29OE
        object the dictionary may look like:
         ```
         mirror = TestMirror({'Ry_coarse': np.radians(2),
                              'Ry_fine': 0, 'Rz': 0,
                              'x': 0, 'y': 0}

         def Ry():
            calculated_Ry = mirror.Ry_coarse + mirror.Ry_fine
            return calculated_Ry

         parameter_map = {'center':{'x':(mirror,'x'), 'y':(mirror,'y'),'z':0),
                          'angles':{'pitch':0, 'roll':(mirror,'Ry'),
                                    'yaw': (mirror,'Rz')}

         here 'center' is (x, y, z) and 'angles' is (pitch, roll, yaw) in XRT
         global coordinates

         here 'center' is (x, y, z) and 'angles' is (pitch, roll, yaw) in XRT
         global coordinates
         ```

        Notes:
        1.  Only parameters that can be updated for the given device should be
            included, for the 'center' and 'angle' parameters these should be
            provided in NSLS-II coordinates.
        2.  The parameters can be provided as either a function that returns a
            value (with no args/kwargs) or as an object that returns a value.
        3.  For the 'center' xrt parameter if a particular entry is not settable
            then the fixed value should be included as a float or int.
        4.  The three 'angles' Rx, Ry and Rz should be provided as a 3 element
            list (called 'angles' as is done for 'center', with the default
            value, as a float of int, used for any non settable angles.
    center : list or tuple.
        A 3 element list or tuple that defines the x, y, z position of the
        center element in XRT coordinates, i.e., (x, y, z).
    transform_matrix : np.array
        A 3x3 numpy array that is the transformation matrix between the input
        'centre' and 'angle' coordinate system and the xrt coordinate system.
    *args : arguments
        The arguments passed to the parent
        'xrt.backends.raycing.sources.GeometricSource' class.

    **kwargs : keyword arguments
        The keyword arguments passed to the parent
        'xrt.backends.raycing.sources.GeometricSource' class.

    Attributes
    ----------
    *attributes : many
        The attributes of the parent
        `xrt.backends.raycing.sources.GeometricSource` class.
    beamOut :
        Output of self.shine() method call inside self.activate.

    Methods
    -------
    *methods : many
        The methods of the parent `xrt.backends.raycing.sources.GeometricSource`
        class.
    activate(updated=False) :
        A method that updates the beamOut attribute if any parameters it uses
        have been changed or if updated=True.
    """
    def __init__(self, parameter_map, *args, center=(0, 0, 0),
                 transform_matrix=np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                 **kwargs):
        super().__init__(*args, center=center, **kwargs)
        self.beamOut = None  # Output in global coordinate!
        self._default_parameter_map = parameter_map
        self._transform_matrix = transform_matrix
        self._y_offset = center[1]

    @property
    def _parameter_map(self):
        """
        An attribute-like method that returns an updated parameter_map.
        """
        return _parse_parameter_map(self._default_parameter_map)

    @_parameter_map.setter
    def _parameter_map(self, new_parameter_map): # used to take input manually
        self._default_parameter_map = new_parameter_map

    def activate(self, updated=False):
        """
        A method adding or modifying the beamOut attribute.

        This method modifies the Object of beamline source if any parameters had
        been changed and then updates the beamOut accordingly.

        Parameters
        ----------

        updated: a boolean, i.e., False (by default) or True.
            The boolean indicates the beamOut needs to be updated as the source
            has been modified. Potentially modified and returned.

        Returns
        -------
        updated : Boolean
            Potentially modified the input parameter updated if the update
            indicates a re-activation required.
        """

        # TODO: Need to add the 'energies' tuple, with the form (energy,
        #  bandwidth), to this. Consider a look-up table for the bandwidth.
        updated = _update_parameters(self, updated)

        if updated:
            self.beamOut = self.shine()

        return updated


class ID29OE(xrt_oes.OE):
    """
    A modified OE class including the beamIn and beamOut attributes.

    Updates the xrt.backends.raycing.oes.OE with an activate method and
    beamIn, beamOut, upstream, transform_matrix and parameter_map attributes.
    All are described below.

    Parameters
    ----------
    upstream : arguments, such as m1, pgm ...
        The argument takes the beamline component that has Beam Object.
    parameter_map : dict
        A dictionary mapping xrt parameters to python objects that return the
        parameters values. As an example, assuming the use of the TestMirror
        class in this package as the way to update parameters for an ID29OE
        object the dictionary may look like:
         ```
         mirror = TestMirror({'Ry_coarse': np.radians(2),
                              'Ry_fine': 0, 'Rz': 0,
                              'x': 0, 'y': 0})

         def Ry():
            calculated_Ry = mirror.Ry_coarse + mirror.Ry_fine
            return calculated_Ry

         parameter_map = {'center':{'x':(mirror,'x'), 'y':(mirror,'y'),'z':0),
                          'angles':{'pitch':0, 'roll':(mirror,'Ry'),
                                    'yaw': (mirror,'Rz')}

         here 'center' is (x, y, z) and 'angles' is (pitch, roll, yaw) in XRT
         global coordinates
         ```

        Notes:
        1.  Only parameters that can be updated for the given device should be
            included, for the 'center' and 'angle' parameters these should be
            provided in NSLS-II coordinates.
        2.  The parameters can be provided as either a function that returns a
            value (with no args/kwargs) or as an object that returns a value.
        3.  For the 'center' xrt parameter if a particular entry is not settable
            then the fixed value should be included as a float or int.
        4.  The three 'angles' Rx, Ry and Rz should be provided as a 3 element
            list (called 'angles' as is done for 'center', with the default
            value, as a float of int, used for any non settable angles.
    center : list or tuple.
        A 3 element list or tuple that defines the x, y, z position of the
        center element in XRT coordinates, i.e., (x, y, z).
    transform_matrix : np.array
        A 3x3 numpy array that is the transformation matrix between the input
        'centre' and 'angle' coordinate system and the xrt coordinate system.
    *args : arguments
        The arguments passed to the parent 'xrt.backends.raycing.oes.OE' class.

    **kwargs : keyword arguments
        The keyword arguments passed to the parent 'xrt.backends.raycing.oes.OE'
        class.

    Attributes
    ----------
    *attributes : many
        The attributes of the parent `xrt.backends.raycing.oes.OE` class.
    beamIn :
        Input to use in the self.reflect() method call inside self.activate
        global coordinate.
    beamOut :
        Output of self.reflect() method call inside self.activate in XRT global
        co-ordinates.
    beamOutloc :
        Output of self.reflect() method call inside self.activate in XRT local
        co-ordinates.

    Methods
    -------
    *methods : many
        The methods of the parent `xrt.backends.raycing.oes.OE` class.

    activate(updated=False) :
        A method that updates the beamOut attribute if any parameters it uses
        have been changed or if updated=True.
    """

    def __init__(self, parameter_map, *args, center=(0, 0, 0),
                 transform_matrix=np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                 upstream=None, **kwargs):
        super().__init__(*args, center=center, **kwargs)

        self.beamIn = None  # Input in global coordinate!
        self.beamOut = None  # Output in global coordinate!
        self.beamOutloc = None  # Output in local coordinate!
        self._transform_matrix = transform_matrix
        self._default_parameter_map = parameter_map
        self._upstream = upstream  # Object from modified XRT
        self._y_offset = center[1]

    @property
    def _parameter_map(self):
        """
        An attribute-like method that returns an updated parameter_map.
        """
        return _parse_parameter_map(self._default_parameter_map)

    @_parameter_map.setter
    def _parameter_map(self, new_parameter_map): # used to take input manually
        self._default_parameter_map = new_parameter_map

    def activate(self, updated=False):
        """
        A method adding or modifying the beamOut attribute.

        This method modifies the Object of beamline optics if any parameters had
        been changed and then updates the outcome of Beam Object accordingly.

        Parameters
        ----------
        updated: a boolean, i.e., False (by default) or True.
        The True means the outcome of Beam Object needs to be updated
        as the beamline optics has been modified.

        Returns
        -------
        updated : Boolean
            Potentially modified the input parameter updated if the update
            indicates a re-activation required.
        """
        updated = _update_parameters(self, updated)

        if updated:
            self.beamIn = getattr(self._upstream, 'beamOut')
            self.beamOut, self.beamOutloc = self.reflect(self.beamIn)

        return updated


class ID29Aperture(xrt_aperture.RectangularAperture):
    """
    A modified Aperture class including the beamIn and beamOut attributes.

    Updates the xrt.backends.raycing.apertures.RectangularAperture with an
    activate method and beamIn, beamOut, upstream, transform_matrix and
    parameter_map attributes. All are described below.

    Parameters
    ----------
    upstream : arguments, such as m1, pgm ...
        The argument takes the beamline component that has Beam Object.
    parameter_map : dict
        A dictionary mapping xrt parameters to python objects that return the
        parameters values. As an example, assuming the use of the TestMirror
        class in this package as the way to update parameters for an ID29OE
        object the dictionary may look like:
         ```
         mirror = TestMirror({'Ry_coarse': np.radians(2),
                              'Ry_fine': 0, 'Rz': 0,
                              'x': 0, 'y': 0}

         def Ry():
            calculated_Ry = mirror.Ry_coarse + mirror.Ry_fine
            return calculated_Ry


         parameter_map = {'center':{'x':(mirror,'x'), 'y':(mirror,'y'),'z':0),
                          'angles':{'pitch':0, 'roll':(mirror,'Ry'),
                                    'yaw': (mirror,'Rz')}

         here 'center' is (x, y, z) and 'angles' is (pitch, roll, yaw) in XRT
         global coordinates

         here 'center' is (x, y, z) and 'angles' is (pitch, roll, yaw) in XRT
         global coordinates.
         ```

        Notes:
        1.  Only parameters that can be updated for the given device should be
            included, for the 'center' and 'angle' parameters these should be
            provided in NSLS-II coordinates.
        2.  The parameters can be provided as either a function that returns a
            value (with no args/kwargs) or as an object that returns a value.
        3.  For the 'center' xrt parameter if a particular entry is not settable
            then the fixed value should be included as a float or int.
        4.  The three 'angles' Rx, Ry and Rz should be provided as a 3 element
            list (called 'angles' as is done for 'center', with the default
            value, as a float of int, used for any non settable angles.
    center : list or tuple.
        A 3 element list or tuple that defines the x, y, z position of the
        center element in XRT coordinates, i.e., (x, y, z).
    transform_matrix : np.array
        A 3x3 numpy array that is the transformation matrix between the input
        'centre' and 'angle' coordinate system and the xrt coordinate system.
    *args : arguments
        The arguments passed to the parent
        'xrt.backends.raycing.apertures.RectangularAperture' class.
    **kwargs : keyword arguments
        The keyword arguments passed to the parent
        'xrt.backends.raycing.apertures.RectangularAperture' class.

    Attributes
    ----------
    *attributes : many
        The attributes of the parent
        `xrt.backends.raycing.apertures.RectangularAperture` class.
    beamIn :
        Input to use in the self.propagate() method call inside self.activate
        global coordinate.
    beamOut :
        Output of self.propagate() method call inside self.activate.


    Methods
    -------
    *methods : many
        The methods of the parent `xrt.backends.raycing.apertures
        `RectangularAperture` class.
    activate(updated=False) :
        A method that updates the beamOut attribute if any parameters it uses
        have been changed or if updated=True.

    """
    def __init__(self, parameter_map, *args, center=(0, 0, 0),
                 transform_matrix=np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                 upstream=None, **kwargs):
        super().__init__(*args, center=center, **kwargs)

        self.beamIn = None  # Input in global coordinate!
        self.beamOut = None  # Output in global coordinate!
        self._transform_matrix = transform_matrix
        self._default_parameter_map = parameter_map
        self._upstream = upstream  # Object from modified XRT
        self._y_offset = center[1]

    @property
    def _parameter_map(self):
        """
        An attribute-like method that returns an updated parameter_map.
        """
        return _parse_parameter_map(self._default_parameter_map)

    @_parameter_map.setter
    def _parameter_map(self, new_parameter_map): # used to take input manually
        self._default_parameter_map = new_parameter_map

    def activate(self, updated=False):
        """
        A method adding or modifying the beamOut attribute.

        This method modifies the Object of beamline aperture if any parameters
        had been changed and then updates the outcome of Beam Object
        accordingly.


        Parameters
        ----------
        updated: a boolean, i.e., False (by default) or True.
        The Ture means the outcome of Beam Object needs to be updated
        as the beamline aperture has been modified.

        Returns
        -------
        updated : Boolean
            Potentially modified the input parameter updated if the update
            indicates a re-activation required.

        """
        updated = _update_parameters(self, updated)

        if updated:
            self.beamIn = getattr(self._upstream, 'beamOut')
            self.beamOut = self.propagate(self.beamIn)

        return updated


class ID29Screen(xrt_screen.Screen):
    """
    A modified Screen class including the beamIn and beamOut attributes.

    Updates the xrt.backends.raycing.screens.Screen with an activate method and
    beamIn, beamOut, upstream, transform_matrix and parameter_map attributes.
    All are described below.

    Parameters
    ----------
    upstream : arguments, such as m1, pgm ...
        The argument takes the beamline component that has Beam Object.
    parameter_map : dict
        A dictionary mapping xrt parameters to python objects that return the
        parameters values. As an example, assuming the use of the TestMirror
        class in this package as the way to update parameters for an ID29OE
        object the dictionary may look like:
         ```
         mirror = TestMirror({'Ry_coarse': np.radians(2),
                              'Ry_fine': 0, 'Rz': 0,
                              'x': 0, 'y': 0}

         def Ry():
            calculated_Ry = mirror.Ry_coarse + mirror.Ry_fine
            return calculated_Ry

         parameter_map = {'center':{'x':(mirror,'x'), 'y':(mirror,'y'),'z':0),
                          'angles':{'pitch':0, 'roll':(mirror,'Ry'),
                                    'yaw': (mirror,'Rz')}

         here 'center' is (x, y, z) and 'angles' is (pitch, roll, yaw) in XRT
         global coordinates

         here 'center' is (x, y, z) and 'angles' is (pitch, roll, yaw) in XRT
         global coordinates.
         ```

        Notes:
        1.  Only parameters that can be updated for the given device should be
            included, for the 'center' and 'angle' parameters these should be
            provided in NSLS-II coordinates.
        2.  The parameters can be provided as either a function that returns a
            value (with no args/kwargs) or as an object that returns a value.
        3.  For the 'center' xrt parameter if a particular entry is not settable
            then the fixed value should be included as a float or int.
        4.  The three 'angles' Rx, Ry and Rz should be provided as a 3 element
            list (called 'angles' as is done for 'center', with the default
            value, as a float of int, used for any non settable angles.
    center : list or tuple.
        A 3 element list or tuple that defines the x, y, z position of the
        center element in XRT coordinates, i.e., (x, y, z).
    transform_matrix : np.array
        A 3x3 numpy array that is the transformation matrix between the input
        'centre' and 'angle' coordinate system and the xrt coordinate system.
    *args : arguments
        The arguments passed to the parent
        'xrt.backends.raycing.screens.Screen' class.
    **kwargs : keyword arguments
        The keyword arguments passed to the parent
        'xrt.backends.raycing.screens.Screen' class.

    Attributes
    ----------
    *attributes : many
        The attributes of the `xrt.backends.raycing.screens.Screen` class.
    beamIn :
        Input to use in the self.expose() method call inside self.activate
        global coordinate.
    beamOut :
        Output of self.expose() method call inside self.activate.

    Methods
    -------
    *methods : many
        The methods of the parent `xrt.backends.raycing.screens.Screen` class.

    activate(updated=False) :
        A method that updates the beamOut attribute if any parameters it uses
        have been changed or if updated=True.

    """
    def __init__(self, parameter_map, *args, center=(0, 0, 0),
                 transform_matrix=np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
                 upstream=None, **kwargs):
        super().__init__(*args, center=center, **kwargs)

        self.beamIn = None  # Input in global coordinate!
        self.beamOut = None  # Output in global coordinate!
        self._transform_matrix = transform_matrix
        self._default_parameter_map = parameter_map
        self._upstream = upstream  # Object from modified XRT
        self._y_offset = center[1]

    @property
    def _parameter_map(self):
        """
        An attribute-like method that returns an updated parameter_map.
        """
        return _parse_parameter_map(self._default_parameter_map)

    @_parameter_map.setter
    def _parameter_map(self, new_parameter_map): # used to take input manually
        self._default_parameter_map = new_parameter_map

    def activate(self, updated=False):
        """

        A method adding or modifying the beamOut attribute.

        This method modifies the Object of beamline screen if any parameters
        had been changed and then updates the outcome of Beam Object
        accordingly.


        Parameters
        ----------
        updated: a boolean, i.e., False (by default) or True.
        True means the outcome of Beam Object needs to be updated
        as the beamline aperture has been modified.

        Returns
        -------
        updated : Boolean
            Potentially modified the input parameter updated if the update
            indicates a re-activation required.

        """
        updated = _update_parameters(self, updated)

        if updated:
            self.beamIn = getattr(self._upstream, 'beamOut')
            self.beamOut = self.expose(self.beamIn)

        return updated
