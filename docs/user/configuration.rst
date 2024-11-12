Konfiguration und Benutzerverwaltung
====================================

.. only:: html

   .. contents::
      :depth: 2


.. _configuration:

Konfiguration
-------------

Die Konfiguration von ooresults erfolgt über die Datei config.ini.
Sie wird im Unterverzeichnis .ooresults des Heimverzeichnisses des Benutzers gesucht.
Existiert keine solche Datei wird sie mit folgendem Inhalt angelegt:

.. code-block::

   [Server]
   ssl_cert =
   ssl_key =
   demo_reader = off

   [Cardreader]
   host = 127.0.0.1
   ssl_verify = false
   serial_number =
   key = local


Der ooresults-server verwendet den Abschnitt [Server],
der ooresults-reader den Abschnitt [Cardreader].

Es bedeuten:

.. index:: ooresults-server; Konfiguration

[Server]ssl_cert und [Server]ssl_key

   Die Einträge ssl_cert und ssl_key verweisen auf die für den https-Server
   benötigten Zertifikate. Fehlen die Einträge oder sind sie leer,
   werden die Files cert.pem und privkey.pem aus dem Unterverzeichnis
   .ooresults/cert des Heimverzeichnisses des Benutzers verwendet,
   existieren sie nicht werden selbst-zertifizierte Files erstellt.


[Server]demo_reader

   Ist der Eintrag demo_reader on, kann unter der Adresse https://localhost:8080/demo
   ein Seite aufgerufen werden, mit der das Auslesen einer SiCards simuliert werden kann,
   siehe Abschnitt :ref:`demo_cardreader`.

   .. note::

      Aus Sicherheitsgründen sollte demo_reader nur zum Kennenlernen der Software auf "on"
      und sonst auf "off" gesetzt werden.


.. index:: ooresults-reader; Konfiguration

[Cardreader]host

   Ip-Adresse oder Name, unter der der ooresults-server erreichbar ist.

   .. note::

      Auf Windows-Rechnern sollte anstelle von localhost immer 127.0.0.1 verwendet werden,
      da Windows das IPv6 Protokoll priorisiert und der oo-result-server dann unter Umständen nicht
      erreichbar ist.


[Cardreader]ssl_verify

   Bei false wird keine Verifizierung des ooresults-server durchgeführt.
   Sollte bei selbsterstellten Zertifikaten auf false gesetzt werden, andernfalls auf true.


[Cardreader]serial_number

   Sind mehrere Auslesestationen an einen Rechner angeschlossen, kann durch Angabe der Seriennummer
   der SPORTident Auslesestation die zu verwendende ausgewählt werden.
   Die Seriennummer befindet sich auf der Rückseite der SPORTident Auslesestation.

   Bei nur einer angeschlossenen Auslestation sollte der Eintrag leer bleiben.


[Cardreader]key

   Schlüssel, um den ooresults-reader einem Wettkampf zuzuordnen.

   .. warning::

      Der Schlüssel dient gleichzeitig auch zum Berechtigungsnachweis. Jeder der den Schlüssel kennt, kann Daten
      auf dem ooresults-server im zugeordneten Wettkampf speichern.


.. _user_management:

Benutzerverwaltung
------------------

Die Benutzerverwaltung zum Anmelden an ooresults erfolgt über die Datei users.json.
Sie wird im Unterverzeichnis .ooresults des Heimverzeichnisses des Benutzers gesucht
und enthält die Benutzernamen und Passwörter.

Existiert keine solche Datei wird sie mit folgendem Inhalt angelegt:

.. code-block::

   [
       {
           "username": "admin",
           "password": "admin"
       }
   ]

.. warning::

   Aus Sicherheitsgründen wird empfohlen, das Passwort zu ändern.

Änderungen von Benutzernamen und Passwörtern, Anlegen neuer Benutzer oder Löschen
von Benutzern erfolgt direkt durch Editieren der Datei.
Z.B. enthält die folgende Datei die drei Benutzernamen Scholz, Habeck und Lindner:

.. code-block::

   [
       {
           "username": "Scholz",
           "password": "Ka_1_lbsbraten"
       },
       {
           "username": "Habeck",
           "password": "Sc_2_hweinebraten"
       },
       {
           "username": "Lindner",
           "password": "Hirsch$Gulasch"
       }
   ]

.. note::

   Änderungen an users.json werden erst nach einem Neustart des ooresults-server wirksam.

.. warning::

   Der ooresults-server kann nur mit einer vorhandenen und inhaltlich
   korrekten users.json gestartet werden. Sie wird gegen folgendes JSON-Schema geprüft:

   .. code-block::

      {
          'type': 'array',
          'items': {
              'type': 'object',
              'properties': {
                  'username': {'type': 'string'},
                  'password': {'type': 'string'},
              },        
              'required': ['username', 'password'],
              'additionalProperties': False,
          }
      }
