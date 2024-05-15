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

    plugin_type = pvproperty(name=':PluginType_RBV', value='NDPluginStdArrays',
                             report_as_string=True, read_only=True)

    # Add some code to start a version of the server if this file is 'run'.
    if __name__ == "__main__":
        ioc_options, run_options = ioc_arg_parser(
            default_prefix="ImagePlugin",
            desc=dedent(ImagePlugin.__doc__))
        ioc = ImagePlugin(**ioc_options)
        run(ioc.pvdb, **run_options)