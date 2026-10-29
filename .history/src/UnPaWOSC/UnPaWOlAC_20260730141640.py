"""UnPaWOlAC: UnPartitioned Overlap-Add Convolver.

This module provides a lightweight FFT-based partitioned convolution class
that supports multiple channels and input streams. It is intended for
real-time block processing using overlap-add with a Hanning window.

Usage:
    conv = UnPaWOlAC(block_size, h_init, input_channels)
    out = conv.UPC_Convolution(data)

All arrays are numpy arrays and the convolution operates in the FFT domain.
"""

import numpy as np

class UnPaWOlAC():
        """Partitioned FFT convolution helper.

        Parameters
        - block_size: int, processed block length L
        - h_init: array-like, initial impulse response(s). Can be 1D (single
            channel) or 2D (num_channels x impulse_length).
        - input_channels: int, number of separate input channels to process.
        """
        def __init__(self, block_size, h_init, input_channels):
        
        self.L = block_size 
        self.LL = self.L *2
        self.N = 2 * self.LL

        self.N_inputChannels = input_channels
            
        self.calculate_partitions(h_init)
        
        self.win = np.hanning(self.LL)
        if self.N_inputChannels > 1:
            self.win = np.tile(self.win, (self.N_inputChannels, 1))
   
        self.conv_mem = np.zeros((self.num_channels, self.num_partitions, self.N//2+1), dtype=np.complex64)
        
        self.overlap = np.zeros([self.num_channels,self.N], dtype=np.float32)
        self.data_mem = np.zeros([self.N_inputChannels, self.L]).squeeze()
        
    def calculate_partitions(self, h):
        """Partition and FFT the impulse response(s).

        The impulse responses are split into blocks of length L and each
        block is transformed with an N-point real FFT and stored.
        """
        h = np.atleast_2d(h).astype(np.float32)
        if h.shape[0] == 1 and h.shape[1] > 1:
            h = h
        elif h.ndim == 1 or (h.shape[0] > h.shape[1]):
            h = h[np.newaxis, :]
        
        self.num_channels = h.shape[0]
        I = h.shape[1]
        self.num_partitions = int(np.ceil(I/self.L))
        
        new_partitions = np.zeros([self.num_channels, self.num_partitions, self.N//2+1], dtype=np.complex64)
        
        for p in range(self.num_partitions):
            idx = slice(p * self.L, (p+1) * self.L)
            for c in range(self.num_channels):
                new_partitions[c,p,:] = np.fft.rfft(h[c,idx], n=self.N)  

        self.partitions = new_partitions
        

    def update_filter(self, h_new):
        """Replace the current filter with h_new and recompute partitions."""
        self.calculate_partitions(h_new)
        
    def UPC_Convolution(self, data):
        """Process one input block and return the convolution output block.

        'data' should be shape (input_channels, L) if input_channels>1,
        otherwise shape (L,). Returns output of shape (num_channels, L).
        """
        if self.N_inputChannels > 1:
            process_data = np.append(self.data_mem, data, axis = 1) * self.win
        else:
            process_data = np.append(self.data_mem, data) * self.win
        x_padded = np.zeros([self.N_inputChannels, self.N]).squeeze()
        if self.N_inputChannels > 1:
            x_padded[:,:self.LL] = process_data
        else:
            x_padded[:self.LL] = process_data
        self.data_mem = data.copy()
        X = np.fft.rfft(x_padded)

        y = np.zeros([self.num_channels,self.N])
        for c in range(self.num_channels):
            for p in range(self.num_partitions):
                if self.N_inputChannels > 1:
                    self.conv_mem[c,p,:] += X[c,:] * self.partitions[c,p,:]
                else:
                    self.conv_mem[c,p,:] += X * self.partitions[c,p,:]
                    
            y[c,:] = np.fft.irfft(self.conv_mem[c,0,:], self.N)

        self.conv_mem[:,:-1,:] = self.conv_mem[:,1:,:]
        self.conv_mem[:,-1,:] = 0 
        y += self.overlap
        out = y[:,:self.L].astype(np.float32)
        self.overlap[:,:-self.L] = y[:,self.L:]
        self.overlap[:,-self.L:] = 0
        return out
        