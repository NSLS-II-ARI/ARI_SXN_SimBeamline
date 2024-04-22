from caproto.server import PVGroup, SubGroup, ioc_arg_parser, run
from four_blade_electrometer import FourBladeElectrometer
from motor_record import MotorRecord
from textwrap import dedent


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
    top = SubGroup(MotorRecord, velocity=0.1, acceleration=1.0,
                   motion_range={'low': -1, 'high': 20},
                   prefix=':top')
    bottom = SubGroup(MotorRecord, velocity=0.1, acceleration=1.0,
                      motion_range={'low': -20, 'high': 1},
                      prefix=':bottom')
    inboard = SubGroup(MotorRecord, velocity=0.1, acceleration=1.0,
                       motion_range={'low': -20, 'high': 1},
                       prefix=':inboard')
    outboard = SubGroup(MotorRecord, velocity=0.1, acceleration=1.0,
                        motion_range={'low': -1, 'high': 20}, tick_rate_hz=10.,
                        prefix=':outboard')

    current = SubGroup(FourBladeElectrometer, prefix=':current')


# Add some code to start a version of the server if this file is 'run'.
if __name__ == "__main__":
    ioc_options, run_options = ioc_arg_parser(
        default_prefix="BaffleSlit",
        desc=dedent(BaffleSlit.__doc__))
    ioc = BaffleSlit(**ioc_options)
    run(ioc.pvdb, **run_options)
