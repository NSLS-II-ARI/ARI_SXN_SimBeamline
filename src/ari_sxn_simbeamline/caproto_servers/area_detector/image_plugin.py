from area_detector.plugin_base import PluginBase
from caproto import ChannelType
from caproto.server import pvproperty, ioc_arg_parser, run
import numpy as np
from textwrap import dedent


class ImagePlugin(PluginBase):
    """
    A PV Group that generates the PVs associated with an Area Detector Stats Plugin.

    NOTES:
    1. Unless otherwise listed in the notes below the PVs generated are 'Dummy' PVs
    that are not modified by any inputs, or modify any other PVs, except there own
    values when they are updated.
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

    TODO:
    1. ...
    """

    async def _generate_image(self):
        """
        This method returns an image to be used as the return array.

        This method returns a self.array_size0 x array_size1 random image
        array to be used inside a putter hook for self.acquire which also
        updates array data with the flattened version of the returned image
        file via image.flatten().

        Returns
        -------
        image : np.array,
            A self.array_size0 x self.array_size1 numpy array consisting of
            random integers between 0 and 256.

        """
        image = np.random.randint(0, 257, size=(self.array_size0,
                                                self.array_size1))

        return image

    async def _reset_acquire_period(self):
        """This is a method that resets num_averaged when required.

        self.num_averaged requires to be reset whenever self.acquire_time,
        self.num_exposures or self.num_images are updated. This
        method will be used as the putter hook for these.
        """

        await self.acquire_period.write(
            self.acquire_time.readback.value *
            self.num_exposures.readback.value *
            self.num_images.readback.value)

        return

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
    acquire = pvproperty(name=':Acquire', dtype=int, value=True)
    acquire_time = pvproperty(name=':AcquireTime', value=0.1, dtype=float)
    acquire_period = pvproperty(name=':AcquirePeriod', value=0.1, dtype=float,
                                read_only=True)
    num_exposures = pvproperty(name=':NumExposures', value=1, dtype=int)
    num_images = pvproperty(name=':NumImages', value=1, dtype=int)
    image_mode = pvproperty(name=':AcquireMode', dtype=ChannelType.ENUM,
                            value='Single', enum_strings=['', 'Continuous',
                                                          'Single'])
    detector_state = pvproperty(name=':DetectorStateRBV', dtype=ChannelType.ENUM,
                                value='idle', enum_strings=['idle', 'acquiring'],
                                read_only=True)


    @acquire.putter
    async def acquire(self, instance, value):
        """
        This is a putter function that steps through the proces required when the 'acquire'
        PV is set to 1. If it is set to 0 it just sets itself to 0.
        """
        if value == 1:
            start_timestamp = time.time()  # record initial time
            await self.array_counter.write(0)  # set the number of averaged points to 0
            image = await self._generate_image()  # calculate the new image.
            await self.array_data.write(image.flatten())
            # Make sure that it has taken at least averaging_time to finish
            while time.time() - start_timestamp < self.acquire_period.value:
                time.sleep(1E-3)

            await self.array_counter.write(self.num_exposures)

        return value

    @acquire_time.putter
    async def acquire_time(obj, instance, value):
        """
        This is a putter function that updates num_average when averaging_time is set
        """
        await obj.write(value)
        await obj.parent._reset_acquire_period()

        return value

    @num_exposures.putter
    async def num_exposures(obj, instance, value):
        """
        This is a putter function that updates num_average when averaging_time is set
        """
        await obj.write(value)
        await obj.parent._reset_acquire_period()

        return value

    @num_images.putter
    async def num_images(obj, instance, value):
        """
        This is a putter function that updates num_average when averaging_time is set
        """
        await obj.write(value)
        await obj.parent._reset_acquire_period()

        return value


    # Add some code to start a version of the server if this file is 'run'.
    if __name__ == "__main__":
        ioc_options, run_options = ioc_arg_parser(
            default_prefix="ImagePlugin",
            desc=dedent(ImagePlugin.__doc__))
        ioc = ImagePlugin(**ioc_options)
        run(ioc.pvdb, **run_options)
