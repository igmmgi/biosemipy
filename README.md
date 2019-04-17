# biosemipy 
Python code for BioSemi 24 bit EEG files. A dataviewer written in PyQt5/pyqtgraph
allows visualisation of the datafiles. 

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

### Basic Example bdf
```python
# bdf file class
from biosemipy import bdf

dat1 = bdf.BDF("filename1.bdf")
dat2 = bdf.BDF("filename2.bdf")

dat1.merge("merged.bdf", dat2)
dat1.write()

```
### Basic Example dataviewer from python console
```python
from biosemipy import dataviewer
dataviewer.run()
# or
dataviewer.run("filename.bdf")

```
### Basic Example dataviewer from command line
python -m biosemipy.dataviewer
