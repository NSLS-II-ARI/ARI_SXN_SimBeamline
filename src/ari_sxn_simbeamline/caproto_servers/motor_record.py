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
                elif self.RBV+d_interval > self.limits['high']: # if we trip the high limit
                    self.high_limit_switch = 1
                    self.user_setpoint = self.user_readback
                    break
                elif self.RBV+d_interval < self.limits['low']: # if we trip the low limit
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


# Add some code to start a version of the server if this file is 'run'.
if __name__ == "__main__":
    ioc_options, run_options = ioc_arg_parser(
        default_prefix="MotorRecord",
        desc=dedent(MotorRecord.__doc__))
    ioc = MotorRecord(**ioc_options)
    run(ioc.pvdb, **run_options)
