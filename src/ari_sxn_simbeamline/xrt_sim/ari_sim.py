import numpy as np
import matplotlib.pyplot as plt
from time import strftime

import xrt.backends.raycing as xrt_raycing
import xrt.backends.raycing.sources as xrt_source
import xrt.backends.raycing.apertures as xrt_aperture
import xrt.backends.raycing.screens as xrt_screen
import xrt.backends.raycing.oes as xrt_oes
# import xrt.backends.raycing.materials as xrt_material
#################################################################
from initialization import BLparams

#################################################################
Nrays = 10000
energy_ref = 850.0 # eV
energy_sigma = 5.0 # eV

def AriSim(update_para=None):
    '''
    The beamline simulation for ARI beamline!

    update_para is a dictionary containing the parameters that are modified
    comparing to their initial values.
    '''
    blG = BLparams(update_para=update_para)
    ###############################################
    # Initialize the beamline object
    bl = xrt_raycing.BeamLine(azimuth=0.0, height=0.0, alignE=0)
    ###############################################
    # Add the source to beamline object bl
    xrt_source.GeometricSource(bl=bl,
                               name='GeoSrc',
                               center=(0, 0, 0), # source position
                               nrays=Nrays,
                               distx='normal', dx=0.30, # source linear profile
                               disty=None, dy=0,
                               distz='normal', dz=0.001,
                               distxprime='normal', dxprime=0.0001, # source angular profile
                               distzprime='normal', dzprime=0.01,
                               distE='normal', energies=(energy_ref, energy_sigma), # source energy profile
                               polarization='horizontal',
                               filamentBeam=False,
                               uniformRayDensity=False)

    ###############################################
    # Add one optics to beamline object bl
    xrt_oes.OE(bl=bl,
               name='PM',
               center=blG['rM1'],
               yaw=blG['yawM1xrt'], roll=blG['rolM1xrt'], pitch=blG['pitM1xrt'],
               positionRoll=np.pi/2,
               material=blG['matM1'],
               limPhysX=blG['XphysSzM1'], limOptX=blG['XoptSzM1'],
               limPhysY=blG['YphysSzM1'], limOptY=blG['YoptSzM1'],
               shape='rect')  # optics is defined in the material!!!

    ###############################################
    # Add one slit to beamline object bl
    xrt_aperture.RectangularAperture(bl=bl,
                                     name='Exit slit',
                                     center=blG['rScrXslt'],
                                     x='auto', z='auto',  # what are these x and z???
                                     kind=['left', 'right', 'bottom', 'top'],
                                     opening=[-blG['HsltSz'] / 2, blG['HsltSz'] / 2,
                                              -blG['VsltSz'] / 2, blG['VsltSz'] / 2])
    ###############################################
    # Add one screen to beamline object bl
    xrt_screen.Screen(bl=bl,
                      name='Screen',
                      center=blG['rSrcM1Diag'],
                      x=np.array([1, 0, 0]),
                      z=np.array([0, 0, 1]))

    ###############################################
    beamSource = bl.sources[0].shine()
    beamPMgl, beamPMloc = bl.oes[0].reflect(beamSource)
    beamXslt = bl.slits[0].propagate(beamPMgl)
    beamScrn = bl.screens[0].expose(beamPMgl)

    beam_prop = {'source': beamSource, 'm1': beamPMgl,
                 'slit': beamXslt, 'm1_screen': beamScrn}

    return beam_prop

beam_prop = AriM1Sim(blG=BLparams())

#####################################
def f1(sig='source',xlabel='x',ylabel='z'):
    #####################################
    x = beam_prop[sig].x
    z = beam_prop[sig].z
    E = beam_prop[sig].E

    sig_x = eval(xlabel)
    sig_y = eval(ylabel)

    plt.close('all')
    fig = plt.figure(strftime("%Y %b %d  %H:%M:%S"), figsize=(7, 5.5))
    ax = fig.add_subplot(111)
    ax.plot(sig_x,sig_y,
            marker='o', mfc='navy', mec='navy',markersize=2, markeredgewidth=0.2,
            linestyle='none', color='r', lw=3.0,
            alpha=0.7,)

    # ax.plot(beam_prop[sig].state,
    #         marker='o', mfc='navy', mec='navy',markersize=2, markeredgewidth=0.2,
    #         linestyle='none', color='r', lw=3.0,
    #         alpha=0.7,)

    ax.set_xlabel(xlabel, fontdict={'fontsize': 12})
    ax.set_ylabel(ylabel, fontdict={'fontsize': 12})

    fig.tight_layout()



