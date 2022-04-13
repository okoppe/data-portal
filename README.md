# data-portal
This repository holds code for a data portal that automatically servers Jupyter Notebook data visualizations generated with the Bokeh package to the web. 
It automatically updates the visualizations on the web as files are added and deleted from a GitHub repo holding the Notebooks it servers to the web.

Must set the following environment variables: GIT_REPO_LINK, REPO_LOCAL_DIR, PORT_START

Setting up the data portal to run on a Ubuntu server:

```
git clone https://github.com/okoppe/data-portal.git
git clone LINK TO YOUR REPOSITORY WITH JUYPTER NOTEBOOKS

cd data-portal

sudo apt-get update -y
sudo apt-get install -y python3-pip
```

Set up a virtual enviroment:

```
cd flask_app

sudo apt-get update -y
sudo apt-get install -y python3-venv
python3 -m venv venv
```
activate the virtual enviroment:

```
source venv/bin/activate
```

Install the requirments:

```
python3 -m pip install -r requirements.txt
```

Start the Flask server and local host:

```
# NOTE to access from outside localhost (NOTE: dangerous!) replace the line 
# app.run(debug=True)
# with the line
# app.run(host="0.0.0.0", port=int(os.environ['PORT_START']), debug=True)

python3 app.py
```

You may be prometed to enter your sudo password.

6. Navigate to the url for your local host (should be outputed in the terminal)
