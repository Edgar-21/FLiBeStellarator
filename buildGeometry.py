import parastell
import pickle

#set filename of vmec file
plas_eq = 'plas_eq.nc'

#Set number of periods present in vmec
numPeriods = 4

#Define radial build dict

radialBuild = {
    'phi_list':[0,22.5,45,67.5,90],
    'theta_list': [0.0, 5.0, 90.0, 175.0, 180.0, 185.0, 270.0, 355.0, 360.0],
    'wall_s': 1.2, #no extrapolating
    'radial_build':{
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
                    [32,32,32,32,32,32,32,32,32],
                    [32,32,32,32,32,32,32,32,32],
                    [32,32,32,32,32,32,32,32,32],
                    [32,32,32,32,32,32,32,32,32],
                    [32,32,32,32,32,32,32,32,32]
            ]
        },
        'structure': {
            'thickness_matrix': [
                    [28,28,28,28,28,28,28,28,28],
                    [28,28,28,28,28,28,28,28,28],
                    [28,28,28,28,28,28,28,28,28],
                    [28,28,28,28,28,28,28,28,28],
                    [28,28,28,28,28,28,28,28,28]
            ]
        }
    }
    }

#generate 1 period
genPeriods = 1
#toroidal x secs to use in sweep per period
numPhi = 60
#poloidal points at each x section
numTheta = 100
#magnet parameters
magnets = None #for now

#source mesh parameters
source = {
    'num_s' : 11,
    'num_theta' : 81,
    'num_phi' : 241
}

#define export parameters
export = {
    'exclude': [],
    'graveyard': False,
    'step_export': 'Cubit',
    'plas_h5m_tag': 'Vacuum',
    'facet_tol' : 1,
    'len_tol': 5,
    'norm_tol' : None
}

#create stellarator geometry and save source term
strengths = parastell.parastell(plas_eq, numPeriods, radialBuild, genPeriods, num_phi=numPhi, num_theta=numTheta, magnets=magnets, source=source, export=export)

#pickle strengths for later
with open('strengths.pickle','wb') as f:
    pickle.dump(strengths, f)
