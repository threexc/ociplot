# routesignal
routesignal is a set of tools to plot OpenCellID data on street maps and other
images. The project was originally motivated by interest in comparing
real-world data to random walk models in the context of signal reception and
quality. It relies heavily on the use of freely-available mobile apps and
online services:

1. [Network Cell Info Lite](https://play.google.com/store/apps/details?id=com.wilysis.cellinfolite&hl=en_CA&gl=US)
2. [OpenStreetMap](https://www.openstreetmap.org)
3. [OpenCellID](https://www.opencellid.org)

## Usage

### Requirements

See [requirements.txt](requirements.txt) , or just run `pip install -r requirements.txt`.

You will also need to install the matplotlib PyQt5 backend for your
distribution, e.g. python3-matplotlib-pyqt5 (on Fedora).

At least one measurement set is required for use.

#### The Measurement Set

In order to compile a dataset for use, the following things are required:

1. At least one set of OpenCellID data, such as that exported by the Network
   Cell Info Lite app
2. A map image exported from the OpenStreetMap site, which contains the area of
   interest (if plotting spatial data such as in the example)
3. A map boundary box, defined as min/max lat/long readings, defined in the
   same path as the map file and the data as "bbox.txt". This can be
   obtained on the same page as the export of the map image

Examples can be found in the `data` directory.

### Using gws

Run the following to start the GUI:
`./rsgui`

## Screenshots

### RSRP

![rsrp](media/example_rsrp.png?raw=true "RSRP")

### Path Loss

![path loss](media/example_pathloss.png?raw=true "Path Loss")

### Tower Map

![map](media/example_map.png?raw=true "Map")

## Path Loss Models

Routesignal implements two path loss models provided in [[1]](#1) known
as the Alpha-Beta-Gamma (ABG) and the Close-In (CI) models,
respectively. The free space, two-ray, and Okumura-Hata[[2]](#2) are also
included.

## References

<a id="1">[1]</a> 
S. Sun, T. S. Rappaport, et al.,
*Investigation of Prediction Accuracy, Sensitivity, and
Parameter Stability of Large-Scale Propagation Path
Loss Models for 5G Wireless Communications*,
IEEE TRANSACTIONS ON VEHICULAR TECHNOLOGY, VOL. 65, NO. 5, 2016

<a id="1">[1]</a> 
M. Hata,
*Empirical formula for propagation loss in land mobile radio services*,
IEEE TRANSACTIONS ON VEHICULAR TECHNOLOGY, VOL. 29, NO. 3, 1980

<a id="3">[3]</a>
M2Catalyst, LLC.,
*Network Cell Info: The Ultimate Network Cell Signal Information Tool*,
https://m2catalyst.com/apps/network-cell-info
