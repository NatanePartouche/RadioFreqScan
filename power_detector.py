#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# GNU Radio version: 3.10.12.0

# Imports for GUI and GNU Radio functionality
from PyQt5 import Qt  # PyQt5 for creating the application window
from gnuradio import qtgui  # Qt GUI elements from GNU Radio
from gnuradio import blocks  # Basic GNU Radio signal processing blocks
from gnuradio import filter  # Filtering blocks
from gnuradio.filter import firdes  # FIR filter design utilities
from gnuradio import gr  # GNU Radio core
from gnuradio.fft import window  # Windowing functions for FFT
import sys  # System-level access (e.g. exit, arguments)
import signal  # Used for handling termination signals like Ctrl+C
from argparse import ArgumentParser  # Command-line argument parsing
from gnuradio.eng_arg import eng_float, intx  # Engineering units for command-line arguments
from gnuradio import eng_notation  # Engineering notation helpers (e.g. 10k, 2.4M)
from gnuradio import soapy  # Interface to SoapySDR-compatible devices (like RTL-SDR)
import sip  # Used for wrapping C++ Qt widgets into Python
import threading  # Threading primitives (used for synchronization)


# Main GNU Radio top block with GUI
class power_detector(gr.top_block, Qt.QWidget):

    def __init__(self):
        # Initialize GNU Radio top block and Qt GUI
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Not titled yet")

        # Apply GNU Radio Qt stylesheet
        qtgui.util.check_set_qss()

        # Set application icon (if available)
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)

        # Set up scrollable layout in the GUI window
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        # Load and restore saved window geometry
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "power_detector")
        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        self.flowgraph_started = threading.Event()  # Event flag to signal flowgraph start

        ##################################################
        # Variables
        ##################################################
        self.tune_freq = tune_freq = 100e6  # Set center frequency to 100 MHz

        ##################################################
        # SDR Source Configuration
        ##################################################

        dev = 'driver=rtlsdr'  # Use RTL-SDR driver
        stream_args = 'bufflen=16384'  # SDR buffer size
        tune_args = ['']  # Tuning-specific arguments
        settings = ['']  # Other settings

        # SDR Gain Mode Setter: Enables/disables AGC (Automatic Gain Control)
        def _set_soapy_rtlsdr_source_0_gain_mode(channel, agc):
            self.soapy_rtlsdr_source_0.set_gain_mode(channel, agc)
            if not agc:
                self.soapy_rtlsdr_source_0.set_gain(channel, self._soapy_rtlsdr_source_0_gain_value)
        self.set_soapy_rtlsdr_source_0_gain_mode = _set_soapy_rtlsdr_source_0_gain_mode

        # Manual Gain Setter: Sets gain value if AGC is disabled
        def _set_soapy_rtlsdr_source_0_gain(channel, name, gain):
            self._soapy_rtlsdr_source_0_gain_value = gain
            if not self.soapy_rtlsdr_source_0.get_gain_mode(channel):
                self.soapy_rtlsdr_source_0.set_gain(channel, gain)
        self.set_soapy_rtlsdr_source_0_gain = _set_soapy_rtlsdr_source_0_gain

        # Optional Bias Tee Control (for enabling antenna power)
        def _set_soapy_rtlsdr_source_0_bias(bias):
            if 'biastee' in self._soapy_rtlsdr_source_0_setting_keys:
                self.soapy_rtlsdr_source_0.write_setting('biastee', bias)
        self.set_soapy_rtlsdr_source_0_bias = _set_soapy_rtlsdr_source_0_bias

        # Create SDR source block with SoapySDR interface
        self.soapy_rtlsdr_source_0 = soapy.source(dev, "fc32", 1, '', stream_args, tune_args, settings)
        self._soapy_rtlsdr_source_0_setting_keys = [a.key for a in self.soapy_rtlsdr_source_0.get_setting_info()]

        # Set SDR sample rate, tuning frequency, frequency correction, gain, and bias tee
        self.soapy_rtlsdr_source_0.set_sample_rate(0, 2.4e6)
        self.soapy_rtlsdr_source_0.set_frequency(0, tune_freq)
        self.soapy_rtlsdr_source_0.set_frequency_correction(0, 60)  # PPM correction
        self.set_soapy_rtlsdr_source_0_bias(bool(False))
        self._soapy_rtlsdr_source_0_gain_value = 29.6
        self.set_soapy_rtlsdr_source_0_gain_mode(0, bool(False))
        self.set_soapy_rtlsdr_source_0_gain(0, 'TUNER', 29.6)

        ##################################################
        # Visualization: Frequency Spectrum Plot
        ##################################################

        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            1024,  # FFT size
            window.WIN_BLACKMAN_hARRIS,  # Window function for FFT
            tune_freq,  # Center frequency
            2.4e6,  # Sample rate / Bandwidth
            "FM Spectrum",  # Plot title
            1,  # Number of inputs
            None  # Parent widget
        )

        # Configure plot display options
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis((-140), 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(False)
        self.qtgui_freq_sink_x_0.set_fft_average(0.05)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_0.set_fft_window_normalized(True)

        # Line style configuration for the plot
        for i in range(1):
            self.qtgui_freq_sink_x_0.set_line_label(i, f"Data {i}")
            self.qtgui_freq_sink_x_0.set_line_width(i, 1)
            self.qtgui_freq_sink_x_0.set_line_color(i, "blue")
            self.qtgui_freq_sink_x_0.set_line_alpha(i, 1.0)

        # Wrap the Qt widget and add it to the GUI layout
        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_0_win)

        ##################################################
        # Signal Processing Chain for Power Detection
        ##################################################

        # Low-pass filter to isolate the desired bandwidth
        self.low_pass_filter_0 = filter.fir_filter_ccf(
            10,
            firdes.low_pass(
                1,        # Gain
                2.4e6,    # Sampling rate
                100e3,    # Cutoff frequency
                100e3,    # Transition width
                window.WIN_HAMMING,
                6.76))

        # Convert complex samples to power (magnitude squared)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(1)

        # Apply moving average to smooth the power values
        self.blocks_moving_average_xx_0 = blocks.moving_average_ff(50000, (1/50000), 4000, 1)

        # Probe to access real-time power level (can be polled from Python)
        self.blocks_probe_signal_x_0 = blocks.probe_signal_f()

        ##################################################
        # Connections
        ##################################################

        # Connect blocks to form the full flowgraph
        self.connect((self.soapy_rtlsdr_source_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.blocks_moving_average_xx_0, 0))
        self.connect((self.blocks_moving_average_xx_0, 0), (self.blocks_probe_signal_x_0, 0))

    # Called when the GUI window is closed
    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "power_detector")
        self.settings.setValue("geometry", self.saveGeometry())  # Save window position
        self.stop()  # Stop the flowgraph
        self.wait()  # Wait until all threads are joined
        event.accept()  # Confirm GUI close

    # Getter for current tuning frequency
    def get_tune_freq(self):
        return self.tune_freq

    # Update tuning frequency for both source and spectrum display
    def set_tune_freq(self, tune_freq):
        self.tune_freq = tune_freq
        self.qtgui_freq_sink_x_0.set_frequency_range(self.tune_freq, 2.4e6)
        self.soapy_rtlsdr_source_0.set_frequency(0, self.tune_freq)

# Main application loop
def main(top_block_cls=power_detector, options=None):
    qapp = Qt.QApplication(sys.argv)  # Create Qt application
    tb = top_block_cls()  # Create an instance of the top block
    tb.start()  # Start the GNU Radio flowgraph
    tb.flowgraph_started.set()  # Signal that the flowgraph has started
    tb.show()  # Show the GUI window

    # Define signal handler to gracefully stop the application
    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()
        Qt.QApplication.quit()

    # Connect signal handlers
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    # Qt timer to keep UI responsive (even without user interaction)
    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    # Launch Qt main loop
    qapp.exec_()

# Entry point
if __name__ == '__main__':
    main()