import time

import pyvisa


RESOURCE = "GPIB0::6::INSTR"
INTERVAL_SECONDS = 1.0


rm = pyvisa.ResourceManager("@ivi")  # force NI/IVI VISA
print("VISA resources:", rm.list_resources())

dmm = rm.open_resource(RESOURCE)
dmm.timeout = 5000

MAX_RETRIES = 3

try:
	print(dmm.query("*IDN?").strip())
	dmm.write("CONF:VOLT:DC")

	while True:
		for attempt in range(MAX_RETRIES):
			try:
				voltage = dmm.query("READ?").strip()
				print(f"DC voltage: {voltage} V")
				break
			except pyvisa.errors.VisaIOError as e:
				print(f"  [retry {attempt + 1}/{MAX_RETRIES}] VISA error: {e}")
				dmm.clear()       # flush instrument buffers
				time.sleep(0.5)
		time.sleep(INTERVAL_SECONDS)
except KeyboardInterrupt:
	print("Stopped.")
finally:
	dmm.close()