# NER Validator
A small tool to validate NER annotations in inside-outside-beginning (IOB) format.
## Getting Started (with SSH Tunnel)
### 1. Install environment
`conda env create -f env.yml`
### 2. Run streamlit app on the server with `FILE.IOB` being your IOB file. 
`streamlit run app.py --server.port 8501 -- --file FILE.IOB`
### 3. On your machine with your connection to `USER@SERVER`:
`ssh -L 8501:localhost:8501 USER@SERVER`
### 4. Open on your machine in the browser:
`http://localhost:8501`
