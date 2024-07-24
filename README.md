# NER Validator
A small tool to validate NER annotations in inside-outside-beginning (IOB) format.
## Connecting with SSH Tunnel
### Requirements
- a user on a server which is reachable via SSH
- Python, Conda etc. on the respective server
### Steps
1. Run `run_server.sh` on the server
2. Run `run_local.sh YOUR_USER@YOUR_SERVER` on your machine replacing `YOUR_USER` and `YOUR_SERVER` accordingly
## Data Preparation
- an IOB file into `data/input`
- optionally: a .metadata file (csv file with tab separators) for showing metadata per item (eg. true entity names)
