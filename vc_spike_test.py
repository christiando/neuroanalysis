import numpy as np
import scipy.ndimage as ndi
import pyqtgraph as pg
from neuroanalysis.nwb_viewer import PlotGrid

# Load test data
data = np.load('test_data/evoked_spikes/vc_evoked_spikes.npz')['arr_0']
dt = 20e-6

# Initialize Qt
pg.mkQApp()

# Create a window with a grid of plots (N rows, 1 column)
win = PlotGrid()
win.set_shape(data.shape[0], 1)
win.show()

# Loop over all 10 channels
for i in range(data.shape[0]):
    # select the data for this channel
    trace = data[i, :, 0]
    stim = data[i, :, 1]

    # select the plot we will use for this trace
    plot = win[i, 0]

    # link all x-axes together
    plot.setXLink(win[0, 0])
    xaxis = plot.getAxis('bottom')
    if i == data.shape[0]-1:
        xaxis.setLabel('Time', 's')
    else:
        xaxis.hide()

    # use stimulus to find pulse edges
    diff = np.diff(stim)   # np.diff() gives first derivative
    on_times = np.argwhere(diff > 0)[:,0]
    off_times = np.argwhere(diff < 0)[:,0]

    # decide on the region of the trace to focus on
    start = on_times[1] - 1000
    stop = off_times[8] + 1000
    chunk = trace[start:stop]

    # plot the selected chunk
    t = np.arange(chunk.shape[0]) * dt
    plot.plot(t, chunk)

    # detect spike times
    delay = int(100e-6 / dt)  # 100us window after stimulus should be ignored
    peak_inds = []
    rise_inds = []
    for j in range(8):  # loop over pulses
        # select just the portion of the chunk that contains the pulse
        pstart = on_times[j+1] - start + delay
        pstop = off_times[j+1] - start
        # find the location of the minimum value during the pulse
        sigma = 10e-6 / dt
        smooth = ndi.gaussian_filter(chunk[pstart:pstop], sigma)
        peak_ind = np.argmin(smooth) + pstart
        # a spike is detected only if the peak is at least 50pA less than the final value before pulse offset
        margin = 50e-12
        if chunk[peak_ind] < chunk[pstop] - margin:
            peak_inds.append(peak_ind)
            
            # Walk backward to the point of max dv/dt
            dvdt = np.diff(smooth)
            rise_ind = np.argmin(dvdt[:peak_ind]) + pstart
            rise_inds.append(rise_ind)

    # display spike rise and peak times as ticks
    pticks = pg.VTickGroup(np.array(peak_inds) * dt, yrange=[0, 0.3], pen='r')
    rticks = pg.VTickGroup(np.array(rise_inds) * dt, yrange=[0, 0.3], pen='y')
    plot.addItem(pticks)
    plot.addItem(rticks)
    
    
    