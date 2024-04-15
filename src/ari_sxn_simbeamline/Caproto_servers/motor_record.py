from caproto.server import PVGroup, SubGroup, pvproperty, ioc_arg_parser, run
from textwrap import dedent


class MotorRecord(PVGroup):
    """
    A PVGroup that simulates an Epics Motor Record motor.
    
    This PVGroup simulates an Epics Motor Record motor IOC, it utilizes the velocity
    PV and the distance of travel required to determine the time that the motor will 
    take to make the move and uses the update_rate_hz PV (not part of an Epics Motor 
    Record) to determine how often it should update the .RBV PV during this time.

    NOTE: In the following discussion we will assume that the term 'unit(s)' refers to
    the physical units that the motor motion is measured in (i.e. mm, nm, deg., rad.,
    ...). This PVGroup is agnostic to what the actual unit is.
    
    TODO:
    1. Currently, this only has the PVs that are referenced in the ophyd.EpicsMotor
    device class, I should consider if other parameters are used for CSS pages and
    if we want to add all of them.
    
    Parameters
    ----------
    *args : list
        The arguments passed to the PVGroup parent class.
    velocity : float, optional
        A float that indicates the velocity, in units/s, that the simulated motor should
        move with. Default is 0.1 unit/s.
    precision : float, optional
        The precision of the motor positioning system, in units, the motion will be
        considered 'complete' when the .rbv PV is within 'precision' of the .val PV.
        Default is 1E-3.
    acceleration : float, optional
        A float that indicates the 'acceleration' of the motor, note that this is
        ignored when determining the time the motor move takes and is included only
        as it is included in an Epics motor record. Default is 1.
    resolution : float, optional
        A float that indicates the 'resolution'
    update_rate_hz : float, optional
        A float that indicates how many times per second the .rbv PV should be updated
        during the 'interval'. Default is 10.
    **kwargs : list, optional
        The Keyword arguments passed to the PVGroup parent class.
    """
    def __init__(self, *args, velocity=0.1, precision=1E-3, acceleration=1.0,
                 resolution=1e-6, user_limits=(0.0, 100.0), update_rate_hz=10, **kwargs):
        super().__init__(*args, **kwargs)  # call the PVGroup __init__ function


# Add some code to start a version of the server if this file is 'run'.
if __name__ == "__main__":
    ioc_options, run_options = ioc_arg_parser(
        default_prefix="MotorRecord",
        desc=dedent(MotorRecord.__doc__))
    ioc = MotorRecord(**ioc_options)
    run(ioc.pvdb, **run_options)
