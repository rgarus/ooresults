Referenzhandbuch
================

.. only:: html

   .. contents::
      :depth: 2


.. _events:

Events
------


Name

   Name des Wettkampfes.


Date

   Datum, an dem der Wettkampf stattfindet, z.B. 2022-03-31.


.. _entries:

Entries
-------

Diese Datensammlung enthält die Teilnehmer eines Wettkampfes.
Ein Teilnehmer wird durch seinen Vor- und Nachnamen eindeutig identifiziert.

Wird ein Teilnehmer bei einem Wettkampf eingetragen und ist noch nicht in der Liste :ref:`competitors` enthalten,
wird er dort automatisch mit seinem Vor- und Nachnamen, seinem Geschlecht und seinem Geburtsjahr ergänzt.

Wird der Vor- oder Nachname eines Teilnehmers korrigiert,
so wird sein Vor- und Nachname auch bei **allen** anderen Wettkämpfen
und in der Datensammlung :ref:`competitors` entsprechend geändert.
Gleiches gilt bei einer Korrektur seines Geschlechts oder seines Geburtsjahres.

.. warning::

   Wird Geschlecht oder Geburtsjahr eines Teilnehmers korrigiert, werden die Ergebnisse **aller** Wettkämpfe,
   an denen der Teilnehmer in einer Kategorie mit Handicap-Wertung teilgenommen hat, neu berechnet.


First name

   Vorname des Teilnehmers.
   

Last name

   Nachname des Teilnehmers.


Gender

   Geschlecht des Teilnehmers (F = weiblich, M = männlich).
   

Year

   Geburtsjahr des Teilnehmers (vierstellig), z.B. 1982 oder 2008.


Chip

   Nummer der SPORTident Card, die der Teilnehmer beim Lauf verwenden will / verwendet hat.
   
   Eine Änderung der Nummer ist nicht möglich, wenn dem Teilnehmer das ausgelesene Ergebnis
   einer Sportident Card zugeordnet ist.


Club

   Verein des Teilnehmers. Um einen Teilnehmer einem Verein zuordnen zu können,
   muss der Verein vorab in die Liste :ref:`clubs` eingetragen werden.


Class

   Kategorie, in der der Teilnehmer startet.


NC (not competing)

   Der Teilnehmer startet ausser Konkurrenz, d.h. er wird in den Ergebnislisten mit seiner Laufzeit
   aufgeführt, das Ergebnis wird aber nicht bei der Berechnung der Platzierungen berücksichtigt.


Start

   Startzeit des Teilnehmers. Wird die Kategorie ohne Stempeln eines Startpostens durchgeführt,
   wird diese Zeit als Startzeit des Teilnehmers verwendet.
   
   Bei einem Massenstart sollte hier keine Zeit eingetragen werden.
   Ist sowohl hier als auch bei der Kategorie eine Startzeit angegeben,
   wird die hier angegebene Zeit als Startzeit des Teilnehmers verwendet.


Status

   Es gibt folgende Zustände:

   - **OK (ok)**:
   
     Der Läufer hat alle Posten (in richtiger Reihenfolge) gestempelt.

   - **MP (mispunched)**:
   
     Der Läufer hat mindestens einen Posten nicht korrekt gestempelt.

   - **DNS (did not started)**:
   
     Der Läufer ist nicht gestartet.

   - **DNF (did not finished)**:
   
     Der Läufer hat den Lauf nicht beendet.
     Mögliche Ursachen:
    
     1. Der Läufer hat den Lauf abgebrochen ohne "Ziel" zu stempeln,
     #. Der Läufer hat "Ziel" gestempelt, aber nicht die letzten drei Kontrollstationen.

   - **OTL (over time limit)**:
   
     Der Läufer hat das Zeitlimit des Wettkampfes überschritten.

   - **DSQ (disqualified)**:
   
     Der Läufer wurde disqualifiziert.


.. _classes:

Classes
-------


Name

   Name der Kategorie, z.B. "Damen A" oder "Herren A".


Short name

   Wird derzeit nicht verwendet.


Course

   Bahn, die für diese Kategorie verwendet wird. Die Bahn muss zuvor in :ref:`Courses` definiert werden.
   Wird der Bahn keine Kategorie zugeordnet, werden keine Ergebnisse berechnet.
   Dies kann dazu verwendet werden, um Ergebnisse einer Wettkampfserie zu importieren.


Type

   Zur Auswahl stehen drei Wettkampfformen:

   - **Standard**:
   
     Die Kontrollstationen müssen in der vorgeschriebenen Reihenfolge angelaufen werden. Es gewinnt der Läufer mit der schnellsten Zeit, der alle Posten in der richtigen Reihenfolge gestempelt hat.

   - **Net**:
   
     Die Kontrollstationen dürfen in beliebiger Reihenfolge angelaufen werden. Es gewinnt der Läufer mit der schnellsten Zeit, der alle Posten gestempelt hat.

   - **Score**:
     
     Score Wettkampf, d.h. pro angelaufener Kontrollstation gibt es einen Punkt. Es gewinnt der Läufer mit der höchsten Punktzahl.


Voided Legs

   Wird bei "Standard" verwendet, um die Laufzeit der Teilstrecke zwischen
   zwei direkt aufeinander folgenden Posten nicht zu berücksichtigen.
   Die beiden Postennummern werden durch einen Bindestrich getrennt.
   Es können mehrere Teilstrecken durch Komma getrennt angegeben werden, z.B. "113-119, 112-114".


