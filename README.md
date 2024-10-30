# flybrain-clustering
Clustering analysis of the *oviIN* connectome. Based on the *Drosophila melanogaster* connectome clustering analysis done [here.](https://www.biorxiv.org/content/10.1101/2022.11.23.517722v1)

The notebooks are used to do large dataset analysis and includes the cluster identities determined by maximizing [generalized modularity density](https://github.com/prameshsingh/generalized-modularity-density).


# Set up

## Packages
You will need the following python packages:
* [`neuprint`](https://github.com/connectome-neuprint/neuprint-python)
* [`ipyvolume`](https://ipyvolume.readthedocs.io/en/latest/install.html)
* [`bokeh`](https://docs.bokeh.org/en/2.4.3/docs/first_steps.html)
* [`colorcet`](https://colorcet.holoviz.org/)


## Neuprint Auth token
In order to use these notebooks, you will need an authorization token to access NeuPrint.

1. Go to [neuprint.janelia.org](https://neuprint.janelia.org/)
2. Log in with your Google account.
3. Go to your account (menu in the top right of the screen)
4. Copy the auth token to a plain text file in the same directory as the notebooks and name it `flybrain.auth`

# Folder Information
- The APL folder contains the data used to create the figures in APL/Figures-APL
- The oviIN folder contains the data used to create the figures in Figures-oviIN
- The joint-marginal plots were created in the files called joint_marginals_***.ipynb for the oviIN and APL substituted for the *** respectively
  - [`oviIN`](https://github.com/RhessaWL/flybrain-clustering/blob/main/joint_marginals_graph.ipynb)
  - [`APL`](https://github.com/RhessaWL/flybrain-clustering/blob/main/joint_marginals_APL.ipynb)
