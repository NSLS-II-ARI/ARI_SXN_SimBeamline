from area_detector.quad_em import QuadEM
from area_detector.prosilica import Prosilica
from caproto.ioc_examples.fake_motor_record import FakeMotor
from caproto.server import PVGroup, SubGroup, ioc_arg_parser, run
from textwrap import dedent


class Diagnostic(PVGroup):
    """
    A PVGroup that generates the PVs associated with the ARI and SXN Diagnostic units.

    This class should be used to define the ARI & SXN Diagnostic unit PVs. It will
    consist of PVs for each of the motors (main translation stage and the YaG screen
    translation stage) as well as those related to the electrometer for the photo-diode
    and the camera.

    TODO:
    1. Work out how we want to define the area detector PVs, including how we 'update'
       the photo-current PVs for the photodiode and the image seen on the camera.
    2. Decide how we want to implement the motor-record PVs.
        - See the section in the AriM1Mirror PVGroup below on this topic.
    3. Decide how we want to represent the electrometer PVs (and which ones are important).
        - see Baffleslit PVGroup for more info.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # call the PVGroup __init__ function

    # Add the motor PVs
    multi_trans = SubGroup(FakeMotor, velocity=5, precision = 3,
                           user_limits = (-125, 25), prefix=':multi_trans')

    yag_trans = SubGroup(FakeMotor, velocity=5, precision = 3,
                         user_limits = (-25, 25), prefix=':yag_trans')

    # Add the photodiode electrometer PVs
    currents = SubGroup(QuadEM, prefix=':Currents')

    # Add the camera PVs
    camera = SubGroup(Prosilica, prefix=':Camera')


# Add some code to start a version of the server if this file is 'run'.
if __name__ == "__main__":
    ioc_options, run_options = ioc_arg_parser(
        default_prefix="Diagnostic",
        desc=dedent(Diagnostic.__doc__))
    ioc = Diagnostic(**ioc_options)
    run(ioc.pvdb, **run_options)
