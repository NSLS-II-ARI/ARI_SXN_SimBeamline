"""
This file will contain some generic caproto PVGroups used to generate the beamline
Caproto IOC servers
"""
from caproto.ioc_examples.fake_motor_record import FakeMotor
from caproto.server import PVGroup, SubGroup, pvproperty, ioc_arg_parser, run
from textwrap import dedent


class FourBladeCurrent(PVGroup):
    """
    A PVGroup that generates the PVs associated with the 4 blade electrometer.

    This class should be used to define the PVs for the 4 blade electrometers used
    in the ARI and SXN beamlines for the Baffle slits.

    TODO:
    1. Work out how we want to update the returned current values based on the position
    of the blades and the upstream mirrors.
    2. Decide how we want to represent the electrometer PVs (and which ones are important).
        - I suspect we will need some extra PVs (like dwell/acquisition time, ....) as well
        as others. Take a look at the NSLS-II electrometer ophyd device for a list.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # call the PVGroup __init__ function

    # Add the current PVs
    top = pvproperty(value=3E-6, name=':top', read_only=True)
    bottom = pvproperty(value=3E-6, name=':bottom', read_only=True)
    inboard = pvproperty(value=3E-6, name=':inboard', read_only=True)
    outboard = pvproperty(value=3E-6, name=':outboard', read_only=True)


class BaffleSlit(PVGroup):
    """
    A PVGroup that generates the PVs associated with the ARI M1 mirror system.

    This class should be used to define the Baffle Slit system PVs for the baffle slits
    used in the ARI and SXN beamlines. It will consist of PVs for each of the associated
    motors for each baffle as well as the photo-current PVs from each of the blades.

    TODO:
    1. Work out how we want to define the area detector PVs, including how we 'update'
       the photo-current PVs based from each of the blades when the mirror and/or baffles
       are moved.
    2. Decide how we want to implement the motor-record PVs.
        - See the section in the AriM1Mirror PVGroup below on this topic.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # call the PVGroup __init__ function

    # Add the baffle motor PVs.
    top = SubGroup(FakeMotor, velocity=0.1, precision=6E-3, acceleration=1.0,
                   resolution=6E-3, user_limits=(-1, 20), tick_rate_hz=10.,
                   prefix=':top')
    bottom = SubGroup(FakeMotor, velocity=0.1, precision=6E-3, acceleration=1.0,
                      resolution=6E-3, user_limits=(-20, 1), tick_rate_hz=10.,
                      prefix=':bottom')
    inboard = SubGroup(FakeMotor, velocity=0.1, precision=6E-3, acceleration=1.0,
                       resolution=6E-3, user_limits=(-20, 1), tick_rate_hz=10.,
                       prefix=':inboard')
    outboard = SubGroup(FakeMotor, velocity=0.1, precision=6E-3, acceleration=1.0,
                        resolution=6E-3, user_limits=(-1, 20), tick_rate_hz=10.,
                        prefix=':outboard')

    current = SubGroup(FourBladeCurrent, prefix=':current')


