# fortigate__rrdtool
Creates RRD graphs for Fortinet Integrated Wi-Fi channel utilization over time.

# Install (Debian)
	sudo apt install git gcc python3-venv librrd-dev libpython3-dev
	git clone https://github.com/emieli/fortigate_rrd.git
	cd fortigate_rrd/
	python3 -m venv venv
	source venv/bin/activate
	pip install --upgrade pip
	pip install -r pip-requirements.txt

# Running script to gather RRD data
	screen python3 script.py --ip 1.2.3.4

# Generate graph images
	python3 create_graph.py
