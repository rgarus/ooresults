Referenzhandbuch
================

.. only:: html

   .. contents::
      :depth: 2



.. _entries:

Entries
-------


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

   Bahn, die für diese Kategorie verwendet wird. Die Bahn muss zuvor in "Courses" definiert werden.
   Wird der Bahn keine Kategorie zugeordnet, werden keine Ergebnisse berechnet.
   Dies kann dazu verwendet werden, um Ergebnisse einer Wettkampfserie zu importieren.


Type

   Zur Auswahl stehen drei Wettkampfformen:

   - **Standard**:
   
     Die Kontrollstationen müssen in der vorgeschriebenen Reihenfolge angelaufen werden. Es gewinnt der Läufer mit der schnellsten Zeit, der alle Posten in der richtigen Reihenfolge gestempelt hat.

   - **Net**:
   
     Die Kontrollstationen dürfen in belieber Reihenfolge angelaufen werden. Es gewinnt der Läufer mit der schnellsten Zeit, der alle Posten gestempelt hat.

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
   
     Wird eine Startstation verwendet, wird deren Zeit als Startzeit verwendet, ansonsten die in "Entries" angegebene Startzeit des Läufers. Ist dort nichts angegeben, wird die in "Classes" angegebene Massenstartzeit verwendet.

   - **No**:
     
     Auch wenn eine Startstation gestempelt wurde, wird sie nicht als Startzeit verwendet. Es wird immer die in "Entries" angegebene Startzeit des Läufers bzw. wenn dort nichts angegeben ist, die in "Classes" angegebene Massenstartzeit verwendet.

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
 