class Diagnostic(PVGroup):
    """
    A PVGroup that generates the PVs associated with the ARI and SXN Diagnostic units.

    This class should be used to define the ARI & SXN Diagnostic unit PVs. It will
    consist of PVs for each of the motors (main translation stage and the YaG screen
    translation stage) as well as those related to the electrometer for the photo-diode
    and the camera.

    TODO:
    1. Work out how we want to define the area detector PVs, including how we 'update'
       the photo-current PVs for the photodiode and the image seen on the camera.
    2. Decide how we want to implement the motor-record PVs.
        - See the section in the AriM1Mirror PVGroup below on this topic.
    3. Decide how we want to represent the electrometer PVs (and which ones are important).
        - see Baffleslit PVGroup for more info.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # call the PVGroup __init__ function

    # Add the motor PVs
    multi_trans = SubGroup(FakeMotor, velocity=0.1, precision=6E-3, acceleration=1.0,
                           resolution=6E-3, user_limits=(-1, 20), tick_rate_hz=10.,
                           prefix=':multi_trans')

    yag_trans = SubGroup(FakeMotor, velocity=0.1, precision=6E-3, acceleration=1.0,
                         resolution=6E-3, user_limits=(-1, 20), tick_rate_hz=10.,
                         prefix=':yag_trans')

    # Add the photodiode PVs
    photodiode = pvproperty(value=3E-6, name=':photodiode', read_only=True)

    # TODO: Add the camera Areadetector PV.
    # camera = .........


class AriM1Mirror(PVGroup):
    """
    A PVGroup that generates the PVs associated with the ARI M1 mirror system.

    This class should be used to define the M1 mirror system PVs for the ARI beamline.
    It will consist of PVs for each of the motors for each mirror axis as well as the
    related vacuum component PVs.

    TODO:
    1. Decide if we want to have this include the baffleslit and diagnostic
       components as well:
        - This may help create a cohesive connection between them but also blurs
          the lines between vacuum sections and physical devices.
    2. Add the vacuum component (gauges, pumps, valves, ....).
        - Temporary read only PVs have been created but I need to see what other PVs
        are associated with this hardware that we may want to simulate.
    3. Decide how we want to implement the motor-record PVs.
        - Currently I use the FakeMotor PVGroup from the caproto source code, this
        does not have all of the required PVs for a motor record and so will need
        to be replaced.
        - Options I think are: 1, to use the C++ based Epics motor record simulated
        IOC or 2, to write our own Epics motor record IOC in caproto with only the
        minimum required Epics PVs for our applications (see motor record ophyd device
        for required PVs).

    Parameters
    ----------
    *args : list
        The arguments passed to the PVGroup parent class.
    **kwargs : list, optional
        The Keyword arguments passed to the PVGroup parent class.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # call the PVGroup __init__ function

    # Add the mirror motor PVs.
    Ry_coarse = SubGroup(FakeMotor, velocity=0.1, precision=6E-5, acceleration=1.0,
                         resolution=6E-5, user_limits=(-3.15, -1.15), tick_rate_hz=10.,
                         prefix=':Ry_coarse')
    Ry_fine = SubGroup(FakeMotor, velocity=0.1, precision=6E-7, acceleration=1.0,
                       resolution=6E-7, user_limits=(-0.03, 0.03), tick_rate_hz=10.,
                       prefix=':Ry_fine')
    Rz = SubGroup(FakeMotor, velocity=0.1, precision=6E-5, acceleration=1.0,
                  resolution=6E-5, user_limits=(-2.3, 2.3), tick_rate_hz=10.,
                  prefix=':Rz')
    x = SubGroup(FakeMotor, velocity=0.0001, precision=5., acceleration=1.0,
                 resolution=5., user_limits=(-10000., 10000.), tick_rate_hz=1E-3,
                 prefix=':x')
    y = SubGroup(FakeMotor, velocity=0.1, precision=5., acceleration=1.0,
                 resolution=5., user_limits=(-10000., 10000.), tick_rate_hz=10.,
                 prefix=':y')

    # Add the mirror chamber vacuum PVs.
    ccg = pvproperty(value=3E-10, name=':ccg', read_only=True)
    tcg = pvproperty(value=1E-4, name=':tcg', read_only=True)
    ip = pvproperty(value=4E-10, name=':ip', read_only=True)

    # Add the baffle slit PVs.
    baffle = SubGroup(BaffleSlit, prefix=':baffle')

    # Add the diagnostic PVs.
    diag = SubGroup(Diagnostic, prefix=':diag')


# Add some code to start a version of the server if this file is 'run'.
if __name__ == "__main__":
    ioc_options, run_options = ioc_arg_parser(
        default_prefix="ARI_M1",
        desc=dedent(AriM1Mirror.__doc__))
    ioc = AriM1Mirror(**ioc_options)
    run(ioc.pvdb, **run_options)
