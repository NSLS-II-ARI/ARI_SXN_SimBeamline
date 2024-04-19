from caproto.server import (pvproperty, PVGroup, SubGroup,
                            ioc_arg_parser, run)
from plugin_base import PluginBase, pvproperty_rbv
from stats_plugin import StatsPlugin
from textwrap import dedent


class QuadEM(PVGroup):
    """
    A PV Group that generates the PVs associated with a QuadEM device.

    The QuadEM device which this PVGroup simulates is a commonly employed 4 channel
    electrometer at NSLS-II. In this case passing in this version we randomly update
    the current values when the device is triggered via setting the 'acquire' PV to
    1 (see Notes below for details). This is done via the self.trigger method, to
    add functionality other than a 'random' current sub-class this class and
    define a new self.trigger method.

    NOTES:
    1. Unless otherwise listed in the notes below the PVs generated are 'Dummy' PVs
    that are not modified by any inputs, or modify any other PVs, except there own
    values when they are updated.
    2. Add description of acquire process here
    3. Add description of averaging/integration time update here.

    TODO:
    1. ...
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # call the PluginBase __init__ function

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


# Add some code to start a version of the server if this file is 'run'.
if __name__ == "__main__":
    ioc_options, run_options = ioc_arg_parser(
        default_prefix="QuadEM",
        desc=dedent(QuadEM.__doc__))
    ioc = QuadEM(**ioc_options)
    run(ioc.pvdb, **run_options)
