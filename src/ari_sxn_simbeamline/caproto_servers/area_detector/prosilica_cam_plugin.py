from area_detector.plugin_base import pvproperty_rbv
from area_detector.cam_plugin import CamPlugin
from caproto.server import pvproperty, ioc_arg_parser, run
from textwrap import dedent

class ProsilicaCamPlugin(CamPlugin):
    """
    A cam plugin PVGroup for use with Prosilica cameras.

    This class modifies the CamPlugin with some Prosilica cam specific
    properties.
    """

    manufacturer = pvproperty(name=':Manufacturer', value='Allied Vision')
    model = pvproperty(name=':Model', value='Prosilica')

# Add some code to start a version of the server if this file is 'run'.
if __name__ == "__main__":
    ioc_options, run_options = ioc_arg_parser(
        default_prefix="ProsilicaCamPlugin",
        desc=dedent(ProsilicaCamPlugin.__doc__))
    ioc = ProsilicaCamPlugin(**ioc_options)
    run(ioc.pvdb, **run_options)