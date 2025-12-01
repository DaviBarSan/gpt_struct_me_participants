python -m pip install virtualenv
virtualenv venv --python=python3.9
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
pip install -e .