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
`./wsgui`

## Screenshots

### Path Loss

![path loss](media/example_pathloss.png?raw=true "Path Loss")

### Tower Map

![tower map](media/example_towermap.png?raw=true "Tower Map")

### Bitrate Plot

![bitrate](media/example_bitrate.png?raw=true "Bitrate")

## Path Loss Models

The two path loss models provided originate in [[1]](#1) and are known
as the Alpha-Beta-Gamma (ABG) and the Close-In (CI) models,
respectively. They have the following expressions:

**ABG:**

`10 * alpha * np.log10(dist/ref_dist) + beta + 10 * gamma * np.log10(freq/ref_freq) + np.random.normal(0, sigma)`

**CI:**

`pl_fs(ref_dist, freq) + 10 * pl_exp * np.log10(dist/ref_dist) + np.random.normal(0, sigma)`

Where: 

- **alpha** is the distance-dependency coefficient
- **beta** is an offset value in dB
- **gamma** is the frequency-dependency coefficient
- **sigma** is the standard deviation for a zero-mean Gaussian random
  variable in dB
- **pl_exp** is the path loss exponent
- **dist** is the measurement distance
- **ref_dist** is the free space reference distance
- **freq** is the carrier frequency
- **ref_freq** is the reference frequency

It is important to note that while the alpha parameter has some physical
basis in the ABG model, the **beta** and **gamma** parameters are primarily for
curve-fitting[[1]](#1)(p. 2847) and do not have obvious physical
origins. Also stated there are the conditions for equivalence between
the ABG and CI models:

- Equate the **alpha** and **pl_exp** values
- Set **gamma** to 2 (the free space **pl_exp** value)
- Set **beta** to `20 * np.log10((4 * np.pi * 10^9)/c)`, where **c** is
  the speed of light

## Challenges

- Accurate tower positioning info is still difficult to obtain - the
  Network Cell Info Lite app shows a tower icon at the location of the
  cell, not the tower itself[[3]](#3)
    - Means that there is outstanding effort remaining to collect full
      data set for analysis (i.e. find, photograph, and get approximate
      GPS position of each tower projecting to a cell)
- Data collection is somewhat erratic and inconsistent, as the same
  campaign route can provide significantly different results on
  subsequent runs
- Still an outstanding issue with accurate positioning in "street
  canyons" and even in low-density non-line-of-sight (NLOS) areas,
  leading to inaccurate positioning readings. This can be corrected with
  the addition of a windowing algorithm that "smoothes" the data via
  dead-reckoning
    - Existing datasets for more urban areas are still useful, but
      require more repeated measurement campaigns in the same locations
      to have sufficient numbers of data points for this to work
- Need to expand and compare this with other devices - a 5G-capable
  mobile device would be a valuable addition, but the Network Cell Info
  app does not clearly state support for 5G yet
- Measurements thus far do not adequately compare to the stochastic
  nature of the PL and RWM models. In [[1]](#1)(p. 2847), it is stated
  that their experiments used 30 data sets to compare with the models,
  so more campaigns should be undertaken in the previously-visited areas
  to ensure level comparisons

## References

<a id="1">[1]</a> 
S. Sun, T. S. Rappaport, et al.,
*Investigation of Prediction Accuracy, Sensitivity, and
Parameter Stability of Large-Scale Propagation Path
Loss Models for 5G Wireless Communications*,
IEEE TRANSACTIONS ON VEHICULAR TECHNOLOGY, VOL. 65, NO. 5, MAY 2016

<a id="2">[3]</a>
M2Catalyst, LLC.,
*Network Cell Info: The Ultimate Network Cell Signal Information Tool*,
https://m2catalyst.com/apps/network-cell-info
