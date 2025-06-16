# /opt/homebrew/bin/python3 scan_stations.py

import time
import numpy as np
from power_detector import power_detector  # Import the GNU Radio flowgraph class
from PyQt5 import Qt  # For QApplication (required by GNU Radio GUI elements)

# Constants for the FM band scan
SCAN_START = 88e6       # Start of FM band in Hz
SCAN_END = 108e6        # End of FM band in Hz
STEP = 200e3            # Frequency step in Hz (200 kHz typical FM channel spacing)
DWELL_TIME = 0.5        # Time in seconds to stay on each frequency before reading power

def scan():
    # Create the Qt application context required by GNU Radio GUI
    app = Qt.QApplication([])

    # Instantiate and start the GNU Radio flowgraph
    tb = power_detector()
    tb.start()
    tb.flowgraph_started.set()
    time.sleep(1)  # Wait to ensure SDR is initialized and stable

    # Create a list of frequencies to scan
    freqs = np.arange(SCAN_START, SCAN_END, STEP)
    results = []

    for freq in freqs:
        tb.set_tune_freq(freq)  # Tune to the current frequency
        time.sleep(DWELL_TIME)  # Wait for signal to stabilize

        power = tb.blocks_probe_signal_x_0.level()  # Get the measured power level
        print(f"{freq/1e6:.1f} MHz: power = {power:.4f}")  # Log result

        results.append((freq, power))  # Store result

    # Stop the flowgraph when done
    tb.stop()
    tb.wait()

    # Sort all frequencies by descending signal power
    results.sort(key=lambda x: x[1], reverse=True)

    # Print the top 5 strongest signals
    print("\nTop stations:")
    for freq, power in results[:5]:
        print(f"{freq/1e6:.1f} MHz - Power: {power:.4f}")

# Run the scan if script is executed directly
if __name__ == "__main__":
    scan()