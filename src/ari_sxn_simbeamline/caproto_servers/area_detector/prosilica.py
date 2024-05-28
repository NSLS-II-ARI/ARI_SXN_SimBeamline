from area_detector.prosilica_cam_plugin import ProsilicaCamPlugin
from caproto.server import (PVGroup, SubGroup, ioc_arg_parser, run)
from textwrap import dedent


class Prosilica(PVGroup):
    """
    A PVGroup that generates the PVs associated with a prosilica camera

    The prosilica camera that this PVGroup simulates is a commonly used
    camera at NSLS-II. In this version we use the 'prosilica_cam_plugin
    which randomly updates the image when the device is triggered via
    setting the 'self.cam.acquire' PV to 1 (see prosilica_cam_plugin
    docstring for details). This is done via the
    self.cam._generate_image method, to add functionality other than a
    'random' image use a sub-class which defines a new
    self.cam._generate_image method. If you want the camera to save images
    then use the (TO BE DONE) ProsilicaTiff sub-class instead.

    NOTES:
    1. Unless otherwise listed in the notes below the PVs generated are
    'Dummy' PVs that are not modified by any inputs, or modify any other PVs,
    except there own values when they are updated.
    """

    cam = SubGroup(ProsilicaCamPlugin, prefix=":cam1")


# Add some code to start a version of the server if this file is 'run'.
if __name__ == "__main__":
    ioc_options, run_options = ioc_arg_parser(
        default_prefix="Prosilica",
        desc=dedent(Prosilica.__doc__))
    ioc = Prosilica(**ioc_options)
    run(ioc.pvdb, **run_options)

