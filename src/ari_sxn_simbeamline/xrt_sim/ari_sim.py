from custom_devices import (ID29Source, ID29OE, ID29Aperture, ID29Screen,
                            TestMirror, transform_NSLS2XRT)
import numpy as np
import xrt.backends.raycing as xrt_raycing
import xrt.backends.raycing.materials as xrt_material


# Define a test object to use in place of the caproto IOC for testing
mirror1 = TestMirror({'Ry_coarse': np.radians(2), 'Ry_fine': 0, 'Rz': 0,
                     'x': 0, 'y': 0})


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


# noinspection PyUnresolvedReferences
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
                        uniformRayDensity=False,
                        parameter_map={'center': [0, 0, 0],
                                       'angles': [0, 0, 0]},
                        transform_matrix=transform_NSLS2XRT['upward'])
    source.activate(updated=True)  # initialize the source output

    # Add the M1 to beamline object bl
    m1 = ID29OE(bl=bl,
                name='m1',
                center=(0, 27850, 0),  # location (global XRT coords)
                yaw=0, roll=0, pitch=np.radians(2),
                material=gold,
                limPhysX=[-60/2+10, 60/2+10], limOptX=[-15/2, 15/2],
                limPhysY=[-400/2, 400/2], limOptY=[-240/2, 240/2],
                shape='rect', upstream=source,
                parameter_map={'center': [mirror1.x, mirror1.y, 0],
                               'angles': [0, mirror1.Ry, mirror1.Rz]},
                transform_matrix=transform_NSLS2XRT['inboard'])
    m1.activate(updated=True)  # initialize the m1 mirror output.

    # Add the M1 Baffle slit to beamline object bl
    m1_baffles = ID29Aperture(bl=bl,
                              name='m1_baffles',
                              center=[0, 31094.5, 0],  # location (XRT coords)
                              x='auto', z='auto',
                              kind=['left', 'right', 'bottom', 'top'],
                              opening=[-20 / 2, 20 / 2,
                                       -20 / 2, 20 / 2],
                              upstream=m1,
                              parameter_map={
                                  'opening': [mirror1.baffles.outboard,
                                              mirror1.baffles.inboard,
                                              mirror1.baffles.bottom,
                                              mirror1.baffles.top]},
                              transform_matrix=transform_NSLS2XRT['upward'])
    m1_baffles.activate(updated=True)  # initialize the m1 baffles output

    # Add one screen at M1 diagnostic to monitor the beam
    # NOTE: the IOC needs to select the right region based on diag position
    m1_diag = ID29Screen(bl=bl,
                         name='m1_diag',
                         center=[0, 31340.6, 0],  # location (global XRT coords)
                         x=np.array([1, 0, 0]),
                         z=np.array([0, 0, 1]),
                         upstream=m1_baffles,
                         parameter_map={},
                         transform_matrix=transform_NSLS2XRT['upward'])
    m1_diag.activate(updated=True)  # initialize the m1 diagnostic.

    # Add slit at M1 diagnostic to block beam when diagnostic unit is in
    m1_diag_slit = ID29Aperture(bl=bl,
                                name='m1_diag_slit',
                                center=[0, 31340.7, 0],  # 0.1mm offset to diag
                                x='auto', z='auto',
                                kind=['left', 'right', 'bottom', 'top'],
                                opening=[-50, 50, -50, 50],
                                upstream=m1_baffles,
                                parameter_map={
                                    'opening': [-50, 50, -50,
                                                mirror1.diagnostic.multi_trans]},
                                transform_matrix=transform_NSLS2XRT['upward'])
    m1_diag_slit.activate(updated=True)  # initialize the m1 diag screen.
