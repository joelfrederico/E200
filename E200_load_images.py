import tifffile
import h5py as _h5
import numpy as _np
import ipdb
import matplotlib.pyplot as _plt
# import mytools as _mt
from .E200_api_getdat import E200_api_getdat
import scipy.io as _spio
from .get_remoteprefix import get_remoteprefix
import os
from .classes import *
import logging
loggerlevel = logging.DEBUG
logger      = logging.getLogger(__name__)


def E200_load_images(imgstr, UID=None):
    logger.log(level=loggerlevel, msg='Loading images...')
    try:
        remote_bool = imgstr._hdf5.file['data']['VersionInfo']['remotefiles']['dat'][0, 0]
    except:
        remote_bool = True
    if remote_bool:
        prefix = get_remoteprefix()
    else:
        prefix = ''

    imgdat = E200_api_getdat(imgstr, UID=UID)

    imgs = [tifffile.imread(os.path.join(prefix, val[0:])) for val in imgdat.dat]
    for i, img in enumerate(imgs):
        imgs[i] = _np.float64(img)

    logger.log(level=loggerlevel, msg='Loading backgrounds...')

    imgbgdat = E200_api_getdat(imgstr, fieldname='background_dat', UID=imgdat.uid)

    for i, val in enumerate(imgbgdat.dat):
        # print val
        val = os.path.join(prefix, val[0:])
        mat = _spio.loadmat(val)
        imgbg = mat['img']
        
        if imgs[i].shape[0] == imgbg.shape[1]:
            imgbg = _np.transpose(imgbg)

        imgs[i] = _np.fliplr(_np.abs(imgs[i]-_np.float64(imgbg)))

    return E200_Image(images=_np.array(imgs), dat=imgdat.dat, uid=imgdat.uid)
