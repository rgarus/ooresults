Changelog
=========


[Unreleased]
------------

Changed
^^^^^^^

- Marking changed elements of 'Add' or 'Edit' windows improved.


[0.3.0] - 2024-07-26
--------------------

Added
^^^^^

- Added export of an IOF XML ResultList based on runtimes for import into Splitsbrowser software when time credits cause problems.

Changed
^^^^^^^

- Database schema updated to version 12.


[0.2.11] - 2024-07-10
---------------------

Added
^^^^^

- Status "Started" added.

Changed
^^^^^^^

- Database schema updated to version 11.
- Times of an IOF ResultList are imported both as punch times and as si punch times.

Fixed
^^^^^

- Status value entered in "Add entry ..." or "Edit entry ..." was no longer used.


[0.2.10] - 2024-05-24
---------------------

Added
^^^^^

- Result data (start time, finish time and split times) can be edited.

Changed
^^^^^^^

- Database schema updated to version 9.
- Unnecessary additional punches in split time printouts removed.


[0.2.9] - 2024-02-13
--------------------

Fixed
^^^^^

- Python TypeError exception when using Python 3.11 fixed, if a /si1 or /si2 pages is opened in a webbrowser.
- Python TypeError exception when using Python 3.8 or 3.9 fixed when printing results or split times.
- Course data (climb) not correctly included in the result and split time printouts.


[0.2.8] - 2024-01-05
--------------------

Fixed
^^^^^

- ooresults.server startup error when using Python 3.11 fixed.


[0.2.7] - 2024-01-04
--------------------

Changed
^^^^^^^

- Internally used data structures and interfaces changed.
- Course names added to IOF ResultList export.

Fixed
^^^^^

- Display error message if the server cannot be reached when executing a function.
- Start times of an IOF ResultList of not started participants are no longer imported as punched times.


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
