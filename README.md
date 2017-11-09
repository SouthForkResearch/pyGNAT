# pyGNAT

South Fork Research, Inc. (SFR) is redesigning the network topology component of **Geomorphic Network Analysit 
Toolbox** in an effort to optimize processing times and improved functionality. GNAT now uses the excellent [NetworkX](
https://networkx.github.io/documentation/networkx-1.11/) Python library to identify disconnected stream reaches 
and subnetworks, identify edge and node types, and calculate river kilometers.

Originally, this new functionality was indtended to serve as the foundation of a completely new version of GNAT, redesigned as a QGIS
plugin. However, due to constraints in time and resources, we will be incorporating the new functionality into the existing [GNAT 
ArcGIS Python toolbox](https://github.com/Riverscapes/arcGNAT).