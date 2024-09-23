import numpy as np
import xrt.backends.raycing.materials as xrt_material


nickel = xrt_material.Material('Ni', rho=8.908, table='Chantler Total', kind='mirror', name='Ni')
genericGR = xrt_material.Material('Ni', rho=8.908, table='Chantler total', kind='grating',
                        name='generic grating', efficiency=[(1, 1), (-1, 1)])  # efficiency = 1

def BLparams():
    '''Initialize the beamline parameters!

    1. blG is a dictionary containing all parameters for beamline simulation.

    2. update_para is a dictionary containing the parameters that are modified
    comparing to their initial values. update_para should be a sub-dict of blG.

    Note: The distance is in the unit of mm,
        and the angle is in the unit of radian.
    '''
    blG = dict()

    # Initialize all basic parameters for beamline simulation
    blG['dSrcToM1'] = 27850
    blG['dSrctoM1Baff'] = 31094.5
    blG['dSrctoM1Diag'] = 31340.6
    blG['pitM1'] = np.radians(2)

    blG['HsltSz'] = 10
    blG['VsltSz'] = 10


    # M1 details
    blG['rM1'] = [0, blG['dSrcToM1'], 0] # M1 local coordinate
    # blG['rM1'] = [0, 58792, 0] # M1 local coordinate

    gold = xrt_material.Material('Au', rho=19.3, table='Chantler Total',
                                 kind='mirror', name='Au')
    blG['matM1'] = gold # M1 coating

    blG['yawM1xrt'] = 0
    blG['rolM1xrt'] = 0
    blG['pitM1xrt'] = blG['pitM1']

    # M1 physical length
    optL=285; optW=18
    blG['XoptSzM1']=[-optW/2,optW/2]; blG['XphysSzM1']=blG['XoptSzM1']
    blG['YoptSzM1']=[-optL/2,optL/2]; blG['YphysSzM1']=blG['YoptSzM1']


    blG['rSrcM1Diag'] = [0, blG['dSrctoM1Diag'], 0]

    blG['rScrXslt'] = [0, blG['dSrctoM1Baff'], 0]

    return blG