import numpy as np
import pylab as pl
from matplotlib.colors import hsv_to_rgb

S, H = np.mgrid[0:1:50j, 0:1:180j]  # 50j means dividing into 50 sections
V = np.ones_like(S)
# V = np.full_like(S, 0.67)
HSV = np.dstack((H,S,V))
RGB = hsv_to_rgb(HSV)
pl.imshow(RGB, origin="lower", extent=[0, 360, 0, 1], aspect=180)
pl.tick_params(labelsize=12)
pl.xlabel("$H$",fontsize=16)
pl.ylabel("$S$",fontsize=16)
pl.title("$V_{HSV}=1$",fontsize=16)
pl.show()
