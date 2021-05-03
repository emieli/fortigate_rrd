# fortigate_rrd
Creates RRD graphs for Fortinet Integrated Wi-Fi

# Install (Debian)
	sudo apt install git gcc python3-venv librrd-dev libpython3-dev
	git clone https://github.com/emieli/fortigate_rrd.git
	cd fortigate_rrd/
	python3 -m venv venv
	source venv/bin/activate
	pip install --upgrade pip
	pip install -r pip-requirements.

# Example poller cronjob
	*/5 * * * * root cd /home/script-user/fortigate_rrd && sudo -u script-user venv/bin/python3 poller.py --ip 172.31.255.255

# Generate graph images
	python3 create_graph.py