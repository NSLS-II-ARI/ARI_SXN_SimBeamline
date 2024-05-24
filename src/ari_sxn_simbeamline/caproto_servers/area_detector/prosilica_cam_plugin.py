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

    manufacturer = pvproperty(name=':Manufacturer_RBV', value='Allied Vision',
                              read_only=True, report_as_string=True)
    model = pvproperty(name=':Model_RBV', value='Prosilica', read_only=True,
                       report_as_string=True)

    array_size0 = pvproperty(name=':ArraySizeX_RBV', value=1544, dtype=int,
                             read_only=True, )
    array_size1 = pvproperty(name=':ArraySizeY_RBV', value=2064, dtype=int,
                             read_only=True)
    array_size2 = pvproperty(name=':ArraySizeZ_RBV', value=1, dtype=int,
                             read_only=True)

# Add some code to start a version of the server if this file is 'run'.
if __name__ == "__main__":
    ioc_options, run_options = ioc_arg_parser(
        default_prefix="ProsilicaCamPlugin",
        desc=dedent(ProsilicaCamPlugin.__doc__))
    ioc = ProsilicaCamPlugin(**ioc_options)
    run(ioc.pvdb, **run_options)