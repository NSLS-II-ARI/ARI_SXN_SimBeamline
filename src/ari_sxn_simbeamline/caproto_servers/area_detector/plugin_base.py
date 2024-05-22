from caproto.server import (PVGroup, pvproperty, get_pv_pair_wrapper,
                            ioc_arg_parser, run)
from textwrap import dedent

# A shortcut to use for PVs with a readback partner given by the suffix '_RBV'
pvproperty_rbv = get_pv_pair_wrapper(setpoint_suffix='', readback_suffix='_RBV')


class PluginBase(PVGroup):
    """
    A PVGroup that generates the PVs associated with a generic areadetector plugin.

    This class should be used to define the PVs for a generic areadetector plugin.
    It is based on the 'ophyd.areadetector.plugins.PluginBase' object.

    NOTES:
    1. Unless otherwise listed in the notes below the PVs generated are 'Dummy' PVs
    that are not modified by any inputs, or modify any other PVs, except there own
    values when they are updated.

    TODO:
    1. ...
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # call the PVGroup __init__ function

    _default_port_name = 'EM180'
    array_counter = pvproperty_rbv(name=':ArrayCounter', dtype=int)
    array_rate = pvproperty(name=':ArrayRate_RBV', dtype=float, read_only=True)

    array_size0 = pvproperty(name=':ArraySize0_RBV', dtype=int, read_only=True)
    array_size1 = pvproperty(name=':ArraySize1_RBV', dtype=int, read_only=True)
    array_size2 = pvproperty(name=':ArraySize2_RBV', dtype=int, read_only=True)

    nd_attributes_file = pvproperty(name=':NDAttributesFile', dtype=str,
                                    report_as_string=True, max_length=256)

    pool_alloc_buffers = pvproperty(name=':PoolAllocBuffers', dtype=int, read_only=True)
    pool_free_buffers = pvproperty(name=':PoolFreeBuffers', dtype=int, read_only=True)
    pool_max_buffers = pvproperty(name=':PoolMaxBuffers', dtype=int, read_only=True)
    pool_max_mem = pvproperty(name=':PoolMaxMem', dtype=float, read_only=True)
    pool_used_buffers = pvproperty(name=':PoolUsedBuffers', dtype=float, read_only=True)
    pool_used_mem = pvproperty(name=':PoolUsedMem', dtype=float, read_only=True)
    port_name = pvproperty(name=':PortName_RBV', value=_default_port_name,
                           report_as_string=True, read_only=True)

    bayer_pattern = pvproperty(name=':BayerPattern_RBV', dtype=int, read_only=True)
    blocking_callbacks = pvproperty_rbv(name=':BlockingCallbacks',
                                        report_as_string=True, dtype=str)
    color_mode = pvproperty(name=':ColorMode_RBV', dtype=int, read_only=True)
    data_type = pvproperty(name=':DataType_RBV', dtype=str,
                           report_as_string=True, read_only=True)

    dim0_sa = pvproperty(name=':Dim0SA', dtype=int, max_length=10)
    dim1_sa = pvproperty(name=':Dim1SA', dtype=int, max_length=10)
    dim2_sa = pvproperty(name=':Dim2SA', dtype=int, max_length=10)

    dimensions = pvproperty(name=':Dimensions_RBV', dtype=int, max_length=10,
                            read_only=True)
    dropped_arrays = pvproperty_rbv(name=':DroppedArrays', dtype=int)
    enable = pvproperty_rbv(name=':EnableCallbacks', dtype=bool)
    min_callback_time = pvproperty_rbv(name=':MinCallbackTime', dtype=float)
    nd_array_address = pvproperty_rbv(name=':NDArrayAddress', value=0)
    nd_array_port = pvproperty_rbv(name=':NDArrayPort', value=_default_port_name,
                                   report_as_string=True)
    ndimensions = pvproperty(name=':NDimensions_RBV', dtype=int, read_only=True)
    plugin_type = pvproperty(name=':PluginType_RBV', value='NDPluginStats',
                             report_as_string=True, read_only=True)
    queue_free = pvproperty(name=':QueueFree', dtype=int)
    queue_free_low = pvproperty(name=':QueueFreeLow', dtype=float)
    queue_size = pvproperty(name=':QueueSize', dtype=int)
    queue_use = pvproperty(name=':QueueUse', dtype=float)
    queue_use_high = pvproperty(name=':QueueUseHIGH', dtype=float)
    queue_use_hihi = pvproperty(name=':QueueUseHIHI', dtype=float)
    time_stamp = pvproperty(name=':TimeStamp_RBV', dtype=float, read_only=True)
    unique_id = pvproperty(name=':UniqueId_RBV', dtype=int, read_only=True)
    array_data = pvproperty(name=':ArrayData', dtype=int, max_length=300000)


# Add some code to start a version of the server if this file is 'run'.
if __name__ == "__main__":
    ioc_options, run_options = ioc_arg_parser(
        default_prefix="PluginBase",
        desc=dedent(PluginBase.__doc__))
    ioc = PluginBase(**ioc_options)
    run(ioc.pvdb, **run_options)
