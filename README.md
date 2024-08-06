# NER Validator
A small tool to validate NER annotations in inside-outside-beginning (IOB) format.
## Getting Started
### Requirements
- local Linux distribution (tested on Ubuntu), WSL etc.
- Python, Conda etc. on the respective server
- a user on a server which is reachable via SSH
### Usage
1. Run `run_app.sh` on the server
2. Run `run_tunne.sh YOUR_USER@YOUR_SERVER` on your machine replacing `YOUR_USER` and `YOUR_SERVER` accordingly
### Alternative: Run Locally
Simply run `run_app.sh`.
## Data Preparation
- an IOB file into `data/input`
- optionally: a .metadata file (csv file with tab separators) for showing metadata per item (eg. true entity names)
