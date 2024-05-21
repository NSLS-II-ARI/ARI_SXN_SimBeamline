from caproto.server import pvproperty, ioc_arg_parser, run
from area_detector.plugin_base import PluginBase
from textwrap import dedent


class ImagePlugin(PluginBase):
    """
    A PV Group that generates the PVs associated with an Area Detector Stats Plugin.

    NOTES:
    1. Unless otherwise listed in the notes below the PVs generated are 'Dummy' PVs
    that are not modified by any inputs, or modify any other PVs, except there own
    values when they are updated.

    TODO:
    1. ...
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # call the PluginBase __init__ function

    # Write some new values for the image plugin
    plugin_type = pvproperty(name=':PluginType_RBV', value='NDPluginStdArrays',
                             report_as_string=True, read_only=True)
    # set the image size
    array_size0 = pvproperty(name=':ArraySize0_RBV', value=1544, dtype=int,
                             read_only=True,)
    array_size1 = pvproperty(name=':ArraySize1_RBV', value=2064, dtype=int,
                             read_only=True)
    array_size2 = pvproperty(name=':ArraySize2_RBV', value=1, dtype=int,
                             read_only=True)
    # Acquisition properties
    acquire_time = pvproperty(name=':AcquireTime', value=0.1, dtype=float)
    num_exposures = pvproperty(name=':NumExposures', value=1, dtype=int)
    num_images = pvproperty(name=':NumImages', value=1, dtype=int)
    image_mode = pvproperty_rbv(name=':AcquireMode', dtype=ChannelType.ENUM,
                                value='Single',
                                enum_strings=['', 'Continuous', 'Single'])


    # Add some code to start a version of the server if this file is 'run'.
    if __name__ == "__main__":
        ioc_options, run_options = ioc_arg_parser(
            default_prefix="ImagePlugin",
            desc=dedent(ImagePlugin.__doc__))
        ioc = ImagePlugin(**ioc_options)
        run(ioc.pvdb, **run_options)