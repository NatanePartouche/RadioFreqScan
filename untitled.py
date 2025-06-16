#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-3.0
# GNU Radio version: 3.10.12.0
# Title: Not titled yet (WFM Receiver)

# Required imports
from PyQt5 import Qt, QtCore  # Qt for GUI
from gnuradio import qtgui  # GNU Radio GUI widgets
from gnuradio import analog  # Analog signal processing blocks
from gnuradio import audio  # Audio output blocks
from gnuradio import filter  # Signal filtering blocks
from gnuradio.filter import firdes  # FIR filter design
from gnuradio import gr  # Core GNU Radio class
from gnuradio.fft import window  # Windowing functions for FFT
import sys  # System operations
import signal  # Signal handling
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation  # Engineering notation utils
from gnuradio import soapy  # Interface with SoapySDR-compatible SDRs
import sip  # For wrapping Qt widgets
import threading  # Threading tools

# Main GNU Radio top block with Qt GUI
class untitled(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Not titled yet")
        qtgui.util.check_set_qss()  # Apply Qt styling

        # Set window icon (optional)
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)

        # GUI layout setup
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

        # Save/restore GUI layout
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "untitled")
        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.tune_freq = tune_freq = 100.1e6  # Initial tuned frequency
        self.samp_rate = samp_rate = 2048000  # Sample rate for SDR

        ##################################################
        # Widgets
        ##################################################
        # Frequency slider (88 MHz to 108 MHz FM band)
        self._tune_freq_range = qtgui.Range(88e6, 108e6, 100e3, 100.1e6, 200)
        self._tune_freq_win = qtgui.RangeWidget(
            self._tune_freq_range, self.set_tune_freq,
            "Tuning Frequency", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._tune_freq_win)

        ##################################################
        # SDR Source Setup (RTL-SDR via Soapy)
        ##################################################
        self.soapy_rtlsdr_source_0 = None
        dev = 'driver=rtlsdr'
        stream_args = 'bufflen=16384'
        tune_args = ['']
        settings = ['']

        # Gain control helpers
        def _set_soapy_rtlsdr_source_0_gain_mode(channel, agc):
            self.soapy_rtlsdr_source_0.set_gain_mode(channel, agc)
            if not agc:
                self.soapy_rtlsdr_source_0.set_gain(channel, self._soapy_rtlsdr_source_0_gain_value)
        self.set_soapy_rtlsdr_source_0_gain_mode = _set_soapy_rtlsdr_source_0_gain_mode

        def _set_soapy_rtlsdr_source_0_gain(channel, name, gain):
            self._soapy_rtlsdr_source_0_gain_value = gain
            if not self.soapy_rtlsdr_source_0.get_gain_mode(channel):
                self.soapy_rtlsdr_source_0.set_gain(channel, gain)
        self.set_soapy_rtlsdr_source_0_gain = _set_soapy_rtlsdr_source_0_gain

        def _set_soapy_rtlsdr_source_0_bias(bias):
            if 'biastee' in self._soapy_rtlsdr_source_0_setting_keys:
                self.soapy_rtlsdr_source_0.write_setting('biastee', bias)
        self.set_soapy_rtlsdr_source_0_bias = _set_soapy_rtlsdr_source_0_bias

        # Initialize SDR source
        self.soapy_rtlsdr_source_0 = soapy.source(dev, "fc32", 1, '', stream_args, tune_args, settings)
        self._soapy_rtlsdr_source_0_setting_keys = [a.key for a in self.soapy_rtlsdr_source_0.get_setting_info()]
        self.soapy_rtlsdr_source_0.set_sample_rate(0, 2.4e6)
        self.soapy_rtlsdr_source_0.set_frequency(0, tune_freq)
        self.soapy_rtlsdr_source_0.set_frequency_correction(0, 60)  # PPM correction
        self.set_soapy_rtlsdr_source_0_bias(False)
        self._soapy_rtlsdr_source_0_gain_value = 29.6
        self.set_soapy_rtlsdr_source_0_gain_mode(0, False)
        self.set_soapy_rtlsdr_source_0_gain(0, 'TUNER', 29.6)

        ##################################################
        # Frequency Spectrum Display (FFT)
        ##################################################
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            1024, window.WIN_BLACKMAN_hARRIS, tune_freq,
            2.4e6, "FM Spectrum", 1, None)
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis(-140, 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(False)
        self.qtgui_freq_sink_x_0.set_fft_average(0.05)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_0.set_fft_window_normalized(True)

        # Configure visual line display
        self.qtgui_freq_sink_x_0.set_line_label(0, "Data 0")
        self.qtgui_freq_sink_x_0.set_line_width(0, 1)
        self.qtgui_freq_sink_x_0.set_line_color(0, "blue")
        self.qtgui_freq_sink_x_0.set_line_alpha(0, 1.0)

        # Add FFT display to GUI layout
        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_0_win)

        ##################################################
        # Signal Processing Chain
        ##################################################

        # Low-pass filter to isolate FM signal from SDR input
        self.low_pass_filter_0 = filter.fir_filter_ccf(
            10, firdes.low_pass(
                1, 2.4e6, 100e3, 50e3, window.WIN_HAMMING, 6.76))

        # WFM demodulator (wideband FM to audio)
        self.analog_wfm_rcv_0 = analog.wfm_rcv(
            quad_rate=240e3,
            audio_decimation=5,
        )

        # Audio output to default sound device
        self.audio_sink_0 = audio.sink(48000, '', True)

        ##################################################
        # Connections: Build the Flowgraph
        ##################################################
        self.connect((self.soapy_rtlsdr_source_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.analog_wfm_rcv_0, 0))
        self.connect((self.analog_wfm_rcv_0, 0), (self.audio_sink_0, 0))

    # Save GUI window state on close
    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "untitled")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()
        event.accept()

    # Frequency getter/setter
    def get_tune_freq(self):
        return self.tune_freq

    def set_tune_freq(self, tune_freq):
        self.tune_freq = tune_freq
        self.qtgui_freq_sink_x_0.set_frequency_range(self.tune_freq, 2.4e6)
        self.soapy_rtlsdr_source_0.set_frequency(0, self.tune_freq)

    # Sample rate getter/setter (not connected to anything here)
    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate


# Main application launcher
def main(top_block_cls=untitled, options=None):
    qapp = Qt.QApplication(sys.argv)  # Qt application setup
    tb = top_block_cls()  # Create flowgraph
    tb.start()  # Start SDR processing
    tb.flowgraph_started.set()
    tb.show()  # Show GUI

    # Signal handlers for clean exit
    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    # Dummy timer for Qt responsiveness
    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()  # Enter Qt event loop

# Launch main if run as script
if __name__ == '__main__':
    main()