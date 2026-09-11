.. raw:: latex

    \clearpage


.. _ooresults_live_server:

Veröffentlichung von Ergebnissen über einen ooresults-Live-Server
-----------------------------------------------------------------


Konzept
^^^^^^^

Ein ooresults-server kann als Live-Server verwendet werden. Seine Wettkampfdaten werden
dann von einer externen Quelle (z.B. einem anderen ooresults-server) regelmässig aktualisiert.
Die externe Quelle sendet die Daten als "IOF 3.0 Interface Standard ResultList".


.. warning::

   Es ist auch möglich, die Ergebnisse eines Wettkampfes direkt über den ooresults-server,
   der für die Verwaltung eines Wettkampfes verwendet wird, zu veröffentlichen.
   Dies kann für ein lokales WLAN ausreichend sein. Für eine Veröffentlichung im Internet sollte aus
   Stabilitäts- und Sicherheitsgründen ein zweiter ooresults-server verwendet werden.

   
.. _configuration_live_server:

Konfiguration des ooresults-Live-Server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1.  In der Konfiguration ist der Parameter "import_stream" auf "on" zu setzen, siehe auch :ref:`configuration`.

#.  Es ist ein Wettkampf anzulegen, dessen Ergebnisse veröffentlicht und vom ooresults-Wettkampf-Server aktualisiert werden.
    Für diesen Wettkampf sind folgende Parameter zu setzen:

    - Publish

      Um die Ergebnisdaten des Wettkampfes zu veröffentlichen,
      ist der Parameter "Publish" dieses Wettkampfes auf true zu setzen.
      
    - Key

      Definition eines Schlüssels. Der Schlüssel ist beim Aufbau der Verbindung zum ooresults-server anzugeben,
      um den Wettkampf zu definieren, für den die empfangenen Daten bestimmt sind.


.. _configuration_events_server:

Konfiguration des ooresults-Wettkampf-Server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1.  Auf dem ooresults-Server, von dem Daten eines Wettkampfes zum ooresults-Live-Server gesendet werden sollen,
    sind folgende Parameter zu setzen:

    - Streaming address

      Adresse des ooresults-Live-server mit Angabe des Ports, aber ohne Angabe des Protokolls,
      z.B. "server.com:8081".


    - Streaming key

      Key des Wettkampfes auf dem ooresults-Live-Server, für den die gesendeten Ergebnisse bestimmt sind.

      
    - Streaming enabled

      Es werden nur dann Daten zum ooresults-Live-Server gesendet, wenn die Parameter "Streaming address"
      und "Streaming key" definiert und "Streaming enabled" eingeschaltet ist.
