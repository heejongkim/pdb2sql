import numpy as np
from time import time
from .pdb2sqlcore import pdb2sql

'''
This file contains several transformations of the
molecular coordinate that might be usefull during the
definition of the data set.
'''

def get_rot_axis_angle(seed=None):
    """Get the rotation angle/axis.

    Args:
        seed(int): random seed for numpy

    Returns:
        list(float): axis of rotation
        float: angle of rotation
    """
    # define the axis
    # uniform distribution on a sphere
    # http://mathworld.wolfram.com/SpherePointPicking.html
    if seed != None:
        np.random.seed(seed)

    u1, u2 = np.random.rand(), np.random.rand()
    teta, phi = np.arccos(2 * u1 - 1), 2 * np.pi * u2
    axis = [np.sin(teta) * np.cos(phi),
            np.sin(teta) * np.sin(phi),
            np.cos(teta)]


    return axis, angle


def translation(db, vect, **kwargs):
    xyz = _get_xyz(db, **kwargs)
    xyz += vect
    _update(db, xyz, **kwargs)


def rot_axis(db, axis, angle, **kwargs):
    xyz = _get_xyz(db, **kwargs)
    xyz = rot_xyz_around_axis(xyz, axis, angle)
    _update(db, xyz, **kwargs)


def rot_euler(db, alpha, beta, gamma, **kwargs):
    """Rotate molecule from Euler rotation axis.

    Args:
        alpha (float): angle of rotation around the x axis
        beta (float): angle of rotation around the y axis
        gamma (float): angle of rotation around the z axis
        **kwargs: keyword argument to select the atoms.
            See pdb2sql.get()
    """
    xyz = _get_xyz(db, **kwargs)
    xyz = _rotation_euler(xyz, alpha, beta, gamma)
    _update(db, xyz, **kwargs)


def rot_mat(db, mat, **kwargs):
    """Rotate molecule from a rotation matrix.

    Args:
        mat (np.array): 3x3 rotation matrix
        **kwargs: keyword argument to select the atoms.
            See pdb2sql.get()
    """
    xyz = _get_xyz(db, **kwargs)
    xyz = _rotation_matrix(xyz, mat)
    _update(db, xyz, **kwargs)
    # define the rotation angle
    angle =  2 * np.pi * np.random.rand()


def rot_xyz_around_axis(xyz, axis, angle, center=None):
    """Get the rotated xyz.

    Args:
        xyz(np.array): original xyz coordinates
        axis (list(float)): axis of rotation
        angle (float): angle of rotation
        center (list(float)): center of rotation,
            defaults to the mean of input xyz.

    Returns:
        np.array: rotated xyz coordinates
    """

    # check center
    if center is None:
        center = np.mean(xyz, 0)

    # get the data
    ct, st = np.cos(angle), np.sin(angle)
    ux, uy, uz = axis

    # definition of the rotation matrix
    # see https://en.wikipedia.org/wiki/Rotation_matrix
    rot_mat = np.array([[ct + ux**2 * (1 - ct),
                         ux * uy * (1 - ct) - uz * st,
                         ux * uz * (1 - ct) + uy * st],
                        [uy * ux * (1 - ct) + uz * st,
                         ct + uy**2 * (1 - ct),
                         uy * uz * (1 - ct) - ux * st],
                        [uz * ux * (1 - ct) - uy * st,
                         uz * uy * (1 - ct) + ux * st,
                         ct + uz**2 * (1 - ct)]])

    # apply the rotation
    return np.dot(rot_mat, (xyz - center).T).T + center


def _rotation_euler(xyz, alpha, beta, gamma):

    # precomte the trig
    ca, sa = np.cos(alpha), np.sin(alpha)
    cb, sb = np.cos(beta), np.sin(beta)
    cg, sg = np.cos(gamma), np.sin(gamma)

    # get the center of the molecule
    xyz0 = np.mean(xyz, 0)

    # rotation matrices
    rx = np.array([[1, 0, 0], [0, ca, -sa], [0, sa, ca]])
    ry = np.array([[cb, 0, sb], [0, 1, 0], [-sb, 0, cb]])
    rz = np.array([[cg, -sg, 0], [sg, cg, 0], [0, 0, 1]])

    # get rotation matrix
    rot_mat = np.dot(rz, np.dot(ry, rx))

    # apply the rotation
    return np.dot(rot_mat, (xyz - xyz0).T).T + xyz0


def rotation_matrix(xyz, rot_mat, center=True):
    if center:
        xyz0 = np.mean(xyz)
        return np.dot(rot_mat, (xyz - xyz0).T).T + xyz0
    else:
        return np.dot(rot_mat, (xyz).T).T


def _get_xyz(db, **kwargs):
    return np.array(db.get('x,y,z', **kwargs))


def _update(db, xyz, **kwargs):
    db.update('x,y,z', xyz, **kwargs)


if __name__ == "__main__":

    t0 = time()
    db = pdb2sql('5hvd.pdb')
    print('SQL %f' % (time() - t0))

    tr = np.array([1, 2, 3])
    translation(db, tr, chainID='A')
