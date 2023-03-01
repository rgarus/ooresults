.. image:: https://img.shields.io/pypi/v/ooresults
    :target: https://pypi.org/project/ooresults/

.. image:: https://img.shields.io/pypi/pyversions/ooresults
    :target: https://pypi.org/project/ooresults/

.. image:: https://img.shields.io/pypi/l/ooresults
    :target: https://pypi.org/project/ooresults/

.. image:: https://readthedocs.org/projects/ooresults/badge/?version=latest
    :target: https://ooresults.readthedocs.io/en/latest/?badge=latest


ooresults
---------

ooresults (open orienteering results) is a software to compute the results of orienteering events.
Here, "open" stands for "Open Source" (licensed under AGPL) on the one hand,
and for "Open Architecture" (extendable by plugins) on the other.
ooresults is able to read SPORTident cards.

ooresults uses Python 3.8+ and is licensed under the GNU AFFERO GENERAL PUBLIC LICENSE, version 3.
It consists of two programs:

- **ooresults-server**

   ooresults-server is a web server for managing and storing data. It uses TCP ports 8080 and 8081.

- **ooresults-reader**

   ooresults-reader reads the data of a SI-Card with the help of a connected SPORTident readout station
   and sends the data to the ooresults-server.

The operation takes place by means of a current web browser (Chrome, Firefox, Edge, ...).

ooresults was successfully used to compute the results of the SILVA O-Night 2023 in Munich.


Features
--------

- Multi-user capable
- Reading SPORTident cards
- Installation only necessary on the server and computers with connected SPORTident readout station,
  other computers only need a current web browser
- Supports visiting controls in specific order or in no specific order
- Supports score competitions
- Calculation of a total result of several events possible
- Transfer of competitor lists of an event from OrienteeringOnline.net via OE2003-CSV export
- Import of competitor lists of an event in IOF 3.0 XML format
- Import of course data in IOF 3.0 XML format (e.g. PurplePen)
- Export of results in IOF 3.0 XML format
- Creation of result lists as PDF files


Documentation
-------------

The `documentation <https://ooresults.readthedocs.io/en/latest/>`_ contains installation, a tutorial, a reference guide and configuration
(currently only available in german language).
