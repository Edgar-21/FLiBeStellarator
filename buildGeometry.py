import parastell
import numpy as np
import source_mesh
import read_vmec

def makeSource(plas_eq = 'plas_eq.nc', source = {
            'num_s' : 11,
            'num_theta' : 81,
            'num_phi' : 61,
            'tor_ext' : 90
        }
    ):
    vmec = read_vmec.vmec_data(plas_eq)
    strengths = source_mesh.source_mesh(vmec, source)
    return strengths

def buildModel(radialBuild=None, plas_eq = 'plas_eq.nc',
                numPhi = 61, numTheta = 61, 
                magnets = None, build = None, source = None,
                export = None, repeat = 0):

    #Define radial build dict
    if radialBuild == None:
        radialBuild = {
            'sol': {
                'thickness_matrix': [
                        [3,3,3,3,3,3,3,3,3],
                        [3,3,3,3,3,3,3,3,3],
                        [3,3,3,3,3,3,3,3,3],
                        [3,3,3,3,3,3,3,3,3],
                        [3,3,3,3,3,3,3,3,3]
                ]
            },
            'vacVessel': {
                'thickness_matrix': [
                        [8,8,8,8,8,8,8,8,8],
                        [8,8,8,8,8,8,8,8,8],
                        [8,8,8,8,8,8,8,8,8],
                        [8,8,8,8,8,8,8,8,8],
                        [8,8,8,8,8,8,8,8,8]
                ]
            },
            'breeder': {
                'thickness_matrix': [
                        [54.2,54.2,54.2,54.2,54.2,54.2,54.2,54.2,54.2],
                        [54.2,54.2,54.2,54.2,54.2,54.2,54.2,54.2,54.2],
                        [54.2,54.2,54.2,54.2,54.2,54.2,54.2,54.2,54.2],
                        [54.2,54.2,54.2,54.2,54.2,54.2,54.2,54.2,54.2],
                        [54.2,54.2,54.2,54.2,54.2,54.2,54.2,54.2,54.2]
                ]
            },
            'backWall': {
                'thickness_matrix': [
                        [3,3,3,3,3,3,3,3,3],
                        [3,3,3,3,3,3,3,3,3],
                        [3,3,3,3,3,3,3,3,3],
                        [3,3,3,3,3,3,3,3,3],
                        [3,3,3,3,3,3,3,3,3]
                ]
            },
            'neutronShield': {
                'thickness_matrix': [
                        [14,14,14,14,14,14,14,14,14],
                        [14,14,14,14,14,14,14,14,14],
                        [14,14,14,14,14,14,14,14,14],
                        [14,14,14,14,14,14,14,14,14],
                        [14,14,14,14,14,14,14,14,14]
                ]
            },
            'structure': {
                'thickness_matrix': [
                        [15,15,15,15,15,15,15,15,15],
                        [15,15,15,15,15,15,15,15,15],
                        [15,15,15,15,15,15,15,15,15],
                        [15,15,15,15,15,15,15,15,15],
                        [15,15,15,15,15,15,15,15,15]
                ]
            }
        }
    
    #conditionally set build dict    
    if build == None:
        build = {
            'phi_list':[0,22.5,45,67.5,90],
            'theta_list': [0.0, 5.0, 90.0, 175.0, 180.0, 185.0, 270.0, 355.0, 360.0],
            'wall_s': 1, #no extrapolating
            'radial_build' : radialBuild
            }

    #conditionally set source mesh parameters
    if source == None:
        source = {
            'num_s' : 11,
            'num_theta' : 81,
            'num_phi' : 61,
            'tor_ext' : 90
        }

    #define export parameters
    if export == None:    
        export = {
            'exclude': ['plasma'],
            'graveyard': False,
            'step_export': True,
            'h5m_export' : 'Cubit',
            'plas_h5m_tag': 'Vacuum',
            'sol_h5m_tag' : 'Vacuum',
            'facet_tol' : 1,
            'len_tol': 5,
            'norm_tol' : None
        }


    #create stellarator geometry and source term
    strengths = parastell.parastell(plas_eq, build, repeat, num_phi=numPhi, num_theta=numTheta, magnets=magnets, source=source, export=export)

    return strengths