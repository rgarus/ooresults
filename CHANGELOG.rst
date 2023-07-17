Changelog
=========


[0.2.6] - 2023-07-17
--------------------

Added
^^^^^

- Control cards can be marked as rental cards in the table data of the "Entries" and "SI reader" tabs.


[0.2.5] - 2023-06-05 
--------------------

Changed
^^^^^^^

- Printing of results and split times improved (e.g. course data added).


[0.2.4] - 2023-05-07
--------------------

Fixed
^^^^^

- Changing a chip number or setting the status DNS is no longer possible if the entry is assigned a readout result of a SPORTident card.
- The readout result of a SPORTident card should only automatically assigned to an entry if no other result is available for this card.


[0.2.3] - 2023-04-23
--------------------

Changed
^^^^^^^

- Course data, Position and TimeBehind added to IOF ResultList export.
- Documentation improved.


[0.2.2] - 2023-04-07
--------------------

Added
^^^^^

- Import and export of OE12 csv files added.

Changed
^^^^^^^

- Importing club names from orienteeringonline.net via OE2003 csv files improved.

Fixed
^^^^^

- Fixed error in formatting negative time differences.
- Reload button of Results tab not working.


[0.2.1] - 2023-03-23
--------------------

Added
^^^^^

- Missing controls are shown in an additional column in the list of read SI cards in the 'SI reader' window.

Fixed
^^^^^

- Websocket does not reconnect in demo_reader.


[0.2.0] - 2023-03-01
--------------------

Added
^^^^^

- Initial public release.
