"""Uniform Partitioned Weighted OverLap Add Convolution (UnPaWOlAC).

This module provides a class implementing partitioned convolution using
uniform partitions, overlap-add and a Hann window for block processing.
"""

import numpy as np

class UnPaWOlAC():
    """Uniform Partitioned Weighted Overlap-Add Convolution engine.
    
    Implements efficient real-time convolution using partitioned FFT-based
    processing with overlap-add synthesis and Hann windowing. Supports both
    single-channel and multi-channel filtering.
    
    Attributes:
        L (int): Block size for processing.
        LL (int): Window length (2 * L).
        N (int): FFT size (4 * L).
        N_inputChannels (int): Number of input channels.
        num_channels (int): Number of filter channels.
        num_partitions (int): Number of FFT partitions for the filter.
        partitions (np.ndarray): FFT-transformed filter partitions of shape
            (num_channels, num_partitions, N//2+1) in complex64.
        win (np.ndarray): Hann window of shape (num_channels, LL) or (LL,).
        conv_mem (np.ndarray): Circular buffer for convolution state.
        overlap (np.ndarray): Overlap-add buffer for output reconstruction.
        data_mem (np.ndarray): Input history buffer for windowing.
    """
    def __init__(self, block_size, h_init, input_channels):
        """Initialize the UnPaWOlAC partitioned convolution engine.

        Args:
            block_size (int): Processing block size (L). Determines FFT size
                as 4*L and window length as 2*L. Typical values: 64, 128, 256.
            h_init (np.ndarray): Initial filter coefficients. Can be:
                - 1D array of shape (num_taps,) for single-channel filter.
                - 2D array of shape (num_channels, num_taps) for multi-channel.
            input_channels (int): Number of input audio channels to process.
                Should match the channel count in input data to UPC_Convolution().

        Raises:
            ValueError: If block_size is not positive or h_init is empty.
        """
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
        """Calculate FFT partitions of filter coefficients for partitioned convolution.

        Decomposes the impulse response into uniform partitions of size L,
        applies zero-padding to FFT size N, and computes the FFT of each
        partition. Results are stored in self.partitions for use in
        frequency-domain convolution.

        The filter is normalized to 2D shape (num_channels, num_taps) before
        partitioning. If input is 1D, it is treated as a single-channel filter.

        Args:
            h (np.ndarray): Filter coefficients. Can be:
                - 1D array of shape (num_taps,) for single-channel.
                - 2D array of shape (num_channels, num_taps) for multi-channel.
                Data type is cast to float32.

        Sets:
            self.num_channels (int): Number of channels in the filter.
            self.num_partitions (int): Number of partitions, computed as
                ceil(num_taps / L).
            self.partitions (np.ndarray): FFT-transformed partitions of shape
                (num_channels, num_partitions, N//2+1) in complex64.

        Notes:
            - Each partition is zero-padded to length N before FFT.
            - Real FFT (rfft) is used, yielding N//2+1 frequency bins.
            - Partitions are stored in frequency domain for efficient
              multiplication during convolution.
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
        """Update the filter coefficients.

        Args:
            h_new (np.ndarray): New filter coefficients, either 1D or 2D array
        """
        self.calculate_partitions(h_new)
        
    def UPC_Convolution(self, data):
        """Process one block of input data and return the convolved output block.

        Args:
            data (np.ndarray): Input block of shape (input_channels, L) for multichannel
                or shape (L,) for single-channel.

        Returns:
            np.ndarray: Output block of shape (num_channels, L).
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
        