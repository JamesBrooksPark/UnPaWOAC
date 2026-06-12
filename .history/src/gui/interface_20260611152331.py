from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout,
    QHBoxLayout, QLabel, QSlider, QStackedWidget, QGridLayout, QSizePolicy, QTabWidget, QComboBox, QFileDialog
)
from PyQt6.QtCore import Qt, QTimer

from gui.interface_helper import load_stylesheet
from AudioEngine.audio_engine import AudioEngine
class GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.AE = AudioEngine()
        
        # ==== GUI Window ====
        self.setWindowTitle("UnPaWOSC example")
        self.setGeometry(200, 200, 600, 500)
        
        # Load stylesheets
        # ===== Styles =====
        self.default_style = load_stylesheet("./src/gui/style_files/default_button.qss")
        self.clicked_style = load_stylesheet("./src/gui/style_files/clicked_button.qss")
        self.clicked_style_red = load_stylesheet("./src/gui/style_files/clicked_red_button.qss")
        self.default_color = "lightgray"
        self.clicked_color = "lightgreen"
        
        # ==== volume mute layout ====
        volume_mute_layout = QHBoxLayout()
        # === volume slider ===
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(20)
        volume_mute_layout.addWidget(self.volume_slider)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        
        # ==== Mute button ====
        self.mute_button = QPushButton("Mute")
        volume_mute_layout.addWidget(self.mute_button, alignment=Qt.AlignmentFlag.AlignRight)
        self.mute_button.setStyleSheet(self.default_style)
        # self.AE.mute_flag = False
        self.temp_mute_flag = False
        self.mute_button.clicked.connect(self.on_mute_button)
        
        
        # Input tabs 
        input_tab_header = QLabel("Input selection")
        input_tab_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        input_tabs = QTabWidget()
        # == Input .wav file ==
        wav_input_widget = QWidget(self)
        wav_input_layout = QHBoxLayout()
        wav_input_widget.setLayout(wav_input_layout)
        
        wav_input_layout_label = QLabel("Wav file loader")
        wav_input_layout.addWidget(wav_input_layout_label)
        
        self.file_loader_btn_inputwav = QPushButton("Select File", self)
        self.file_loader_btn_inputwav.clicked.connect(lambda: self.open_file_browser('.wav', 'input wavfile'))
        wav_input_layout. addWidget(self.file_loader_btn_inputwav)
        
        # == Input Device ==
        device_input_widget = QWidget(self)
        device_input_layout = QHBoxLayout()
        device_input_widget.setLayout(device_input_layout)
        
        # device_input_layout_label = QLabel("Device Selector")
        # device_input_layout.addWidget(device_input_layout_label)
         
         
        #  Compile input tabs
        input_tabs.addTab(wav_input_widget, "wav file")
        # input_tabs.addTab(device_input_widget, "Audio Device")
        
        # Filter tabs
        filter_tab_header = QLabel("Filter selection")
        filter_tab_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        filter_tabs = QTabWidget()
        
        # == SOFA file ==
        sofa_filter_widget = QWidget(self)
        sofa_filter_layout = QHBoxLayout()
        sofa_filter_widget.setLayout(sofa_filter_layout)
        
        self.file_loader_btn_sofa = QPushButton("Select .sofa File", self)
        self.file_loader_btn_sofa.clicked.connect(lambda: self.open_file_browser('.sofa', 'sofa_file'))
        sofa_filter_layout. addWidget(self.file_loader_btn_sofa)
        
        # == mono filter files ==
        mono_filter_widget = QWidget(self)
        mono_filter_layout = QHBoxLayout()
        mono_filter_widget.setLayout(mono_filter_layout)
        
        self.file_loader_btn_mono = QPushButton("Select mono File", self)
        self.file_loader_btn_mono.clicked.connect(lambda: self.open_file_browser('.wav', 'mono_filter'))
        mono_filter_layout. addWidget(self.file_loader_btn_mono)
        
        # == stereo filter file ==
        stereo_filter_widget = QWidget(self)
        stereo_filter_layout_1 = QHBoxLayout()
        stereo_filter_layout_2 = QHBoxLayout()
        stereo_filter_layout = QVBoxLayout()
        stereo_filter_layout.addLayout(stereo_filter_layout_1)
        stereo_filter_layout.addLayout(stereo_filter_layout_2)
        
        stereo_filter_widget.setLayout(stereo_filter_layout)
        
        
        self.file_loader_btn_stereo = QPushButton("Select stereo File", self)
        self.file_loader_btn_stereo.clicked.connect(lambda: self.open_file_browser('.wav', 'stereo_filter'))
        stereo_filter_layout_1. addWidget(self.file_loader_btn_stereo)
        
        self.file_loader_btn_stero_0 = QPushButton("Select mono File L", self)
        self.file_loader_btn_stero_0.clicked.connect(lambda: self.open_file_browser('.wav', 'stero_filter',0))
        stereo_filter_layout_2. addWidget(self.file_loader_btn_stero_0)
        
        self.file_loader_btn_stero_1 = QPushButton("Select mono File R", self)
        self.file_loader_btn_stero_1.clicked.connect(lambda: self.open_file_browser('.wav', 'stereo_filter',1))
        stereo_filter_layout_2. addWidget(self.file_loader_btn_stero_1)
        
        # Compile filter tabs
        filter_tabs.addTab(sofa_filter_widget,".SOFA file")
        filter_tabs.addTab(mono_filter_widget,"mono filter")
        filter_tabs.addTab(stereo_filter_widget,"stereo filter")
        
        
        # Control panel (Play/Pause,stop (greyed out if audio device is used as input), outputdevice , graphics?)
        control_panel_layout = QHBoxLayout()
        
        # Play/Pause
        self.play_pause_button = QPushButton("Play/Pause")
        self.play_pause_button.clicked.connect(self.on_play_clicked)
        control_panel_layout.addWidget(self.play_pause_button)
       
        
        # Stop button
        self.stop_button = QPushButton("Stop")
        control_panel_layout.addWidget(self.stop_button)
        
        # Output device
        output_device_layout = QVBoxLayout()
        output_device_header = QLabel("Output Device")
        self.output_device_dropdown = QComboBox()
        self.populate_output_devices()
        
        self.refresh_audiodevice_btn = QPushButton("Refresh Audio Devices")
        self.refresh_audiodevice_btn.clicked.connect(self.on_refresh_clicked)
        
        
        output_device_layout.addWidget(output_device_header)
        output_device_layout.addWidget(self.output_device_dropdown)
        output_device_layout.addWidget(self.refresh_audiodevice_btn)
        
        control_panel_layout.addLayout(output_device_layout)
        
        
        # ==== Compile all layouts ====
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.addWidget(input_tab_header)
        main_layout.addWidget(input_tabs)
        main_layout.addWidget(filter_tab_header)
        main_layout.addWidget(filter_tabs)
        main_layout.addLayout(control_panel_layout)
        main_layout.addLayout(volume_mute_layout)
        
        
        # Test settings:
        self.AE.input_file_path = '/Users/jamesbrookspark/Nextcloud/PhD/Working/Audio/Music/Come Fly With Me_monoleft.wav'
        self.AE.output_device = 8
        
    def closeEvent(self, event):
        self.AudioEngine.stop_clicked()
        super().closeEvent(event)
    def on_volume_changed(self, value):
        self.AE.amplitude = float(value/100.0)
        
    def on_mute_button(self):
        if self.AE.mute_flag:
            self.AE.mute_flag = False
            self.mute_button.setStyleSheet(self.default_style)
        else:
            self.AE.mute_flag = True
            self.mute_button.setStyleSheet(self.clicked_style_red)
        
    def open_file_browser(self, type, variable, n = None):
        if type == '.wav':
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select a File",  # Dialog title
                "",  # Initial directory (empty string defaults to current directory)
                "WAV Audio Files (*.wav)",  # File filters
                )
        elif type == '.sofa':
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select a File",
                "",
                "SOFA file (*.sofa)",
                )
        if file_path:
            if variable == 'input wavfile':
                self.AE.input_file_path = file_path
                print(self.AE.input_file_path)
            elif variable == 'sofa file':
                self.loaded_sofa_path = file_path
                print(self.loaded_sofa_path)
            elif variable == 'mono_filter':
                self.mono_wav_filter = file_path
                print(self.mono_wav_filter)
            elif variable == 'stereo_filter':
                if n == 0:
                    self.stereo_wav_filter_0 = file_path
                    print(self.stereo_wav_filter_0)
                elif n == 1:
                    self.stereo_wav_filter_1 = file_path
                    print(self.stereo_wav_filter_1)
                else:
                    self.stereo_wav_filter = file_path
                    print(self.stereo_wav_filter)
        else:
            print("No file was selected.")
            
    def populate_output_devices(self,devices = None):
        self.output_device_dropdown.clear()
        if not devices:
            devices = self.AE.get_output_devices()
        for device in devices:
            display_text = f"Device {device['index']}: {device['name']}"
            
            self.output_device_dropdown.addItem(display_text, device['index'])
            
    def on_refresh_clicked(self):
        updated_devices = self.AE.restart_device()
        self.populate_output_devices(updated_devices)
        
    def get_selected_output_device_index(self):
        device_index = self.output_device_dropdown.currentData()
        
        if device_index is None:
            print("No output device is currently selected.")
            return None
            
        self.AE.output_device = device_index
                
    def on_play_clicked(self):
        # self.get_selected_output_device_index()
        self.AE.amplitude = 0.2
        self.AE.play_clicked()
        
        

        
        