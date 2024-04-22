from caproto.server import (pvproperty, PVGroup,
                            ioc_arg_parser, run)
from textwrap import dedent


class MotorRecord(PVGroup):
    """
    This is a PVGroup that mimics the PVs of a motor record IOC.

    The MotorRecord IOC that this PVGroup simulates is commonly employed
    in Epics for motor axes and other similar devices. In this case we
    intend to pass some 'default values' for a few parameters as well
    as simulate the 'time' it takes for a motor to move. How this is done
    is described below in the NOTES sections.

    Parameters
    ----------
    velocity : float
        The velocity that the motor should move at in units/s (units is the distance
        units of the motor axis). This is used in determining how fast the 'move' will
        happen.
    acceleration : float
        The acceleration value that the motor should return when asked in units/s/s
        (units is the distance units of the motor axis). This is provided as a dummy PV
        only.
    range : {'high':float, 'low': float}
        A dictionary mapping the high and low limits of motion (i.e. the 'range' of
        motion) to the keys 'high' and 'low'. This is used to trigger the high and
        low limit indicator PVs if the motor passes these values.
    min_time_step : float, optional
        A 'minimum' time step to divide the calculated time into for on-the-fly
        updating of the self.user_readback attribute (suffix.RBV PV). Default is 0.1.

    NOTES:
    1. Unless otherwise listed in the notes below the PVs generated are 'Dummy' PVs
    that are not modified by any inputs, or modify any other PVs, except their own
    values when they are updated.
    2. When the self.set_value attribute is updated (via the suffix.VAL PV) the sequence
    of events is:
        i. Set self.moving to 1 and self.done_moving to 0
        ii. Calculate time to move based on the relationship:
            total_time = abs(self.user_readback-self.user_setpoint)/self.velocity
        iii. Calculate the number of intervals (num_intervals) to include in the motion
        and the corresponding distance interval (interval) using the relations:
            num_intervals = floor(total_time/self.min_time_step)
            interval = (self.user_readback-self.user_setpoint)/(num_intervals+1)
        Note: here num_intervals is 1 less than required to reach the endpoint as the last
        step is done independently.
        iv. run a for loop as follows:
            for i in range(num_interval): # move each required interval and wait.
                wait(min_time_step)
                if self.stop = 1: # if the user requested the motion to stop
                    self.user_setpoint = self.user_readback
                    break
                elif self.RBV+d_interval > self.motion_range['high']: # if we trip the high limit
                    self.high_limit_switch = 1
                    self.user_setpoint = self.user_readback
                    break
                elif self.RBV+d_interval < self.motion_range['low']: # if we trip the low limit
                    self.low_limit_switch = 1
                    self.user_setpoint = self.user_readback
                    break
                else:
                    # The next 2 lines take care of us moving off a limit switch.
                    self.low_limit_switch = 0
                    self.high_limit_switch = 0

                    self.user_readback += interval

            self.user_readback = self.user_setpoint # Make the last move and clean up.
            self.moving = 0
            self.done_moving = 1

    """
    def __init__(self, velocity, acceleration, motion_range, *args,
                 min_time_step=0.1, **kwargs):
        super().__init__(*args, **kwargs)
        self.motion_defaults = {'velocity': velocity, 'acceleration': acceleration}
        self.motion_range = motion_range
        self.min_time_step = min_time_step


# Add some code to start a version of the server if this file is 'run'.
if __name__ == "__main__":
    ioc_options, run_options = ioc_arg_parser(
        default_prefix="MotorRecord",
        desc=dedent(MotorRecord.__doc__))
    ioc = MotorRecord(**ioc_options)
    run(ioc.pvdb, **run_options)
