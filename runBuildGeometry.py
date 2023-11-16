import buildGeometry
import numpy as np
import pickle


radialBuild = {
            'sol': {
                'thickness_matrix': [
                        [3,3,3,3,3,3,3,3,3],
                        [3,3,3,3,3,3,3,3,3],
                        [3,3,3,3,3,3,3,3,3],
                        [3,3,3,3,3,3,3,3,3],
                        [3,3,3,3,3,3,3,3,3]
                ],
                'h5m_tag': 'Vacuum'
            },
            'vacVessel': {
                'thickness_matrix': [
                        [8,8,8,8,8,8,8,8,8],
                        [8,8,8,8,8,8,8,8,8],
                        [8,8,8,8,8,8,8,8,8],
                        [8,8,8,8,8,8,8,8,8],
                        [8,8,8,8,8,8,8,8,8]
                ],
                'h5m_tag': 'FNSFFWstruct'
            },
            'breeder': {
                'thickness_matrix': [
                        [54.2,54.2,54.2,54.2,54.2,54.2,54.2,54.2,54.2],
                        [54.2,54.2,54.2,54.2,54.2,54.2,54.2,54.2,54.2],
                        [54.2,54.2,54.2,54.2,54.2,54.2,54.2,54.2,54.2],
                        [54.2,54.2,54.2,54.2,54.2,54.2,54.2,54.2,54.2],
                        [54.2,54.2,54.2,54.2,54.2,54.2,54.2,54.2,54.2]
                ],
                'h5m_tag': 'FlibeLi60BZ'
            },
            'backWall': {
                'thickness_matrix': [
                        [3,3,3,3,3,3,3,3,3],
                        [3,3,3,3,3,3,3,3,3],
                        [3,3,3,3,3,3,3,3,3],
                        [3,3,3,3,3,3,3,3,3],
                        [3,3,3,3,3,3,3,3,3]
                ],
                'h5m_tag': 'FNSFIBSRstruct'
            },
            'neutronShield': {
                'thickness_matrix': [
                        [14,14,14,14,14,14,14,14,14],
                        [14,14,14,14,14,14,14,14,14],
                        [14,14,14,14,14,14,14,14,14],
                        [14,14,14,14,14,14,14,14,14],
                        [14,14,14,14,14,14,14,14,14]
                ],
                'h5m_tag': 'FNSFIBSRfill'
            },
            'structure': {
                'thickness_matrix': [
                        [15,15,15,15,15,15,15,15,15],
                        [15,15,15,15,15,15,15,15,15],
                        [15,15,15,15,15,15,15,15,15],
                        [15,15,15,15,15,15,15,15,15],
                        [15,15,15,15,15,15,15,15,15]
                ],
                'h5m_tag': 'FNSFIBSR'
            }
        }

magnets = {
                'file': 'coils.txt',
                'cross_section': ['circle', 20],
                'start': 3,
                'stop': None,
                'sample': 6,
                'name': 'magnet_coils',
                'h5m_tag': 'magnets',
                'meshing': True
            }

strengths = buildGeometry.buildModel(radialBuild=radialBuild, magnets=magnets)

#pickle strengths for later
with open('strengths.pickle','wb') as f:
    pickle.dump(strengths, f)

