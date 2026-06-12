from PyQt6.QtCore import QObject
import numpy as np
import soundfile as sf
import pyaudio as pya
import wave
import time

def AudioEngine(QObject):
    def __init__(self):
        super().__init__()
        
        
        # Playback variables
        self.block_size = 2**8
        self.is_playing = False
        self.stop_player = False
        
        self.mute_flag = False
        
        # Filter variables
        self.filter = None
        self.filter_Fs = None
        self.N_filter_channels = None
        
        
    def get_audio_devices(self):
        
    # Loading filters
    def load_filter(self, type, path):
        if type == "diotic":
            load_dicotic(path)
            
        elif type == "dichotic":
            load_dichotic(path)
            
    def load_dicotic(self, path):
        self.filter, self.filter_Fs = sf.read(path)
        self.N_filter_channels = 1
        
    def load_dichotic(self,path):
        self.filter, self.filter_Fs = sf.read(path)
        self.N_filter_channels = 1
        
    # Loading Audio
    def select_wav(self,path):
        self.content_path = path
    
    # Audio playback
    def audio_playback(self):
        assert self.filter, "No filter loaded."
        assert self.content_path, "No content_path provided."
        assert self.output_device, "No output device selected"
        

        try:
            p = pya.PyAudio()
            with wave.open(self.content_path, 'rb') as wf:
                d_type = p.get_format_from_width(wf.getsampwidth())
                Fs = wf.getframerate()
                N_content_channels = wf.getnchannels()
                
                player = p.open(
                    format=d_type,
                    channels=2,
                    output_device_index=self.output_device,
                    rate=wf.getframerate(),
                    output=True,
                    frames_per_buffer=self.block_size
                )
                
                if self.filter_Fs != Fs:
                    raise ValueError("filter and content sampling rates do not match")
                
                # Create empty matrices for oputput data
                interleaved_data = np.empty(self.block_size * 2, dtype=np.int16) 
                data_out = np.zeros([2, self.block_size], dtype=np.float32)                
                
                while self.is_playing:  
                    if self.stop_player:
                        break
                    while self.paused:
                        time.sleep(0.001)
                        if self.stop_player: # Check again inside the pause loop
                            break
                    else:
                        # Read current block
                        raw_data = wf.readframes(self.block_size)
                        if not raw_data:
                            wf.rewind() 
                            raw_data = wf.readframes(self.block_size)
                            if not raw_data: break 
                        
                        # convert data to numpy data
                        data = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32)
                        
                        # in case length of file is not interger divisible by blocksize
                        if len(data) != self.block_size:
                            data = np.append(data,np.zeros(self.block_size-len(data)))
                            
                        if not self.mute_flag:
                            # Update convolver
                            self.update_sofa()
                            
                            # Uniformly partitioned convolution and apply attenuation from volume slider
                            data_out = self.UPC.UPC_Convolution(data) * self.amplitude
                            
                            # Reduce amplitude
                            data_out = data_out * 0.1
                        
                        else:
                            data_out[:] = 0
                            
                        # Interleave stereo channels to a single interleaved vector for PyAudio
                        for ii in range(2):
                            interleaved_data[ii :: 2] = data_out[ii, :]

                        # Write interleaved data to PyAudio
                        player.write(interleaved_data.tobytes())
                
        except Exception as e:
            print(f"Audio Playback Error: {e}")
        finally:
            if 'player' in locals() and player.is_active():
                player.stop_stream()
                player.close()
            if 'p' in locals():
                p.terminate()
            