from custom_devices import ID29Source, ID29OE, ID29Aperture, ID29Screen
import numpy as np
import xrt.backends.raycing as xrt_raycing
import xrt.backends.raycing.materials as xrt_material

# Define optics coating material instances.
nickel = xrt_material.Material('Ni', rho=8.908,
                               table='Chantler Total',
                               kind='mirror', name='Ni')

gold = xrt_material.Material('Au', rho=19.3, table='Chantler Total',
                             kind='mirror', name='Au')

genericGR = xrt_material.Material('Ni', rho=8.908,
                                  table='Chantler total',
                                  kind='grating', name='generic grating',
                                  efficiency=[(1, 1), (-1, 1)])  # efficiency=1


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

    # Initialize the beamline object
    bl = xrt_raycing.BeamLine(azimuth=0.0, height=0.0, alignE=0)

    # Add the source to beamline object bl
    energy_ref = 850.0  # eV
    energy_sigma = 5.0  # eV
    source = ID29Source(bl=bl,
                        name='source',
                        center=(0, 0, 0),  # location (global XRT coords)
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
    source.activate(updated=True)  # initialize the source output

    # Add the M1 to beamline object bl
    m1 = ID29OE(bl=bl,
                name='m1',
                center=(0, 27850, 0),  # location (global XRT coords)
                yaw=0, roll=0, pitch=np.radians(2),
                material=gold,
                limPhysX=[-400/2, 400/2], limOptX=[-240/2, 240/2],
                limPhysY=[-60/2+10, 60/2+10], limOptY=[-15/2, 15/2],
                shape='rect', upstream=source,
                deflection='inboard')  # optics is defined in the material!!!
    m1.activate(updated=True)  # initialize the m1 mirror output.

    # Add the M1 Baffle slit to beamline object bl
    m1_baffles = ID29Aperture(bl=bl,
                              name='m1_baffles',
                              center=[0, 31094.5, 0],
                              x='auto', z='auto',
                              kind=['left', 'right', 'bottom', 'top'],
                              opening=[-10 / 2, 10 / 2,
                                       -10 / 2, 10 / 2],
                              upstream=m1)
    m1_baffles.activate(updated=True)  # initialize the m1 baffles output

    # Add one screen at M1 diagnostic to monitor the beam
    # NOTE: the IOC needs to select the right region based on diag position
    m1_diag = ID29Screen(bl=bl,
                         name='m1_diag',
                         center=[0, 31340.6, 0],  # location (global XRT coords)
                         x=np.array([1, 0, 0]),
                         z=np.array([0, 0, 1]),
                         upstream=m1_baffles)
    m1_diag.activate(updated=True)  # initialize the m1 diagnostic.

    # Add another slit at M1 diagnostic to block beam when diagnostic unit is in
    m1_diag_slit = ID29Aperture(bl=bl,
                                name='m1_diag_slit',
                                center=31340.7,  # 0.1mm downstream of diag
                                x='auto', z='auto',
                                kind=['left', 'right', 'bottom', 'top'],
                                opening=[-50, 50, -50, 50.0],
                                upstream=m1_baffles)
    m1_diag_slit.activate(updated=True)  # initialize the m1 diag screen.
