from caproto.server import (pvproperty, PVGroup, SubGroup,
                            ioc_arg_parser, run)
from textwrap import dedent

class Prosilica(PVGroup):
    """
    A PVGroup that generates the PVs associated with a prosilica camera

    The prosilica camera that this PVGroup simulates is a commonly used
    camera at NSLS-II. In this version we randomly update the current
    values when the device is triggered via setting the 'acquire' PV to 1
    (see Notes below for details). This is done via the self._generate_image
    method, to add functionality other than a 'random' image use a
    sub-class which defines a new self._generate_image method. If you want
    the camera to save images then use the (TO BE DONE) ProsilicaTiff
    sub-class instead.

    NOTES:
    1. Unless otherwise listed in the notes below the PVs generated are
    'Dummy' PVs that are not modified by any inputs, or modify any other PVs,
    except there own values when they are updated.
    2. When self.acquire is set to 1 the sequence of events is:
        i. record the initial time and set self.array_counter to 0.
        ii. calculate the image to be returned using self._generate_image
            and write this to the self.image1.array_data attribute
        iii. if self.acquire_time has elapsed continue otherwise wait until
             it has.
        iv. set self.array_counter to self.num_exposures and self.acquire to 0
    3. When self.acquire_time, self.num_exposures or self.num_images are updated
       self.acquire_period should be updated using the following relationship:
        - self.acquire_period = self.acquire_time * self.num_exposures *
                                self.num_images
    """

# Add some code to start a version of the server if this file is 'run'.
if __name__ == "__main__":
    ioc_options, run_options = ioc_arg_parser(
        default_prefix="Prosilica",
        desc=dedent(Prosilica.__doc__))
    ioc = Prosilica(**ioc_options)
    run(ioc.pvdb, **run_options)