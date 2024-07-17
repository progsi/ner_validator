# NER Validator
A small tool to validate NER annotations in inside-outside-beginning (IOB) format.
## Getting Started (with SSH Tunnel)
Install environment
`conda env create -f env.yml`
Run streamlit app on the server with `FILE.IOB` being your IOB file. 
`streamlit run app.py --server.port 8501 -- --file FILE.IOB`
On your machine with your connection to `USER@SERVER`:
`ssh -L 8501:localhost:8501 USER@SERVER`
Open on your machine in the browser:
`http://localhost:8501`
