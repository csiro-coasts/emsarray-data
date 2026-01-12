=========================
emsarray example datasets
=========================

This repository contains the example datasets
available through the ``emsarray.tutorial.open_datasets()`` function.

``austen``
==========

A day of the AUSTEn National Tidal model data.
This dataset is defined on an `unstructured grid <https://ugrid-conventions.github.io/ugrid-conventions/>`_,
handled by the ``UGrid`` convention.
Most variables are defined on grid faces.
The dataset is downloaded and subset via the ``scripts/download_austen.py`` script.

Link
    https://doi.org/10.25919/q8dw-c732
Licence
    `CC BY-SA 4.0 <https://creativecommons.org/licenses/by-sa/4.0/>`_
Citation
    Herzfeld, Mike; Griffin, David; Hemer, Mark; Rosebrock, Uwe; Rizwi, Farhan; Trenham, Claire (2020): AusTEN National Tidal model data. v3. CSIRO. Data Collection. https://doi.org/10.25919/q8dw-c732

``bran2020``
============

A small sample of the Bluelink Reanalysis 2020 (BRAN2020) ocean dataset.
This dataset is defined on a rectangular grid with one dimensional coordinates,
handled by the ``CFGrid1D`` convention.
The dataset is downloaded and subset via the ``scripts/download_bran2020.py`` script.

Link
    https://dx.doi.org/10.25914/6009627c7af03
Licence
    `CC BY 4.0 <https://creativecommons.org/licenses/by/4.0/>`_

``kgari``
========

A subset of the Great Barrier Reef 4km (GBR4) v2.0 model,
part of the eReefs data.
This subset is centred around K'gari.
This dataset is defined on a curvilinear grid with two dimensional coordinates,
handled by the ``CFGrid2D`` convention.
Temperature, sea surface height, and current variables are included.
The dataset is downloaded and subset via the ``scripts/download_kgari.py`` script.

Link
    https://research.csiro.au/ereefs/ereefs-data/
Licence
    `CC BY 4.0 <https://creativecommons.org/licenses/by/4.0/>`_

``gbr4``
========

A subset of the Great Barrier Reef 4km (GBR4) v2.0 model,
part of the eReefs data.
This dataset is defined on a curvilinear grid with two dimensional coordinates,
handled by the ``CFGrid2D`` convention.
Temperature, sea surface heigh, and salinity variables are included.
The dataset is downloaded and subset via the ``scripts/download_gbr4.py`` script.

Link
    https://research.csiro.au/ereefs/ereefs-data/
Licence
    `CC BY 4.0 <https://creativecommons.org/licenses/by/4.0/>`_

``vanuatu``
===========

One day of the SCHISM-WWMIII hydrological and wave model hindcast for Vanuatu.
This dataset is defined on an `unstructured grid <https://ugrid-conventions.github.io/ugrid-conventions/>`_,
handled by the ``UGrid`` convention.
Most variables are defined on grid nodes.
The dataset is downloaded and subset via the ``scripts/download_vanutatu.py`` script.

Link
    https://data.csiro.au/collection/65060
Licence
    `CC BY 4.0 <https://creativecommons.org/licenses/by/4.0/>`_
Citation
    Hernaman, Vanessa; Hally, Bryan; Hoeke, Ron; Ortiz-Angulo Cantos, Jared; Perez Diaz, Beatriz; & Trenham, Claire (2024): SCHISM-WWMIII hydrological and wave model hindcast for Vanuatu. v4. CSIRO. Data Collection. https://doi.org/10.25919/gqdd-jc07
