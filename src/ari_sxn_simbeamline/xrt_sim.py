import sys

# sys.path.append('/Users/jieminli/PycharmProjects/Beamline_sim/')
import numpy as np
# from scipy import *
# from pandas import DataFrame
import matplotlib.pyplot as plt
from pandas import DataFrame
#################################################################
# import xrt packages
import xrt.backends.raycing as raycing
import xrt.backends.raycing.run as rr
import xrt.plotter as xrtp
import xrt.runner as xrtr
import xrt.backends.raycing.sources as rs
from xrt.backends.raycing.physconsts import SIE0
import xrt.backends.raycing.apertures as raa
import xrt.backends.raycing.screens as rsc
import xrt.backends.raycing.oes as roe
import xrt.backends.raycing.materials as rm
import xrt.backends.raycing.materials_compounds as rmComp

#################################################################
gold = rm.Material('Au', rho=19.3, table='Chantler Total', kind='mirror', name='Au')
nickel = rm.Material('Ni', rho=8.908, table='Chantler Total', kind='mirror', name='Ni')
genericGR = rm.Material('Ni', rho=8.908, table='Chantler total', kind='grating',
                        name='generic grating', efficiency=[(1, 1), (-1, 1)])  # efficiency = 1


#################################################################

def buildBeamline(eV, sigma_eV, Nrays, HsltSz=4, VsltSz=4):
    # build a properly aligned beamline

    # global coordinate system:
    #   x transverse to source beam
    #   y along source beam propgation direction
    #   z is up
    #   position of optical elements are given in the global coordinate system
    #   rotations are applied in order yaw, roll, pitch
    #   rotations of optical elements are done in the local coordinate system
    #      in the default order yaw, roll, pitch

    d_Src2Scrn = 28373  # mm
    d_Src2Slit = 28000  # mm
    d_Src2Mirr = 27850  # mm

    mat_mirror = gold
    pit_mirror = 0.0000218  # rad
    # Build beamline.  Set azimuth parameter in beamline to 0.  Then
    # global coordinate system and beamline coordinate system are identical
    # and they are 'SHADOW' like (right hand coordinate system)
    bl = raycing.BeamLine(azimuth=0.0, height=0.0, alignE=0)

    # create geometric source
    bl.source = rs.GeometricSource(
        bl=bl,
        name='test1',
        center=(0, 0, 0),
        nrays=Nrays,
        distx='normal', dx=0.030,
        disty=None, dy=0,
        distz='normal', dz=0.03,
        distxprime='normal', dxprime=0.0001,
        distzprime='normal', dzprime=0.0001,
        distE='normal', energies=(eV, sigma_eV),
        polarization='horizontal',
        filamentBeam=False,
        uniformRayDensity=False
    )

    bl.pm = roe.OE(bl=bl, name='PM', center=[0, d_Src2Mirr, 0],
                   yaw=0, roll=0, pitch=pit_mirror, material=mat_mirror
                   )

    bl.xslt = raa.RectangularAperture(bl=bl, name='Exit slit',
                                      center=np.array([0, d_Src2Slit, 0]), x='auto',
                                      kind=['left', 'right', 'bottom', 'top'],
                                      opening=[-HsltSz / 2, HsltSz / 2,
                                               -VsltSz / 2, VsltSz / 2]
                                      )

    bl.scrn = rsc.Screen(bl=bl,
                         name='Screen',
                         center=np.array([0, d_Src2Scrn, 0]),
                         x=np.array([1, 0, 0]),
                         z=np.array([0, 0, 1])
                         )

    return bl


# set directions to raytrace beamline
def run_process0(bl):
    beamSource = bl.sources[0].shine()
    beamPMgl, beamPMloc = bl.pm.reflect(beamSource)
    beamXslt = bl.xslt.propagate(beamPMgl)
    beamScrn = bl.scrn.expose(beamPMgl)
    #
    # beamXslt = bl.xslt.propagate(beamSource)
    # beamScrn = bl.scrn.expose(beamSource)

    outdict = {
        'beamSource': beamSource,
        'beamPMloc': beamPMloc,
        'beamXslt': beamXslt,
        'beamScrn': beamScrn
    }
    return outdict

Nrays = 1e4
eV = 860  # eV
sigma_eV = 0.05  # eV

bl = buildBeamline(eV, sigma_eV, Nrays)
beamSource = bl.sources[0].shine()
beamPMgl, beamPMloc = bl.pm.reflect(beamSource)
beamXslt = bl.xslt.propagate(beamPMgl)
beamScrn = bl.scrn.expose(beamPMgl)

beam_dict = {'source_x':beamSource.x, 'source_z':beamSource.z, 'source_E':beamSource.E,
             'slit_x':beamXslt.x, 'slit_z':beamXslt.z, 'slit_E':beamXslt.E,
             'screen_x':beamScrn.x, 'screen_z':beamScrn.z, 'screen_E':beamScrn.E}
# #####################################
# plt.close('all')
# fig = plt.figure(1)
# ax = fig.add_subplot(111)
# ax.plot(beam_dict['source_x'],beam_dict['source_z'],
#         linestyle='none',marker='.')
#
# fig.tight_layout()