Use start control

   Zur Auswahl stehen "If punched", "No" und "Yes".

   - **If punched**:
   
     Wird eine Startstation verwendet, wird deren Zeit als Startzeit verwendet, ansonsten die in :ref:`entries` angegebene Startzeit des Läufers. Ist dort nichts angegeben, wird die in :ref:`classes` angegebene Massenstartzeit verwendet.

   - **No**:
     
     Auch wenn eine Startstation gestempelt wurde, wird sie nicht als Startzeit verwendet. Es wird immer die in :ref:`entries` angegebene Startzeit des Läufers bzw. wenn dort nichts angegeben ist, die in :ref:`classes` angegebene Massenstartzeit verwendet.

   - **Yes**:
   
     Es wird immer die Stempelzeit der Startstation verwendet. Wurde vegessen die Startstation zu stempeln, ist der Lauf fehlerhaft.


Apply handicap

   Bei "Yes" wird die Gesamtzeit (Laufzeit plus eventueller Starfzeiten) mit dem Handicap-Faktor des Läufers multipliziert.
   Der Handicap-Faktor des Läufers ist abhängig von Geschlecht und Alter.


Mass start

   Uhrzeit des Massenstarts, z.B. 18:30:00.


Time limit

   Dient zum Festlegen eines Zeitlimits. Die Eingabe erfolgt in Minuten (z.B "45:00" für 45 Minuten).


Penalty controls

   Für jede fehlende Kontrollstation wird die angegebene Strafzeit (einzugeben in Sekunden) zur Laufzeit addiert.


Penalty time limit

   Für jede angefangene Minute, die die Laufzeit das Zeitlimit überschreitet,
   wird die angegebene Strafzeit (einzugeben in Sekunden) zur Laufzeit addiert.


.. _courses:

Courses
-------


Name

   Name der Bahn, z.B. "Bahn A".


Length

   Länge der Bahn in Metern.


Climb

   Steigung der Bahn in Metern, entlang der erwarteten besten Routenwahl.


Controls

   Nummern der Kontrollstationen (ohne Start- und Zielstation), aus der die Bahn besteht.
   
   Für die Wettkampfform "Standard" sind die Kontrollstationen in der hier angegebenen Reihenfolge anzulaufen.
   Für die Wettkampfformen "Net" und "Score" können die Kontrollstationen in beliebiger Reihenfolge angegeben werden.
   
   Die Kontrollstationen werden durch Bindestrich getrennt eingegeben.   
   Zur besseren Lesbarkeit können vor und nach dem Bindestrich Leerzeichen (Space) eingegeben werden.
   Gültige Eingaben sind z.B. "121-141-122-124" oder "121 - 141 - 122 - 124".


.. _settings:

Settings
--------


Name

   Definiert die beim Drucken verwendete Überschrift.


Nr of best results

   Definiert die Anzahl der Wettkämpfe, die maximal für einen Teilnehmer zur Berechnung des
   Gesamtergebnis verwendet werden sollen. Ist nichts angegeben, werden alle Wettkämpfe
   berücksichtigt.


Mode

   Definiert die Berechnungsmethode. Derzeit ist nur proportional möglich,
   d.h. die Zeit des Siegers wird durch die eigene Zeit geteilt.


Maximum points

   Bei proportional Mode: Der Sieger erhält maximum points, alle anderen
   *MaximumPoints* * *(SiegerZeit / EigeneZeit)*. Nicht gewertete Teilnehmer
   (Status ungleich ok) erhaltenen 0 Punkte.


Decimal places

   Bei proportional Mode: Die berechnete Punktzahl
   *MaximumPoints* * *(SiegerZeit / EigeneZeit)* wird auf die angegebene Anzahl
   von Nachkommastellen gerundet.


.. _competitors:

Competitors
-----------

Diese Datensammlung dient als Archiv aller Wettkämpfer.

Ein Wettkämpfer kann nur dann aus dieser Datensammlung gelöscht werden, wenn er bei keinem
Wettkampf als Teilnehmer eingetragen ist. Ein Wettkämpfer wird durch seinen Vor- und Nachnamen
eindeutig identifiziert, d.h. es kann keine zwei Wettkämpfer mit demselben Vor- und Nachnamen geben.

Wird der Vor- oder Nachname eines Wettkämpfers korrigiert,
so wird sein Vor- und Nachname auch bei **allen** Wettkämpfen entsprechend geändert.
Gleiches gilt bei einer Korrektur seines Geschlechts oder seines Geburtsjahres.

.. warning::

   Wird Geschlecht oder Geburtsjahr eines Wettkämpfers korrigiert, werden die Ergebnisse **aller** Wettkämpfe,
   an denen der Wettkämpfer in einer Kategorie mit Handicap-Wertung teilgenommen hat, neu berechnet.


First name

   Vorname des Wettkämpfers.
   

Last name

   Nachname des Wettkämpfers.


Gender

   Geschlecht des Wettkämpfers (F = weiblich, M = männlich).
   

Year

   Geburtsjahr des Wettkämpfers (vierstellig), z.B. 1982 oder 2008.


Chip

   Nummer der SPORTident Card, die der Wettkämpfer üblicherweise verwendet.


Club

   Verein des Wettkämpfers. Um einen Wettkämpfer einem Verein zuordnen zu können,
   muss der Verein vorab in die Liste :ref:`clubs` eingetragen werden.


.. _clubs:

Clubs
-----


Um einen Teilnehmer oder Wettkämpfer in :ref:`entries` oder :ref:`competitors` einem Verein
zuordnen zu können, muss der Verein vorab in diese Datensammlung eingetragen werden.

Ist ein Teilnehmer eines Wettkampfes oder ein Wettkämpfer einem Verein zugeordnet,
kann dieser Verein nicht gelöscht werden.


Name

   Name des Vereins.
