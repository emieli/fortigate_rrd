# fortigate__rrdtool
Creates RRD graphs for Fortinet Integrated Wi-Fi channel utilization over time.

# Install (Debian)
	sudo apt install python3-venv librrd-dev libpython-dev gcc
	python3 -m venv venv
	source venv/bin/activate
	pip install -r pip-requirements.txt

# Running script to gather RRD data
	screen python3 script.py --ip 1.2.3.4

# Generate graph images
	python3 create_graph.py
