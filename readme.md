Portfolio construction in the context of financial index management

To get started:
1. Setup a conda environment using at least python=3.11  
   Access a Windows Subsystem for Linux (WSL) terminal and run  
   `conda create --name env-index-mgt python=3.11`  
   If an environment is already setup, activate it:  
   `conda activate env-index-mgt`  

2. Clone the repo and prepare for execution  
   `git clone https://github.com/ljon3/index-management.git`    
   `cd index-management`  
   `pip install -r requirements.txt`

3. To launch VSCode with the correct PYTHONPATH:  
   `source ./_startup.sh`

Workflows included in this repo:  

* Workflow 1: Portfolio construction  
  In this piece i demonstrate the different modules that are put together to manage an index construction workflow robustly. The files of interest are:  
  `driver-strategy.ipynb`  
  `driver-market.ipynb`  
  `driver-universe.ipynb`  
  `driver-valuation.ipynb`  

  I have setup driver-strategy.ipynb as a deployable app using streamlit library (https://streamlit.io/). This can be accessed by running from WSL terminal:  
  `streamlit run app_portfolio_visualize.py`  
  access the app by navigating to the address:  
  `http://localhost:8501`  
  Verify this is the port displayed when you run the   
  `streamlit run app_portfolio_visualize.py` 

* Workflow 2: Unit Testing  
  An integral part of development workflows is testing. I have setup tests in the respective folders. To run the tests, execute:  
  `pytest`

* Workflow 3: Automation Workflows for CI/CD  
  Finally, to initiate automatically daily valuation workflows, I have setup Github Actions to run automatically. As of now, I have set it up to run on Fridays. This is configured in the file:  
  `.github/workflows/valuation.yml`   
  This can be visualized at: https://github.com/ljon3/index-management/actions
