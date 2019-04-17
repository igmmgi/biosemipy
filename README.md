# biosemipy 
Python code for BioSemi 24 bit EEG files. A dataviewer written using PyQt5/pyqtgraph
allows visualisation of the *.bdf files. 

## Installation
git clone https://github.com/igmmgi/DMCpython.git 

cd biosemipy

pip install -e biosemipy

## Methods
read \
write \
merge \
crop \
decimate \
delete_channels \
select_channels \
channel_difference 

dataviewer gui

#### Basic Example bdf
```python
# bdf file class
from biosemipy import bdf

dat1 = bdf.BDF("filename1.bdf")
dat2 = bdf.BDF("filename2.bdf")

dat1.merge("merged.bdf", dat2)
dat1.write()
```

#### Basic Example dataviewer from python console
```python
from biosemipy import dataviewer
dataviewer.run()
# or
dataviewer.run("filename.bdf")
```

#### Basic Examples dataviewer from command line
python -m biosemipy.dataviewer
python -m biosemipy.dataviewer filename1.bdf

### Data Viewer GUI
![alt text](/screenshots/dataviewer.png)  
