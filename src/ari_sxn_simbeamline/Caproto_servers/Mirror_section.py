"""
This file will contain some generic caproto PVGroups used to generate the beamline
Caproto IOC servers
"""
from caproto.ioc_examples.fake_motor_record import FakeMotor
from caproto.server import PVGroup, SubGroup, ioc_arg_parser, run
from textwrap import dedent


class Mirror(PVGroup):
    """
    A PVGroup that generates the PVs associated with a beamline mirror system.

    This class should be used to define the mirror systems for a beamline, each
    mirror system will consist of motors for each mirror axis as well as the
    related vacuum component PVs.

    TODO:
    1. Decide if we want to have this include the baffleslit and diagnostic
       components as well:
        - This may help create a cohesive connection between them but also blurs
          the lines between vacuum sections and physical devices.
    2. Add the vacuum component (gauges, pumps, valves, ....).
        - This may require defining vacuum component PVGroups.

    Parameters
    ----------
    *args : list
        The arguments passed to the PVGroup parent class
    axes : {axis_name:{key_1:val_1, ... ,key_n,val_n}}, optional
        A dictionary mapping axis names to a 'parameter' dictionary of args/kwargs
        passed to the caproto.ioc_examples.fake_motor_record.FakeMotor PVGroup for
        the given axis. See the caproto.ioc_examples.fake_motor_record.FakeMotor
        for a description of available parameters and their descriptions. An
        example with a single (pitch) axes would be:
        axes={'pitch':{'velocity':0.1, 'precision':3, 'acceleration'=1.0,
                       'resolution'=1E-6,'user_limits'=(0.0,100.0),
                       'tick_rate_hz'=10.}}
    **kwargs : list, optional
        The Keyword arguments passed to the PVGroup parent class
    """

    def __init__(self, *args, axes, **kwargs):
        super().__init__(*args, **kwargs)  # call the PVGroup __init__ function
        for axis_name, axis_kwargs in axes.items():  # create the axis attributes
            setattr(self, axis_name, SubGroup(FakeMotor, **axis_kwargs,
                                              doc=f'The {axis_name} mirror axis'))


# Add some code to start a version of the server if this file is 'run'.
if __name__ == "__main__":
    axes_params = {'velocity': 0.1, 'precision': 3, 'acceleration': 1.0,
                   'resolution': 1E-6, 'user_limits': (0.0, 100.0),
                   'tick_rate_hz': 10.}
    default_axes = {'x': axes_params, 'y': axes_params, 'z': axes_params,
                    'pitch': axes_params, 'yaw': axes_params, 'roll': axes_params}
    ioc_options, run_options = ioc_arg_parser(
        default_prefix="Beamline:M1:",
        desc=dedent(Mirror.__doc__))
    ioc = Mirror(**ioc_options, axes=default_axes)
    run(ioc.pvdb, **run_options)
