from PyQt6.QtCore import QObject
import numpy as np
import soundfile as sf
import pyaudio
import wave
import time
import threading 

from UnPaWOSC.UnPaWOlAC import UnPaWOlAC

class AudioEngine(QObject):
    def __init__(self):
        super().__init__()
        
        self.UPC = None
        
        # Playback variables
        self.p = None
        self.initialize_pyaudio()
        self.block_size = 2**8
        self.is_playing = False
        self.paused = True
        self.stop_player = False
        self.output_device = None
        self.input_file_path = None
        self.amplitude = 0
        
        self.mute_flag = False
        
        # Filter variables
        self.filter = None
        self.filter_Fs = None
        self.N_filter_channels = None
        self.filter_type = None
        self.filter_bool = False
        
    def initialize_pyaudio(self):
        if self.p is not None:
            try:
                self.p.terminate()
            except Exception as e:
                print(f"Error terminating old PyAudio instance: {e}")
        self.p = pyaudio.PyAudio()
        
    def get_output_devices(self):
        devices = []
        device_count = self.p.get_device_count()
        for i in range(device_count):
            try:
                device_info = self.p.get_device_info_by_index(i)
                if device_info.get('maxOutputChannels', 0) > 0:
                    device_name = device_info.get('name')
                    device_index = device_info.get('index')
                    
                    if isinstance(device_name, bytes):
                        device_name = device_name.decode('utf-8', errors='ignore')
                    
                    devices.append({
                        "index": device_index,
                        "name": device_name
                    })
            except Exception as e:
                print(f"Error querying device {i}: {e}")
        return devices
    
    def restart_device(self):
        self.stop_clicked()
        if hasattr(self, 'play_thread') and self.play_thread.is_alive():
            self.play_thread.join(timeout=2.0)
            
        self.initialize_pyaudio()
        return self.get_output_devices()
            
    # Loading filters
    def load_filter(self, type, path):
        raw_filter, self.filter_Fs = sf.read(path)
        filter_array = np.asarray(raw_filter)

        if filter_array.ndim == 1:
            self.filter = filter_array[np.newaxis, :]
        else:
            self.filter = filter_array.T

        self.UPC = UnPaWOlAC(self.block_size, self.filter)
        if type == "mono_filter":
            self.N_filter_channels = 1
            
        elif type == "stereo_filter":
            self.N_filter_channels = 2
        
    # Loading Audio        
    def play_clicked(self, restart = False):
        if restart:
            self.restart_device()
        if self.input_file_path:
            self.stop_player = False
            if not self.is_playing:
                self.paused = not self.paused
                self.is_playing = True
                self.play_thread = threading.Thread(target = self.audio_player)
                self.play_thread.start()
            elif self.is_playing:
                self.paused = not self.paused
        else:
            print("No audio file selected")
            
    def stop_clicked(self):
        self.stop_player = True
        self.is_playing = False
        self.paused = True
        
    # Audio playback
    def audio_player(self):
        # assert self.filter, "No filter loaded."
        assert self.input_file_path, "No content_path provided."
        assert self.output_device, "No output device selected"
        try:
            with wave.open(self.input_file_path, 'rb') as wf:
                d_type = self.p.get_format_from_width(wf.getsampwidth())
                Fs = wf.getframerate()
                self.N_content_channels = wf.getnchannels()
                
                player = self.p.open(
                    format=d_type,
                    channels=2,
                    output_device_index=self.output_device,
                    rate=wf.getframerate(),
                    output=True,
                    frames_per_buffer=self.block_size
                )
                if self.filter_bool:
                    if self.filter_Fs != Fs:
                        raise ValueError("filter and content sampling rates do not match")
                
                # Create empty matrices for oputput data
                interleaved_data = np.zeros(self.block_size * 2, dtype=np.int16) 
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
                    
                        # in case length of file is not interger divisible by blocksize
                        if self.N_content_channels > 1:
                            if np.shape(data)[1] != self.block_size:
                                data = np.append(data,np.zeros(self.block_size-len(data)), axis = 1)
                        else:
                            if len(data) != self.block_size:
                                data = np.append(data,np.zeros(self.block_size-len(data)))
                                
                        # convert data to numpy data
                        data = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32)
                        if self.N_filter_channels == 1:
                            data = self.ensure_mono(data)
                        else:
                            if self.N_content_channels > 1:
                                data = self.multi_channel_data_mat(data)
                        
                        print("here")
                        if not self.mute_flag:
                            if self.filter_bool and self.filter is not None:
                                if self.UPC is None:
                                    self.UPC = UnPaWOlAC(self.block_size, self.filter)
                               
                                # Update convolver
                                if self.filter_type == "mono_filter":
                                    self.UPC.update_filter(self.filter)
                                elif self.filter_type == "stereo_filter":
                                    self.UPC.update_filter(self.filter)
                                elif self.filter_type == "sofa_file":
                                    self.UPC.update_filter(self.filter)
                                    self.UPC.update_sofa()
                                # Uniformly partitioned convolution and apply attenuation from volume slider
                                data_out = self.UPC.UPC_Convolution(data) * self.amplitude
                            else:
                                data_out = data * self.amplitude
                                
                            # Reduce amplitude
                            data_out *= 0.1
                                                    
                        else:
                            data_out[:,:] = 0
                            
                 
                        # Interleave channels to a single interleaved vector for PyAudio
                        if self.N_content_channels > 1:
                            print(np.shape(data_out))
                            for ii in range(2):
                                interleaved_data[ii :: 2] = data_out[ii, :]
                        else:
                            print(np.shape(data_out))
                            interleaved_data[0 :: 2] = data_out

                        # Write interleaved data to PyAudio
                        player.write(interleaved_data.tobytes())
                
        except Exception as e:
            print(f"Audio Playback Error: {e}")
        finally:
            if 'player' in locals() and player.is_active():
                player.stop_stream()
                player.close()
            if 'p' in locals():
                self.p.terminate()
            
    def ensure_mono(self, data):
        # Convert to mono input
        if self.N_content_channels > 1:
            data = data[::self.N_content_channels]
        else:
            data = data
        return data
            
    def multi_channel_data_mat(self, data):
        data_out = np.zeros([self.N_content_channels, int(len(data)/self.N_content_channels)])
        for ii in range(self.N_content_channels):
            data_out[ii,:] = data[ii::self.N_content_channels]
            
        return data_out
    
    
    
# Data shape for mono or stereo is not working, need to fix for mono signals and filters. transform data_out to matrix with channels