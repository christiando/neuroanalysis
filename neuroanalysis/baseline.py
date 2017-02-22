"""
Baseline detection and detrending tools.


"""
from __future__ import division
import numpy as np
import scipy.stats, scipy.signal

    
def adaptive_detrend(data, x=None, threshold=3.0):
    """Linear detrend where the baseline is estimated excluding outliers."""
    if x is None:
        x = data.xvals(0)
    
    d = data.view(ndarray)
    
    d2 = scipy.signal.detrend(d)
    
    stdev = d2.std()
    mask = abs(d2) < stdev*threshold
    
    lr = scipy.stats.linregress(x[mask], d[mask])
    base = lr[1] + lr[0]*x
    d4 = d - base
    
    return d4
    

def float_mode(data, bins=None):
    """Returns the most common value from a floating-point array by binning
    values together.
    """
    if bins is None:
        # try to guess on a resonable bin count
        bins = np.clip(int(len(data)**0.5), 3, 500)
    y, x = np.histogram(data, bins=bins)
    ind = np.argmax(y)
    mode = 0.5 * (x[ind] + x[ind+1])
    return mode


def mode_filter(data, window=500, step=None, bins=None):
    """Sliding-window mode filter."""
    d1 = data.view(np.ndarray)
    vals = []
    l2 = int(window/2.)
    if step is None:
        step = l2
    i = 0
    while True:
        if i > len(data)-step:
            break
        vals.append(mode(d1[i:i+window], bins))
        i += step
            
    chunks = [np.linspace(vals[0], vals[0], l2)]
    for i in range(len(vals)-1):
        chunks.append(np.linspace(vals[i], vals[i+1], step))
    remain = len(data) - step*(len(vals)-1) - l2
    chunks.append(np.linspace(vals[-1], vals[-1], remain))
    d2 = np.hstack(chunks)
    return d2
    

def mode_detrend(data, window=500, bins=None, threshold=3.0):
    """Linear detrend using the mode of the values within a window at the beginning
    and end of the trace."""
    d1 = data.view(np.ndarray)
    ends = [d1[:window], d1[-window:]]
    y = [float_mode(w, bins=bins) for w in ends]
        
    x0 = window / 2.0
    x1 = len(data) - x0
    m = (y[1] - y[0]) / (x1 - x0)
    b0 = y[1] - m * x1
    b1 = b0 + m * len(data)
    
    base = np.linspace(b0, b1, len(data))
    return d1 - base