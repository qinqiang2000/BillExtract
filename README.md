🚧 Under Active Development 🚧
## Development
Set up the environment using poetry:
```sh
pip install -r requirements.txt      
```
Run the following script to create a database and schema:
```sh
python -m scripts.run_migrations create 
```
run the webapp and open the browser to http://localhost:8000
```sh
python webapp.py
```