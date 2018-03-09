# PubMedMetrics

This is a program that can query from [PubMed](https://www.ncbi.nlm.nih.gov/pubmed/), store the results to database for later ranking. It uses [Altmetric](https://www.altmetric.com/) to rank them. 

# Installation (Ubuntu)

```bash
sudo apt update
sudo apt install python python-dev
wget https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py
pip install --upgrade virtualenv
virtualenv pmm
source pmm/bin/activate
pip install .
```

# Run

```
usage: main.py [-h] [-c CONFIG] [-o OUTPUT] [-d DAYS]

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Configuration for querying
  -o OUTPUT, --output OUTPUT
                        Output file name of the fetched papers
  -d DAYS, --days DAYS  Number of days of looking back
```

# Credits

- Denis Odinokov
- Wenwei Huang

# License

MIT License
