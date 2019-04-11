# biosemipy 
Python code for BioSemi 24 bit EEG files.

## Installation
git clone https://github.com/igmmgi/DMCpython.git 

cd biosemipy

pip install -e biosemipy

## Methods
read \
write \
merge \
crop \
delete_channels \
select_channels 
channel_difference 

+ dataviewer

## Basic Example 
```python
# bdf file class
from biosemipy import bdf

dat1 = bdf.BDF("filename1.bdf")
dat2 = bdf.BDF("filename2.bdf")

dat1.merge("merged.bdf", dat2)
dat1.write()

# dataviewer class
from biosemipy import dataviewer
dataviewer.run()
dataviewer.run("filename.bdf")

```
