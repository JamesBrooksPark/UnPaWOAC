import numpy as np

class UnPaWOlAC():
    def __init__(self, block_size, h_init, input_channels):
        """Initialize Uniform Partitioned Weighted Overlap convolver with partitioned convolution.

        Args:
            block_size (int): Processing block size (L)
            h_init (np.ndarray): Initial filter coefficients
            input_channels (int): Number of input channels
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
        self.calculate_partitions(h_new)
        
    def UPC_Convolution(self, data):
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
        