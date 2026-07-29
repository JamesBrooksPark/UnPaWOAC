import numpy as np

class UnPaWOlAC():
    def __init__(self, block_size, h_init, input_channels, sofa = False):
        self.L = block_size 
        self.LL = self.L *2
        self.N = 2 * self.LL
        if sofa:
            self.N_inputChanels = 1
        else:
            self.N_inputChanels = input_channels
        
        self.calculate_partitions(h_init)
        
        self.win = np.hanning(self.LL)
        if self.N_inputChanels > 1:
            self.win = np.tile(self.win, (self.N_inputChanels, 1))
   
        self.conv_mem = np.zeros((self.num_channels, self.num_partitions, self.N//2+1), dtype=np.complex64)
        
        self.overlap = np.zeros([self.N_inputChanels, self.num_channels,self.N], dtype=np.float32).squeeze()
        self.data_mem = np.zeros([self.N_inputChanels, self.L]).squeeze()
        
    def calculate_partitions(self, h):
        if h.ndim > 1:
            self.num_channels = np.shape(h)[0]
            I = np.shape(h)[1]
        else:
            self.num_channels = 1
            I = len(h)
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
        
        print(f"self.data_men:  {np.shape(self.data_mem)}")
        print(f"data:           {np.shape(data)}")
        print(f"self.win:       {np.shape(self.win)}")
        process_data = np.append(self.data_mem, data, axis = 1) * self.win  
        x_padded = np.zeros([self.N_inputChanels, self.N]).squeeze()
        if self.N_inputChanels > 1:
            x_padded[:,:self.LL] = process_data
        else:
            x_padded[:self.LL] = process_data
        self.data_mem = data.copy()
        X = np.fft.rfft(x_padded)

        print("here")
        print(self.num_channels)
        y = np.zeros([self.num_channels,self.N])
        for c in range(self.num_channels):
            for p in range(self.num_partitions):
                if self.N_inputChanels > 1:
                    self.
                else:
                    self.conv_mem[c,p,:] += X * self.partitions[c,p,:]
                
            y[c,:] = np.fft.irfft(self.conv_mem[c,0,:], self.N)
        print("here4")
        
        self.conv_mem[:,:-1,:] = self.conv_mem[:,1:,:]
        self.conv_mem[:,-1,:] = 0 
        
        
        y += self.overlap
        out = y[:,:self.L].astype(np.float32)
        self.overlap[:,:-self.L] = y[:,self.L:]
        self.overlap[:,-self.L:] = 0
        return out
        