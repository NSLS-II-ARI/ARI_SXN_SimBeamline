from caproto.server import (pvproperty, PVGroup, SubGroup,
                            ioc_arg_parser, run)
import math
from area_detector.plugin_base import PluginBase, pvproperty_rbv
import random
from area_detector.stats_plugin import StatsPlugin
from textwrap import dedent
import time


class QuadEM(PVGroup):
    """
    A PV Group that generates the PVs associated with a QuadEM device.

    The QuadEM device which this PVGroup simulates is a commonly employed 4 channel
    electrometer at NSLS-II. In this case passing in this version we randomly update
    the current values when the device is triggered via setting the 'acquire' PV to
    1 (see Notes below for details). This is done via the self._generate_current
    method, to add functionality other than a 'random' current sub-class this class and
    define a new self._generate_current method.

    NOTES:
    1. Unless otherwise listed in the notes below the PVs generated are 'Dummy' PVs
    that are not modified by any inputs, or modify any other PVs, except there own
    values when they are updated.
    2. When self.acquire is set to 1 the sequence of events is:
        i. record the initial time and set self.num_averaged to 0.
        ii.  calculate the current to be set on each channel using self._generate_current
        and write these to the self.current(x).mean_value attributes (x in [1,2,3,4])
        iii. if self.averaging_time has elapsed continue otherwise wait until it has.
        iv. set self.num_averaged to self.num_average and self.acquire to 0
    3. When self.averaging_time or self.integrating_time are updated self.num_average is
    updated using the following relationship:
        - self.num_average = floor(self.averaging_time/self.integration_time)

    TODO:
    1. Think about adding a 'Continuous' acquire_mode as well as the current
    'Single' acquire_mode.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # call the PluginBase __init__ function

    def _generate_current(self):
        """
        This method is used to generate a new set of current values for the QuadEM

        This method is used to generate a list of 4 values to be set to the different
        self.current(x).mean_value parameter, where x is in [1,2,3,4]. In this case
        we just return a random float for each current channel, but a sub-class of
        QuadEM with a different version of this function can output different currents
        as required. When creating this subclass the use of self.attribute can be used
        to interact with the various class attributes.

        Returns
        -------
        currents, [float, float, float, float].
            A list containing four floats which are the updated current values.
        """

        currents = []
        for j in range(4):
            currents.append(random.uniform(0.0, 1E-6))

        return currents

    def _reset_num_average(self):
        """This is a function that resets num_averaged when required.

        num_averaged requires to be reset whenever averaging_time or
        integration_time is changed. This function will be used as the
        putter hook for these.
        """
        self.num_average = math.floor(self.averaging_time/self.integration_time)

        return

    integration_time = pvproperty_rbv(name=':IntegrationTime', dtype=float, value=0.0004)
    averaging_time = pvproperty_rbv(name=':AveragingTime', dtype=float, value=1.0)
    model = pvproperty(name=':Model', dtype=str, read_only=True, value='NSLS_EM')
    firmware = pvproperty(name=':Firmware', dtype=str, read_only=True, value='0.1.04.04')
    acquire_mode = pvproperty_rbv(name=':AcquireMode', dtype=str, value='Single')
    acquire = pvproperty(name=':Acquire', dtype=int, value=True)
    read_format = pvproperty_rbv(name=':ReadFormat', dtype=str, value='')
    range = pvproperty_rbv(name=':Range', dtype=str, value='350 pC')
    ping_pong = pvproperty_rbv(name=':PingPong', dtype=str, value='Phase 0')
    num_channels = pvproperty_rbv(name=':NumChannels', dtype=int, value=4)
    geometry = pvproperty_rbv(name=':Geometry', dtype=str, value='Diamond')
    resolution = pvproperty_rbv(name=':Resolution', dtype=float, value=1E-12)
    bias_state = pvproperty_rbv(name=':BiasState', dtype=str, value='')

    hvs_readback = pvproperty(name=':HVSReadback', dtype=float, read_only=True, value=0)
    hvv_readback = pvproperty(name=':HVVReadback', dtype=float, read_only=True, value=0)
    hvi_readback = pvproperty(name=':HVIReadback', dtype=float, read_only=True, value=0)

    values_per_read = pvproperty_rbv(name=':ValuesPerRead', dtype=int, value=1)
    sample_time = pvproperty(name=':SampleTime_RBV', dtype=float, read_only=True, value=8E-4)
    num_average = pvproperty(name=':NumAverage_RBV', dtype=int, read_only=True, value=1250)
    num_averaged = pvproperty(name=':NumAveraged_RBV', dtype=int, read_only=True, value=1250)
    num_acquire = pvproperty_rbv(name=':NumAcquire', dtype=int, value=1)
    num_acquired = pvproperty(name=':NumAcquired_RBV', dtype=int, read_only=True, value=1)
    read_data = pvproperty(name=':ReadData', dtype=bool, read_only=True, value=False)
    ring_overflows = pvproperty(name=':RingOverflows', dtype=int, read_only=True, value=0)
    trigger_mode = pvproperty(name=':TriggerMode', dtype=str, value='')
    reset = pvproperty(name=':Reset', dtype=bool, value=False)

    current_name_1 = pvproperty(name=':CurrentName1', dtype=str, value='Current 1')
    current_offset_1 = pvproperty(name=':CurrentOffset1', dtype=float, value=0.0)
    compute_current_offset_1 = pvproperty(name=':ComputeCurrentOffset1', dtype=bool, value=False)
    current_scale_1 = pvproperty(name=':CurrentScale1', dtype=float, value=9.0)
    current1 = SubGroup(StatsPlugin, prefix=":Current1")

    current_name_2 = pvproperty(name=':CurrentName2', dtype=str, value='Current 2')
    current_offset_2 = pvproperty(name=':CurrentOffset2', dtype=float, value=0.0)
    compute_current_offset_2 = pvproperty(name=':ComputeCurrentOffset2', dtype=bool, value=False)
    current_scale_2 = pvproperty(name=':CurrentScale2', dtype=float, value=9.0)
    current2 = SubGroup(StatsPlugin, prefix=":Current2")

    current_name_3 = pvproperty(name=':CurrentName3', dtype=str, value='Current 3')
    current_offset_3 = pvproperty(name=':CurrentOffset3', dtype=float, value=0.0)
    compute_current_offset_3 = pvproperty(name=':ComputeCurrentOffset3', dtype=bool, value=False)
    current_scale_3 = pvproperty(name=':CurrentScale3', dtype=float, value=9.0)
    current3 = SubGroup(StatsPlugin, prefix=":Current3")

    current_name_4 = pvproperty(name=':CurrentName4', dtype=str, value='Current 4')
    current_offset_4 = pvproperty(name=':CurrentOffset4', dtype=float, value=0.0)
    compute_current_offset_4 = pvproperty(name=':ComputeCurrentOffset4', dtype=bool, value=False)
    current_scale_4 = pvproperty(name=':CurrentScale4', dtype=float, value=9.0)
    current4 = SubGroup(StatsPlugin, prefix=":Current4")

    position_offset_x = pvproperty(name=':PositionOffsetX', dtype=float, value=0.0)
    position_offset_y = pvproperty(name=':PositionOffsetY', dtype=float, value=0.0)
    compute_position_offset_x = pvproperty(name=':ComputePosOffsetX', dtype=bool, value=False)
    compute_position_offset_y = pvproperty(name=':ComputePosOffsetY', dtype=bool, value=False)
    position_scale_x = pvproperty(name=':PositionScaleX', dtype=float, value=1000000.0)
    position_scale_y = pvproperty(name=':PositionScaleY', dtype=float, value=1000000.0)

    image1 = SubGroup(PluginBase, prefix=":image1")
    sum_all = SubGroup(StatsPlugin, prefix=":SumAll")

    # Add the code that sets new current values when 'acquire' is changed.
    @acquire.putter
    async def acquire(self, instance, value):
        """
        This is a putter function that steps through the proces required when the 'acquire'
        PV is set to 1. If it is set to 0 it just sets itself to 0.
        """
        if value == 1:
            start_timestamp = time.time()  # record initial time
            self.acquire = 1  # at this point set the value to 1
            self.num_averaged = 0  # set the number of averaged points to 0

            currents = self._generate_current()  # calculate the new current values and write out.
            self.compute_current_offset_1.mean_value = currents[0]
            self.compute_current_offset_2.mean_value = currents[1]
            self.compute_current_offset_3.mean_value = currents[2]
            self.compute_current_offset_4.mean_value = currents[3]

            # Make sure that it has taken at least averaging_time to finish
            while time.time()-start_timestamp < self.averaging_time:
                time.sleep(1E-3)

            self.num_averaged = self.num_average  # set the number averaged to the expected values
            self.acquire = 0

        return value

    @averaging_time.setpoint.putter
    async def averaging_time(obj, instance, value):
        """
        This is a putter function that updates num_average when averaging_time is set
        """
        obj.parent._reset_num_average()

        return value

    @integration_time.setpoint.putter
    async def integration_time(obj, instance, value):
        """
        This is a putter function that updates num_average when integration_time is set
        """
        obj.parent._reset_num_average()

        return value


# Add some code to start a version of the server if this file is 'run'.
if __name__ == "__main__":
    ioc_options, run_options = ioc_arg_parser(
        default_prefix="QuadEM",
        desc=dedent(QuadEM.__doc__))
    ioc = QuadEM(**ioc_options)
    run(ioc.pvdb, **run_options)
