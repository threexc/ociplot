# walksignal
walksignal is a set of tools to plot OpenCellID data on street maps and other
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

At least one measurement set and one reference set are required for use.

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

#### The Reference Data Set

A reference set is required to be set for analysis of the measurement
set. An example is provided in `data/oci_ref`

If a tower in the measurement set is not in the reference set, the Path
Loss plot will not display the measurement data until a tower position
is manually set. Doing this will draw the tower in the specified
location on the tower plot.

### Using gws

Run the following to start the GUI:
`./gws`

## Screenshots

### Path Loss

![path loss](example_pathloss.png?raw=true "Path Loss")

### Tower Map

![tower map](example_towermap.png?raw=true "Tower Map")

### Random Walk Model Plot

![random_walk](example_rwm.png?raw=true "Random Walk Model")
