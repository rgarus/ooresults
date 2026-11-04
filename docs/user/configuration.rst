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
   import_stream = off

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
   eine Seite aufgerufen werden, mit der das Auslesen einer SiCard simuliert werden kann,
   siehe Abschnitt :ref:`demo_cardreader`.

   .. note::

      Aus Sicherheitsgründen sollte demo_reader nur zum Kennenlernen der Software auf "on"
      und sonst auf "off" gesetzt werden.


[Server]import_stream

   Ist der Eintrag import_stream "on", können unter der Adresse "wss://<server>:8081/import"
   IOF Interface Standard 3.0 ResultList Daten empfangen werden. Dies ist z.B. dann notwendig,
   wenn der ooresults-server zum Veröffentlichen von Live-Egebnissen verwendet werden soll,
   siehe Abschnitt :ref:`ooresults_live_server`.

   .. note::

      Aus Sicherheitsgründen sollte import_stream nur auf "on" gesetzt werden,
      wenn Ergebnisdaten über das Streaming Interface empfangen werden sollen.


.. index:: ooresults-server; Upload

[Upload]url, [Upload]token und [Upload]name

   Der optionale Abschnitt [Upload] ermöglicht es, die Ergebnisse eines Wettkampfes
   mit einem Klick an einen anderen Server zu senden, z.B. an die Webseite einer Laufserie:

   .. code-block::

      [Upload]
      url = https://www.old-oc-muenchen.de/cup_import.php
      token = <geheimer Schlüssel>
      name = Munich O-Cup

   Ist url gesetzt, erscheint im Tab Entries der Button "Upload to <name> ...".
   Er sendet die Ergebnisse des ausgewählten Wettkampfes als
   IOF Interface Standard 3.0 ResultList (wie Export "IOF Interface Standard 3.0 Result List")
   per HTTP POST an url. Der token wird im Header "X-Upload-Token" mitgesendet.
   Fehlt name, wird der Rechnername aus url angezeigt.

   Der empfangende Server antwortet mit einem JSON-Objekt, z.B.
   ``{"ok": true, "message": "52 Ergebnisse empfangen", "review_url": "https://..."}``.
   message wird angezeigt, review_url (optional) als Link zur Prüfung der Daten.

   .. note::

      url muss mit https:// beginnen, damit der token nicht unverschlüsselt übertragen wird
      (Ausnahme: localhost). Weiterleitungen (z.B. von http:// auf https://) werden nicht verfolgt.


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
