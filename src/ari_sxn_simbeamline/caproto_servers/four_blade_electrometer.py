from caproto.server import PVGroup, pvproperty, ioc_arg_parser, run
from textwrap import dedent


class FourBladeElectrometer(PVGroup):
    """
    A PVGroup that generates the PVs associated with the 4 blade electrometer.

    This class should be used to define the PVs for the 4 blade electrometers used
    in the ARI and SXN beamlines for the Baffle slits.

    TODO:
    1. Work out how we want to update the returned current values based on the position
    of the blades and the upstream mirrors.
    2. Decide how we want to represent the electrometer PVs (and which ones are important).
        - I suspect we will need some extra PVs (like dwell/acquisition time, ....) as well
        as others. Take a look at the NSLS-II electrometer ophyd device for a list.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # call the PVGroup __init__ function

    # Add the current PVs
    top = pvproperty(value=3E-6, name=':top', read_only=True)
    bottom = pvproperty(value=3E-6, name=':bottom', read_only=True)
    inboard = pvproperty(value=3E-6, name=':inboard', read_only=True)
    outboard = pvproperty(value=3E-6, name=':outboard', read_only=True)


# Add some code to start a version of the server if this file is 'run'.
if __name__ == "__main__":
    ioc_options, run_options = ioc_arg_parser(
        default_prefix="Electrometer",
        desc=dedent(FourBladeElectrometer.__doc__))
    ioc = FourBladeElectrometer(**ioc_options)
    run(ioc.pvdb, **run_options)
