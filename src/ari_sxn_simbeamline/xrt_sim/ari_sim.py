from bl_initialization import BLparams
from custom_devices import ID29Source, ID29OE, ID29Aperture, ID29Screen
import numpy as np
import xrt.backends.raycing as xrt_raycing


class AriModel:
    """
    The ARI beamline simulation based on XRT.

    This class simulates the beam propagation along the ARI beamline and gives
    the beam properties from each beamline component.

    TODO:
    One update method will be constructed in the integration with Caproto IOC.

    Parameters
    ----------
    update_comp : argument, passed to the update method.

    Attributes
    ----------
    *attrs : many

    Methods
    -------
    *methods : many

    """

    def __init__(self, update_comp=None):
        self.update_comp = update_comp

    blG = BLparams()

    # Initialize the beamline object
    bl = xrt_raycing.BeamLine(azimuth=0.0, height=0.0, alignE=0)

    # Add the source to beamline object bl
    energy_ref = 850.0  # eV
    energy_sigma = 5.0  # eV
    source = ID29Source(bl=bl,
                        name='GeoSrc',
                        center=(0, 0, 0),  # source position
                        nrays=10000,
                        distx='normal', dx=0.30,  # source linear profile
                        disty=None, dy=0,
                        distz='normal', dz=0.001,
                        distxprime='normal', dxprime=0.0001,  # angular profile
                        distzprime='normal', dzprime=0.01,
                        # source energy profile below
                        distE='normal', energies=(energy_ref, energy_sigma),
                        polarization='horizontal',
                        filamentBeam=False,
                        uniformRayDensity=False)
    source.activate(updated=True)

    # Add the M1 to beamline object bl
    m1 = ID29OE(bl=bl,
                name='M1', center=blG['rM1'],
                yaw=blG['yawM1xrt'], roll=blG['rolM1xrt'],
                pitch=blG['pitM1xrt'],
                material=blG['matM1'],
                limPhysX=blG['XphysSzM1'], limOptX=blG['XoptSzM1'],
                limPhysY=blG['YphysSzM1'], limOptY=blG['YoptSzM1'],
                shape='rect', upstream=source,
                deflection='inboard')  # optics is defined in the material!!!
    m1.activate(updated=True)

    # Add the M2 to beamline object bl
    m2 = ID29OE(bl=bl,
                name='M2',
                center=blG['rM1'],
                yaw=blG['yawM1xrt'], roll=0.002, pitch=blG['pitM1xrt'],
                material=blG['matM1'],
                limPhysX=blG['XphysSzM1'],
                limPhysY=blG['YphysSzM1'],
                shape='rect',
                upstream=m1,
                deflection='outboard')  # optics is defined in the material!!!
    m2.activate(updated=True)

    # Add the M1 Baffle slit to beamline object bl
    slit1 = ID29Aperture(bl=bl,
                         name='M1Baff_slit',
                         center=[0, 57234, 0],  # blG['rSrctoM1Baff']
                         x='auto', z='auto',  # what are these x and z???
                         kind=['left', 'right', 'bottom', 'top'],
                         opening=[-blG['HsltSz'] / 2, blG['HsltSz'] / 2,
                                  -blG['VsltSz'] / 2, blG['VsltSz'] / 2],
                         upstream=m2)
    slit1.activate(updated=True)

    # Add another slit at M1 diagnostic to block beam when diagnostic unit is in
    slit2 = ID29Aperture(bl=bl,
                         name='M1Diag_slit',
                         center=blG['rSrcM1Diag'],
                         x='auto', z='auto',  # what are these x and z???
                         kind=['left', 'right', 'bottom', 'top'],
                         opening=[-50, 50, -50, 50.0],
                         upstream=slit1)
    slit2.activate(updated=True)

    # Add one screen at M1 diagnostic to monitor the beam
    screen1 = ID29Screen(bl=bl,
                         name='M1Diag_Scrn',
                         center=blG['rSrcM1Diag'],
                         x=np.array([1, 0, 0]),
                         z=np.array([0, 0, 1]),
                         upstream=slit2)
    screen1.activate(updated=True)
