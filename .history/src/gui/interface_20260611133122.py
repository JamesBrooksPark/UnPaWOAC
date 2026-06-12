from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout,
    QHBoxLayout, QLabel, QSlider, QStackedWidget, QGridLayout, QSizePolicy, QTabWidget, QComboBox, QFileDialog
)
from PyQt6.QtCore import Qt, QTimer

from gui.interface_helper import load_stylesheet
class GUI(QWidget):
    def __init__(self):
        super().__init__()
        # self.AE = AE
        
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
        
        self.file_loader_btn = QPushButton("Select File", self)
        self.file_loader_btn.clicked.connect(lambda: self.open_file_browser('.wav', 'input wavfile'))
        wav_input_layout. addWidget(self.file_loader_btn)
        
        # == Input Device ==
        device_input_widget = QWidget(self)
        device_input_layout = QHBoxLayout()
        device_input_widget.setLayout(device_input_layout)
        
        device_input_layout_label = QLabel("Device Selector")
        device_input_layout.addWidget(device_input_layout_label)
         
         
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
        
        sofa_filter_layout_label = QLabel("Sofa file filter")
        sofa_filter_layout.addWidget(sofa_filter_layout_label)
        
        # == single impulse files ==
        mono_filter_widget = QWidget(self)
        mono_filter_layout = QHBoxLayout()
        mono_filter_widget.setLayout(mono_filter_layout)
        
        mono_filter_layout_label = QLabel("Mono file filter")
        mono_filter_layout.addWidget(mono_filter_layout_label)
        
        # == diotic file ==
        diotic_filter_widget = QWidget(self)
        diotic_filter_layout = QHBoxLayout()
        diotic_filter_widget.setLayout(diotic_filter_layout)
        
        diotic_filter_layout_label = QLabel("diotic file filter")
        diotic_filter_layout.addWidget(diotic_filter_layout_label)
        
        # Compile filter tabs
        filter_tabs.addTab(sofa_filter_widget,".SOFA file")
        filter_tabs.addTab(mono_filter_widget,"mono file")
        filter_tabs.addTab(diotic_filter_widget,"Diotic file")
        
        
        # Control panel (Play/Pause,stop (greyed out if audio device is used as input), outputdevice , graphics?)
        control_panel_layout = QHBoxLayout()
        
        # Play/Pause
        self.play_pause_button = QPushButton("Play/Pause")
        control_panel_layout.addWidget(self.play_pause_button)
        
        # Stop button
        self.stop_button = QPushButton("Stop")
        control_panel_layout.addWidget(self.stop_button)
        
        # Output device
        self.output_device_layout = QVBoxLayout()
        output_device_header = QLabel("Output Device")
        output_device_dropdown = QComboBox()
        
        self.output_device_layout.addWidget(output_device_header)
        self.output_device_layout.addWidget(output_device_dropdown)
        
        control_panel_layout.addLayout(self.output_device_layout)
        
        
        # ==== Compile all layouts ====
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.addWidget(input_tab_header)
        main_layout.addWidget(input_tabs)
        main_layout.addWidget(filter_tab_header)
        main_layout.addWidget(filter_tabs)
        main_layout.addLayout(control_panel_layout)
        main_layout.addLayout(volume_mute_layout)
        
        
    def on_volume_changed(self, value):
        print(float(value/100.0))
        # self.AE.amplitude = float(value/100.0)
        
    def on_mute_button(self):
        if self.temp_mute_flag:
            self.mute_button.setStyleSheet(self.default_style)
            self.temp_mute_flag = False
        else:
            self.mute_button.setStyleSheet(self.clicked_style_red)
            self.temp_mute_flag = True
        
        # if self.AE.mute_flag:
        #     # self.AudioEngine.mute_flag = False
        #     self.mute_button.setStyleSheet(self.default_style)
        # else:
        #     # self.AudioEngine.mute_flag = True
        #     self.mute_button.setStyleSheet(self.clicked_style_red)
        
    def open_file_browser(self, type, variable):
        
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
                "Select a File",  # Dialog title
                "",  # Initial directory (empty string defaults to current directory)
                "SOFA file (*.sofa)",  # File filters
                )
        if file_path:
            if variable == 'input wavfile':
                self.input_wavfile_path = file_path
                print(self.input_wavfile_path)
            elif variable == 'sofa file':
                self.loaded_sofa_path = file_path
                print(self.input_wavfile_path)
            elif variable == 'mono wav filter':
                self.mono_wav_filter = file_path
                print(self.input_wavfile_path)
            elif variable == 'stereo wav filter':
                self.stereo_wav_filter = file_path
        else:
            print("No file was selected.")
            
    def open_file_browser_sofa(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a File",  # Dialog title
            "",  # Initial directory (empty string defaults to current directory)
            "WAV Audio Files (*.wav)",  # File filters
        )

        # Check if the user actually selected a file or cancelled
        if file_path:
            self.input_wavfile_path = file_path
            print(self.input_wavfile_path)
        else:
            print("No file was selected.")