# WindowStream — Benutzerhandbuch

Dieses Handbuch beschreibt die Arbeit mit der **fertigen ausführbaren Datei `WindowStream.exe`**. Python oder zusätzliche Bibliotheken müssen nicht installiert werden.

> **Sprache der Oberfläche.** Standardmäßig zeigt das Programm eine englische Oberfläche. Für Russisch öffnen Sie die Einstellungsdatei (Menüpunkt **Open settings file**), setzen `"language": "ru"` und starten das Programm neu. Eine deutsche Oberfläche gibt es nicht. In diesem Handbuch stehen Menüpunkte und Meldungen deshalb so, wie sie in der englischen Oberfläche erscheinen; bei Bedarf folgt die deutsche Erklärung.

## Inhalt

1. [Was das Programm macht](#1-was-das-programm-macht)
2. [Voraussetzungen](#2-voraussetzungen)
3. [Installation und erster Start](#3-installation-und-erster-start)
4. [Schnellstart: fünf Schritte](#4-schnellstart-fünf-schritte)
5. [Das Symbol im Infobereich](#5-das-symbol-im-infobereich)
6. [Das Menü des Symbols](#6-das-menü-des-symbols)
7. [Das Fenster für die Übertragung wählen](#7-das-fenster-für-die-übertragung-wählen)
8. [Ansicht auf dem Tablet](#8-ansicht-auf-dem-tablet)
9. [Die Einstellungsdatei](#9-die-einstellungsdatei)
10. [Aufnahmemodi: screen und printwindow](#10-aufnahmemodi-screen-und-printwindow)
11. [Start mit Parametern](#11-start-mit-parametern)
12. [Mit Windows starten](#12-mit-windows-starten)
13. [Pause, Beenden und Schließen](#13-pause-beenden-und-schließen)
14. [Mehrere Übertragungen gleichzeitig](#14-mehrere-übertragungen-gleichzeitig)
15. [Aktualisieren und Entfernen](#15-aktualisieren-und-entfernen)
16. [Sicherheit](#16-sicherheit)
17. [Meldungen des Programms](#17-meldungen-des-programms)
18. [Fehlerbehebung](#18-fehlerbehebung)
19. [Einschränkungen](#19-einschränkungen)
20. [Häufige Fragen](#20-häufige-fragen)

---

## 1. Was das Programm macht

WindowStream zeigt **ein Fenster** Ihres Computers auf dem Bildschirm eines anderen Geräts (Tablet, Smartphone, anderer Computer) in einem gewöhnlichen Webbrowser. Das Bild wird in Echtzeit aktualisiert. Das Fenster lässt sich vom Tablet aus nicht bedienen: Es ist nur eine Ansicht.

Kurz gesagt: Das Programm auf dem PC nimmt den Inhalt des gewählten Fensters auf und stellt ihn im lokalen Netzwerk als Videostream bereit. Auf dem Tablet öffnen Sie im Browser die Adresse des Computers, zum Beispiel `http://192.168.1.20:8080/`, und sehen das Fenster.

Das Programm läuft im Hintergrund und wird über ein Symbol im Infobereich der Taskleiste (neben der Uhr) gesteuert.

## 2. Voraussetzungen

**Auf dem Computer:**

- Windows 10 oder 11, 64 Bit.
- Die Datei `WindowStream.exe`. Es muss nichts installiert werden.

**Auf dem Tablet oder anderen Gerät:**

- Ein aktueller Browser (Chrome, Edge, Firefox und ähnliche).
- Eine Verbindung zum **selben Netzwerk** wie der Computer (meist dasselbe WLAN).

**Im Netzwerk:**

- Der Router darf den Datenaustausch zwischen den Geräten nicht verbieten (bei Routern heißt diese Funktion oft „Client-Isolation“ oder „AP-Isolation“).

## 3. Installation und erster Start

### Installation

1. Legen Sie einen dauerhaften Ordner an, zum Beispiel `C:\Tools\WindowStream\`, und kopieren Sie `WindowStream.exe` hinein.
2. Starten Sie das Programm nicht aus dem Ordner *Downloads* oder aus temporären Ordnern, besonders wenn Sie den Autostart nutzen wollen: Wird die Datei später verschoben oder gelöscht, funktioniert der Autostart nicht mehr.

Es gibt keine separate Installation: Das Programm schreibt keine Dateien nach `Program Files` und braucht keine Administratorrechte.

### Erster Start

1. Doppelklicken Sie auf `WindowStream.exe`.
2. **SmartScreen-Warnung.** Die Datei ist nicht digital signiert, daher zeigt Windows möglicherweise ein blaues Fenster „Der Computer wurde durch Windows geschützt“. Klicken Sie auf **Weitere Informationen → Trotzdem ausführen**. Auch ein Virenscanner kann auf eine solche Datei reagieren; fügen Sie das Programm dann zu den Ausnahmen hinzu.
3. **Firewall-Abfrage.** Windows fragt, ob das Programm auf das Netzwerk zugreifen darf. Setzen Sie ein Häkchen bei **Private Netzwerke** und klicken Sie auf **Zugriff zulassen**. Ohne das kann sich das Tablet nicht verbinden. Öffentliche Netzwerke müssen nicht freigegeben werden.
4. Im Infobereich erscheint ein graues Symbol (das Programm öffnet kein Fenster). Wenn Sie das Symbol nicht sehen, klicken Sie in der Taskleiste auf den Pfeil **^ „Ausgeblendete Symbole anzeigen“**. Damit das Symbol immer sichtbar ist, ziehen Sie es aus dieser Liste auf die Taskleiste.

Beim ersten Start legt das Programm eine Einstellungsdatei an (siehe [Abschnitt 9](#9-die-einstellungsdatei)).

## 4. Schnellstart: fünf Schritte

1. **Starten Sie** `WindowStream.exe` und suchen Sie das Symbol im Infobereich.
2. **Öffnen Sie das Fenster, das angezeigt werden soll** (es muss wiederhergestellt sein, nicht in die Taskleiste minimiert).
3. Klicken Sie mit der **rechten Maustaste** auf das Symbol → Punkt **Window: not selected** → wählen Sie das gewünschte Fenster aus der Liste. Die Übertragung beginnt sofort, das Symbol wird grün.
4. **Adresse herausfinden:** Bewegen Sie den Mauszeiger auf das Symbol — der Tooltip zeigt die Adresse, zum Beispiel `http://192.168.1.20:8080/`.
5. **Geben Sie diese Adresse im Browser des Tablets ein.** Sie sehen nun das Fenster vom Computer.

Beim nächsten Start merkt sich das Programm das Fenster und beginnt die Übertragung selbst: Sie müssen es nicht erneut auswählen.

## 5. Das Symbol im Infobereich

### Farben des Symbols

| Symbol | Zustand |
| --- | --- |
| Grauer Kreis mit Quadrat | Übertragung gestoppt |
| Grüner Kreis mit Dreieck | Übertragung läuft |
| Gelber Kreis mit zwei Balken | Pause |

### Tooltip

Wenn Sie während der Übertragung den Mauszeiger auf das Symbol bewegen, sehen Sie zum Beispiel:

```
Window broadcast: live
Capture 10 fps · new frames 3 fps · clients 1
http://192.168.1.20:8080/
```

- **Capture** — wie oft pro Sekunde das Programm das Fenster aufnimmt.
- **new frames** — wie viele geänderte Bilder pro Sekunde gesendet werden. Ändert sich das Bild im Fenster nicht, steht hier `0`. Das ist normal: Das Programm sendet keine identischen Bilder und spart so Prozessorleistung und Netzwerk.
- **clients** — wie viele Browser die Übertragung gerade ansehen.
- Die letzte Zeile ist die Adresse für das Tablet.

Die Werte werden einmal pro Sekunde aktualisiert. Liegt **Capture** deutlich unter der eingestellten Bildrate (standardmäßig 10), kommt der Computer nicht hinterher: Verringern Sie Bildrate, Skalierung oder Qualität (siehe [Abschnitt 9](#9-die-einstellungsdatei)).

## 6. Das Menü des Symbols

Das Menü öffnet sich mit einem **Rechtsklick** auf das Symbol.

| Punkt | Funktion |
| --- | --- |
| **Start broadcast** (Übertragung starten) | Startet die Übertragung des gewählten Fensters. Verfügbar, wenn die Übertragung gestoppt ist. |
| **Pause / Resume** (Pause / Fortsetzen) | Hält die Übertragung an und setzt sie fort. Auf dem Tablet bleibt das letzte Bild mit der Markierung „Paused“ stehen. Der Name des Punkts ändert sich je nach Zustand. |
| **Stop broadcast** (Übertragung beenden) | Beendet die Übertragung vollständig und schließt die Verbindungen. Das Tablet zeigt „No connection“. |
| **Window: …** (Fenster) | Öffnet die Liste der Fenster, die übertragen werden können. Das aktuelle Fenster ist markiert. Die Auswahl wird gespeichert und startet sofort die Übertragung dieses Fensters. |
| **Bring window to front** (Fenster in den Vordergrund) | Stellt das Fenster wieder her (falls minimiert) und bringt es vor alle anderen. |
| **Start with Windows** (Mit Windows starten) | Schaltet den Autostart ein und aus (ein Häkchen zeigt, dass er aktiv ist). |
| **Open settings file** (Einstellungsdatei öffnen) | Öffnet die Einstellungsdatei im Editor (Notepad). |
| **Exit** (Beenden) | Beendet die Übertragung und schließt das Programm. |

Momentan nicht verfügbare Punkte sind ausgegraut.

## 7. Das Fenster für die Übertragung wählen

### So wählen Sie es aus

Rechtsklick auf das Symbol → **Window: …** → Fenster aus der Liste auswählen.

Was bei der Auswahl passiert:

1. Das Fenster wird gemerkt (Titel und Name des Programms, zu dem es gehört);
2. war das Fenster minimiert, wird es wiederhergestellt und dann in den Vordergrund gebracht;
3. die Übertragung startet mit dem neuen Fenster neu, und eine Benachrichtigung mit der Adresse erscheint.

Die Liste zeigt gewöhnliche Programmfenster (bis zu 40, alphabetisch). Nicht angezeigt werden: Eingabeaufforderung und Terminal, der Desktop, Hilfs- und versteckte Fenster sowie sehr kleine Fenster. Fehlt das gewünschte Fenster in der Liste, prüfen Sie, ob es geöffnet und nicht minimiert ist, und öffnen Sie das Menü erneut: Die Liste wird bei jedem Öffnen neu erstellt.

### Wie das Programm das Fenster später wiederfindet

Das Programm merkt sich den **Titel** des Fensters und den **Dateinamen des Programms** (zum Beispiel `myapp.exe`). Bei der Suche gelten diese Regeln in dieser Reihenfolge:

1. Der Titel stimmt vollständig überein;
2. der Titel beginnt mit dem gespeicherten Text;
3. der Titel enthält den gespeicherten Text;
4. wenn nichts passt, aber der Programmname bekannt ist — wird das **größte sichtbare Fenster dieses Programms** genommen.

Dank der vierten Regel geht die Übertragung nicht verloren, wenn sich der Fenstertitel ändert. Bei vielen Programmen enthält der Titel zum Beispiel den Namen der geöffneten Datei, und beim Öffnen einer anderen Datei ändert sich der Titel.

Damit das Fenster immer übertragen wird, auch wenn sich der Titel ändert, können Sie in den Einstellungen nur einen Teil des Titels angeben (zum Beispiel den Programmnamen ohne Dateinamen): siehe Parameter `title` in [Abschnitt 9](#9-die-einstellungsdatei).

### Das Fenster ist geschlossen oder noch nicht geöffnet

- Schließen Sie das Fenster während der Übertragung, sucht das Programm es erneut und zeigt es weiter an, sobald es wieder erscheint.
- Ist das Fenster beim Start des Programms nicht geöffnet (zum Beispiel direkt nach der Anmeldung bei Windows), zeigt das Programm die Meldung „Window "…" not found. Waiting for the window to appear...“ und prüft alle 5 Sekunden, bis das Fenster erscheint.

## 8. Ansicht auf dem Tablet

### So öffnen Sie die Ansicht

1. Stellen Sie sicher, dass das Tablet mit demselben Netzwerk wie der Computer verbunden ist.
2. Geben Sie im Browser des Tablets die Adresse aus dem Tooltip des Symbols ein, zum Beispiel `http://192.168.1.20:8080/`. Die Adresse beginnt mit `http://` (nicht `https://`).
3. Es ist praktisch, die Seite als Lesezeichen zu speichern.

### Adresse ermitteln, wenn der Tooltip eine unpassende zeigt

Der Tooltip zeigt die am besten geeignete Adresse, der Computer kann aber mehrere Netzwerkverbindungen haben. So sehen Sie alle Adressen:

1. Drücken Sie `Win + R`, geben Sie `cmd` ein und drücken Sie die Eingabetaste;
2. führen Sie den Befehl `ipconfig` aus;
3. suchen Sie die **IPv4-Adresse** der Verbindung, über die der Computer mit dem Tablet verbunden ist (beginnt meist mit `192.168.` oder `10.`).

Adressen, die mit **`169.254.`** beginnen, sind Link-Local-Adressen: Windows hat sie selbst vergeben, weil es keine Adresse vom Router erhalten hat. Sie funktionieren nur, wenn auch das Tablet eine Adresse aus diesem Bereich hat. Bei einer solchen Adresse sollten Sie in der Regel die Netzwerkverbindung prüfen.

Der Port (`8080`) kann in den Einstellungen geändert werden.

### Was auf der Seite zu sehen ist

Das Fensterbild ist unter Beibehaltung der Proportionen in einen sauberen Rahmen mit abgerundeten Ecken eingepasst, der den ganzen Browserbereich ausfüllt. Der Titel des Browser-Tabs entspricht dem Titel des übertragenen Fensters und wird mit ihm aktualisiert.

**Modusanzeige oben rechts:**

| Anzeige | Bedeutung |
| --- | --- |
| Grüner blinkender Punkt, **Live** | Die Übertragung läuft. Daneben steht `N fps · M ms`: wie viele neue Bilder pro Sekunde das Tablet erhält und die ungefähre Verzögerung. |
| Gelber Punkt, **Paused** | Auf dem Computer ist die Pause aktiv. Das Bild steht still und ist abgedunkelt. |
| Roter Punkt, **No connection** | Der Computer ist nicht erreichbar oder die Übertragung ist gestoppt. Das Bild ist grau, darüber dreht sich ein Ladesymbol. Die Seite verbindet sich selbst neu, ein Aktualisieren ist nicht nötig. |

Auch die Farbe des dünnen Leuchtens am Rand des Rahmens entspricht dem Modus (grün, gelb, rot).

**Automatisches Ausblenden.** Während der normalen Übertragung verschwinden Anzeige und Schaltflächen nach 4 Sekunden, um das Bild nicht zu verdecken. Tippen Sie auf den Bildschirm, um sie wieder einzublenden. Bei Pause und bei Verbindungsverlust bleiben sie dauerhaft sichtbar.

### Gestensteuerung

| Aktion | Ergebnis |
| --- | --- |
| Tippen | Anzeige und Schaltflächen einblenden |
| Zwei Finger (zusammen- und auseinanderziehen) | Zoom bis ×8 |
| Ein Finger bei vergrößertem Bild | Bild verschieben |
| Doppeltippen | An dieser Stelle 2,5-fach vergrößern; erneutes Doppeltippen stellt die Ausgangsansicht wieder her |
| Tippen auf die Markierung `×2.4 · reset` (unten rechts) | Zoom zurücksetzen |
| Langes Drücken (etwa 0,7 s) | Zeile `fps · ms` aus- oder einblenden. Die Wahl wird im Browser gespeichert |
| Schaltfläche oben links | Vollbildmodus |
| Mausrad (am Computer) | Zoom |

Die Zoom-Markierung unten rechts erscheint, solange das Bild vergrößert ist, und bleibt sichtbar.

> Tipp: Beim Vergrößern ist das Bild so scharf, wie es vom Computer übertragen wird. Für scharfes Vergrößern lassen Sie `scale` auf `1.0` (Standardwert).

### Mehrere Geräte

An eine Übertragung können mehrere Geräte gleichzeitig angeschlossen werden: Die Anzahl der Verbindungen steht im Tooltip des Symbols („clients“).

## 9. Die Einstellungsdatei

### Wo sie liegt

```
%APPDATA%\WindowStream\settings.json
```

Normalerweise ist das `C:\Users\<Benutzername>\AppData\Roaming\WindowStream\settings.json`.

Am einfachsten öffnen Sie sie über das Menü des Symbols: **Open settings file** (sie öffnet sich im Editor). Die Datei wird beim ersten Start automatisch angelegt.

> **Änderungen werden nach einem Neustart des Programms wirksam.** Schließen Sie es mit **Exit** und starten Sie es erneut.

Das im Menü gewählte Fenster wird automatisch in der Datei gespeichert (Parameter `title` und `process`).

### Beispiel

```json
{
  "title": "Untitled - Map",
  "process": "mapapp.exe",
  "port": 8080,
  "fps": 15.0,
  "quality": 75,
  "scale": 1.0,
  "mode": "printwindow",
  "no_diff": false,
  "no_turbo": false,
  "autostart_broadcast": true,
  "language": "en"
}
```

Halten Sie das JSON-Format ein: Zeichenketten in doppelten Anführungszeichen, Kommas zwischen den Parametern, kein Komma nach dem letzten Parameter, und `true` und `false` klein und ohne Anführungszeichen. Ist die Datei beschädigt, ignoriert das Programm sie und verwendet die Standardwerte. Korrigieren Sie die Datei dann oder löschen Sie sie: Beim nächsten Start wird sie neu angelegt.

### Parameter

| Parameter | Standard | Beschreibung |
| --- | --- | --- |
| `title` | leer | Fenstertitel oder ein Teil davon (Groß-/Kleinschreibung egal). |
| `process` | leer | Dateiname des Programms, dem das Fenster gehört (zum Beispiel `mapapp.exe`). Hilft, das Fenster zu finden, wenn sich der Titel ändert. Wird bei der Fensterwahl im Menü automatisch ausgefüllt. |
| `port` | `8080` | Der Port, unter dem die Übertragung erreichbar ist. Ändern Sie ihn, wenn der Port von einem anderen Programm belegt ist. |
| `fps` | `10` | Maximale Bilder pro Sekunde (nicht weniger als 0,5). Je höher, desto flüssiger und desto höher die Last. |
| `quality` | `75` | JPEG-Qualität von 1 bis 95. Höher ist schärfer, belastet aber das Netzwerk stärker. |
| `scale` | `1.0` | Skalierung des übertragenen Bilds (nicht weniger als 0,1). `0.5` ist an jeder Seite halb so groß. |
| `mode` | `"printwindow"` | Aufnahmemodus: `"screen"` oder `"printwindow"` ([Abschnitt 10](#10-aufnahmemodi-screen-und-printwindow)). |
| `no_diff` | `false` | `true` — Änderungserkennung ausschalten und jedes Bild senden (erhöht die Last, meist unnötig). |
| `no_turbo` | `false` | `true` — den schnellen JPEG-Encoder nicht verwenden (nur für Vergleiche nötig). |
| `autostart_broadcast` | `true` | `false` — die Übertragung nicht direkt nach dem Programmstart beginnen, sondern auf den Befehl **Start broadcast** im Menü warten. |
| `language` | `"en"` | Sprache der Oberfläche: `"en"` — Englisch (Standard), `"ru"` — Russisch. Wirkt auf das Tray-Menü, Benachrichtigungen, Konsolenmeldungen, `--help` und die Seite auf dem Tablet. Nach der Änderung das Programm neu starten. |

### Empfohlene Werte

| Situation | Einstellungen |
| --- | --- |
| Normale Kartenansicht | Standardwerte (`fps` 10, `quality` 75, `scale` 1.0) |
| Schwaches WLAN oder schwaches Tablet | `fps` 10–15, `quality` 60–70, `scale` 0.75 |
| Maximale Schärfe, viel Zoom | `scale` 1.0, `quality` 80–90, `fps` 10 |
| Flüssige Bewegung | `fps` 20–30 (höhere Last auf dem Computer) |
| Geringere Last auf dem Computer | `fps` 5–10, `scale` 0.5–0.75 |

Ändert sich das Bild im Fenster nicht, belastet das Programm Computer und Netzwerk kaum — das leistet die Erkennung von Bildänderungen, die standardmäßig aktiv ist.

## 10. Aufnahmemodi: screen und printwindow

Der Parameter `mode` legt fest, wie das Programm das Fensterbild erhält.

| | `screen` | `printwindow` (Standard) |
| --- | --- | --- |
| Prinzip | Kopiert das Rechteck des Fensters vom Bildschirm | Bittet das Fenster selbst, seinen Inhalt zu zeichnen |
| Andere Fenster über dem gewünschten | **Erscheinen in der Übertragung** | Erscheinen nicht |
| Fenster von anderen verdeckt | Zu sehen ist, was oben liegt | Wird normal übertragen |
| Programme mit GPU-Darstellung (3D-Karten, Video, Spiele) | Funktioniert | Bei manchen Programmen ist das Bild schwarz oder veraltet |
| Minimiertes Fenster | Wird nicht übertragen | Wird nicht übertragen |

**So wählen Sie den Modus:**

1. Standard ist `"printwindow"`. Ist das Bild korrekt, behalten Sie diesen Modus: Andere Fenster gelangen dann nicht mehr in die Übertragung.
2. Ist das Bild schwarz oder aktualisiert es sich nicht, wechseln Sie zu `"screen"`. In diesem Modus halten Sie das Fenster im Vordergrund und achten darauf, dass nichts es verdeckt. Bei der Fensterwahl im Menü bringt das Programm das Fenster selbst nach vorn, und der Punkt **Bring window to front** tut das jederzeit.

Übertragen wird immer der **Clientbereich des Fensters** (ohne Titelleiste und Rahmen) in seiner realen Größe in Pixeln.

## 11. Start mit Parametern

Normalerweise sind keine Kommandozeilenparameter nötig: Alles wird in der Einstellungsdatei gespeichert. Auf Wunsch können Sie das Programm aber mit Schaltern starten.

### Start über die Eingabeaufforderung

Öffnen Sie die Eingabeaufforderung im Ordner des Programms und geben Sie zum Beispiel ein:

```
WindowStream.exe --title "Untitled - Map" --mode printwindow --save
```

### Verknüpfung mit Parametern

1. Klicken Sie mit der rechten Maustaste auf `WindowStream.exe` → **Senden an → Desktop (Verknüpfung erstellen)**.
2. Klicken Sie mit der rechten Maustaste auf die Verknüpfung → **Eigenschaften**.
3. Fügen Sie im Feld **Ziel** hinter dem Dateipfad die Parameter durch Leerzeichen getrennt an, zum Beispiel:
   `"C:\Tools\WindowStream\WindowStream.exe" --port 9000`

### Liste der Schalter

| Schalter | Beschreibung |
| --- | --- |
| `--title "Text"` | Fenstertitel oder ein Teil davon. |
| `--list` | Liste der geöffneten Fenster (Handle, Programm, Titel) anzeigen und beenden. |
| `--port N` | Port (Standard 8080). |
| `--fps N` | Maximale Bilder pro Sekunde (Standard 10). |
| `--quality N` | JPEG-Qualität 1–95 (Standard 75). |
| `--scale X` | Bildskalierung, zum Beispiel `0.5` (Standard 1.0). |
| `--mode screen` / `--mode printwindow` | Aufnahmemodus. |
| `--no-diff` | Erkennung von Bildänderungen ausschalten. |
| `--no-turbo` | Den schnellen JPEG-Encoder nicht verwenden. |
| `--no-autostart` | Die Übertragung beim Start nicht beginnen, auf einen Menübefehl warten. Mit dem Windows-Autostart hat dieser Schalter nichts zu tun. |
| `--config "Pfad"` | Eine andere Einstellungsdatei verwenden. |
| `--save` | Die Parameter dieses Starts in der Einstellungsdatei speichern. |
| `--help` | Hilfe zu den Schaltern. |
| `--version` | Programmversion anzeigen und beenden. |

**Vorrang.** Kommandozeilenschalter haben Vorrang vor der Einstellungsdatei, gelangen aber nicht von selbst in die Datei, wenn Sie nicht `--save` angeben. Umschalter (`--no-diff`, `--no-turbo`) lassen sich nur einschalten; um einen solchen Parameter auszuschalten, ändern Sie die Einstellungsdatei.

### Liste der Fenster

Das kompilierte Programm hat kein eigenes Konsolenfenster, daher geben `--list`, `--help` und `--version` ihren Text in **der Eingabeaufforderung aus, aus der sie gestartet wurden**:

```
WindowStream.exe --list
```

Die Eingabeaufforderung kann früher zurückkehren, als der Text erscheint, weil das Programm eine Fensteranwendung ist. Damit sie wartet, verwenden Sie `start /wait "" WindowStream.exe --list`. Gibt es keine Konsole für die Ausgabe (zum Beispiel beim Start per Doppelklick), wird der Text in einem Meldungsfenster angezeigt.

## 12. Mit Windows starten

### So schalten Sie es ein

Rechtsklick auf das Symbol → **Start with Windows**. Neben dem Punkt erscheint ein Häkchen. Erneutes Auswählen schaltet den Autostart aus.

Der Autostart wird nur für Ihr Benutzerkonto eingerichtet und braucht keine Administratorrechte.

### Was bei der Anmeldung bei Windows passiert

1. Das Programm startet im Hintergrund, das Symbol erscheint im Infobereich.
2. Ist in den Einstellungen ein Fenster festgelegt und `autostart_broadcast` gleich `true`, beginnt das Programm mit der Übertragung.
3. Existiert das Fenster noch nicht (zum Beispiel, weil das benötigte Programm ebenfalls gerade startet), wartet das Programm darauf, prüft alle 5 Sekunden und beginnt dann selbst die Übertragung.

Ist in den Einstellungen kein Fenster gewählt, zeigt das Programm nur einen Hinweis, im Menü des Symbols ein Fenster auszuwählen.

### Wenn die Datei verschoben wurde

Haben Sie `WindowStream.exe` in einen anderen Ordner verschoben und von dort gestartet, aktualisiert das Programm den Pfad im Autostart selbst. Haben Sie die Datei gelöscht, ohne den Autostart auszuschalten, findet Windows das Programm bei der Anmeldung nicht; um den Eintrag zu entfernen, starten Sie das Programm erneut aus einem beliebigen Ordner und schalten den Autostart im Menü aus.

## 13. Pause, Beenden und Schließen

| Aktion | Was passiert | Was das Tablet zeigt |
| --- | --- | --- |
| **Pause** | Die Aufnahme des Fensters wird angehalten, das Programm läuft weiter | Das letzte Bild, die Markierung „Paused“ |
| **Resume** | Die Aufnahme wird fortgesetzt | Live-Bild |
| **Stop broadcast** | Aufnahme und Bereitstellung enden, der Port wird freigegeben, das Symbol ist grau | „No connection“; die Seite verbindet sich selbst, sobald Sie die Übertragung wieder starten |
| **Exit** | Das Programm wird vollständig geschlossen | „No connection“ |

Wird das Fenster minimiert, bleibt das Bild auf dem Tablet beim letzten Bild stehen, bis das Fenster wiederhergestellt wird. Das Programm läuft dabei weiter.

## 14. Mehrere Übertragungen gleichzeitig

Standardmäßig kann nur **eine Kopie** des Programms laufen: Beim zweiten Start erscheint die Meldung „The program is already running“ mit dem Hinweis, das Symbol neben der Uhr zu suchen, und die zweite Kopie wird geschlossen. Der Port bleibt davon unberührt.

Um mehrere Fenster gleichzeitig zu übertragen, starten Sie Kopien mit **unterschiedlichen Einstellungsdateien und unterschiedlichen Ports**:

```
WindowStream.exe --config "D:\ws\first.json" --port 8080 --title "Window 1" --save
WindowStream.exe --config "D:\ws\second.json" --port 8081 --title "Window 2" --save
```

Öffnen Sie auf dem Tablet unterschiedliche Adressen: `http://192.168.1.20:8080/` und `http://192.168.1.20:8081/`. Beide Ports müssen in der Firewall freigegeben werden, und der Autostart funktioniert für die Kopie, aus der Sie ihn eingeschaltet haben.

## 15. Aktualisieren und Entfernen

### Aktualisieren

1. Schließen Sie das Programm: Rechtsklick auf das Symbol → **Exit**.
2. Ersetzen Sie `WindowStream.exe` durch die neue Version im selben Ordner.
3. Starten Sie es. Die Einstellungen bleiben erhalten, da sie getrennt vom Programm gespeichert werden.

War der Autostart eingeschaltet, funktioniert er weiter (der Pfad bleibt derselbe).

### Vollständiges Entfernen

1. Schalten Sie den Autostart aus: Rechtsklick auf das Symbol → Häkchen bei **Start with Windows** entfernen.
2. Schließen Sie das Programm mit **Exit**.
3. Löschen Sie `WindowStream.exe`.
4. Auf Wunsch löschen Sie den Einstellungsordner `%APPDATA%\WindowStream\` (geben Sie diesen Pfad in die Adressleiste des Explorers ein).

## 16. Sicherheit

- Die Übertragung ist **nicht passwortgeschützt und nicht verschlüsselt**. Jeder, der mit Ihrem Netzwerk verbunden ist und die Adresse kennt, kann den Fensterinhalt ansehen.
- Verwenden Sie das Programm nur in vertrauenswürdigen Netzwerken (Heim- oder Firmennetz, mit dem nur Ihre eigenen Geräte verbunden sind). In öffentlichen Netzwerken (Café, Hotel) verwenden Sie es nicht.
- Geben Sie in der Firewall nur den Zugriff für **private Netzwerke** frei.
- Übertragen Sie keine Fenster mit vertraulichen Daten, wenn Fremde im Netzwerk sind.
- Für den Zugriff aus einem anderen Netzwerk nutzen Sie ein VPN. Öffnen Sie den Port des Programms nicht ins Internet.
- Das Tablet kann den Computer über dieses Programm nicht steuern: Es ist nur eine Ansicht.

## 17. Meldungen des Programms

Das kompilierte Programm zeigt keine Konsole, daher erscheinen Meldungen als Windows-Benachrichtigungen neben der Uhr.

| Meldung | Bedeutung und Maßnahme |
| --- | --- |
| **Broadcast started. Open on the tablet: …** | Alles in Ordnung, öffnen Sie die angegebene Adresse auf dem Tablet. |
| **Window "…" not found. Waiting for the window to appear...** | Das gewünschte Fenster ist nicht geöffnet. Öffnen Sie es: Die Übertragung beginnt selbst. Oder wählen Sie im Menü ein anderes Fenster. |
| **No window selected: choose one in the tray menu ("Window" item)** / **Choose a window in the tray menu: "Window" item** | In den Einstellungen ist kein Fenster festgelegt. Wählen Sie ein Fenster im Menü des Symbols. |
| **Could not open port 8080: …** | Der Port ist von einem anderen Programm oder einer anderen Kopie belegt. Ändern Sie `port` in der Einstellungsdatei. |
| **Streaming: …** | Die Übertragung wurde auf das gewählte Fenster umgestellt. |
| **The program will start with Windows** / **Autostart disabled** | Ergebnis des Umschaltens des Autostarts. |
| **Could not change autostart: …** | Der Registry-Eintrag ist nicht zugänglich (zum Beispiel durch eine Richtlinie der Organisation gesperrt). Wenden Sie sich an den Administrator. |
| **Could not open the settings file: …** | Der Editor wurde nicht gestartet. Öffnen Sie die Datei manuell (siehe [Abschnitt 9](#9-die-einstellungsdatei)). |
| Fenster **The program is already running** | Eine Kopie des Programms läuft bereits. Suchen Sie ihr Symbol neben der Uhr, möglicherweise bei den ausgeblendeten Symbolen. |

## 18. Fehlerbehebung

| Problem | Mögliche Ursache und Lösung |
| --- | --- |
| Das Tablet öffnet die Seite nicht | 1) Tablet und Computer sind in verschiedenen Netzwerken — verbinden Sie sie mit demselben. 2) Die Firewall blockiert den Zugriff — erlauben Sie das Programm für private Netzwerke (Start → „Eine App durch die Windows-Firewall kommunizieren lassen“). 3) Falsche Adresse — prüfen Sie sie mit `ipconfig` (siehe [Abschnitt 8](#8-ansicht-auf-dem-tablet)). 4) Der Router hat Client-Isolation aktiviert — schalten Sie sie aus. 5) Die Adresse beginnt mit `169.254.` — prüfen Sie die Netzwerkverbindung. |
| Das Symbol ist nicht sichtbar | Klicken Sie in der Taskleiste auf den Pfeil **^** („Ausgeblendete Symbole anzeigen“) und ziehen Sie das Symbol auf die Leiste. |
| Das Programm startet nicht, nichts passiert | Möglicherweise läuft es bereits: Das Symbol kann unter den ausgeblendeten sein. Starten Sie es erneut: Erscheint die Meldung „The program is already running“, läuft es. |
| SmartScreen oder Virenscanner blockiert die Datei | Die Datei ist nicht signiert. Klicken Sie auf „Weitere Informationen → Trotzdem ausführen“ oder fügen Sie die Datei zu den Ausnahmen des Virenscanners hinzu. |
| Über dem gewünschten Fenster sind andere Fenster zu sehen | Der Modus `screen` kopiert das Bild vom Bildschirm. Setzen Sie in den Einstellungen `"mode": "printwindow"` oder halten Sie das gewünschte Fenster im Vordergrund. |
| Das Bild ist schwarz | Das Fenster wird über die GPU gezeichnet und gibt seinen Inhalt nicht an den Modus `printwindow` ab. Setzen Sie `"mode": "screen"`. |
| Ein Teil des Fensters aktualisiert sich nicht | Dieser Teil liegt außerhalb des Bildschirmrands: Windows und das Programm zeichnen ihn nicht neu. Verschieben Sie das Fenster so, dass es vollständig auf den Bildschirm passt, oder nutzen Sie einen zweiten Monitor. |
| Das Bild steht still, die Anzeige zeigt aber „Live“ | Das Fenster ist minimiert. Stellen Sie es wieder her oder wählen Sie **Bring window to front**. |
| Im Tooltip steht „new frames 0 fps“ | Das Bild im Fenster ändert sich nicht. Das ist normal. |
| Nach dem Wechsel des Fensters blieb auf dem Tablet das alte Bild | Im Modus `screen` kann das neue Fenster hinter anderen Fenstern liegen. Bei der Fensterwahl im Menü wird es jetzt automatisch nach vorn gebracht; falls nicht, nutzen Sie den Punkt **Bring window to front**. |
| Hohe Prozessorlast | Verringern Sie `fps`, setzen Sie `scale` auf 0.5–0.75, verringern Sie `quality`. |
| Das Bild ruckelt oder hinkt hinterher | Schwaches WLAN oder schwaches Tablet: Verringern Sie `scale` und `quality`; verbinden Sie sich möglichst mit einem 5-GHz-Netz. Beobachten Sie die Verzögerung in ms auf dem Tablet und die Aufnahmerate im Tooltip des Symbols. |
| Die Verzögerung auf dem Tablet zeigt „—“ | Das ist in den ersten Sekunden nach dem Verbinden normal. |
| Die Übertragung startet nach der Windows-Anmeldung nicht | Das gewünschte Fenster ist noch nicht geöffnet (das Programm wartet darauf) oder in den Einstellungen ist kein Fenster gewählt — wählen Sie es im Menü des Symbols. |
| Das Fenster eines als Administrator gestarteten Programms wird nicht übertragen | Starten Sie WindowStream ebenfalls als Administrator (Rechtsklick auf die Datei → „Als Administrator ausführen“): Windows erlaubt gewöhnlichen Programmen nicht, Fenster mit erhöhten Rechten zu bedienen. |
| Einstellungen wirken nicht | Änderungen werden nach einem Neustart des Programms wirksam. Prüfen Sie auch das Dateiformat (Kommas, Anführungszeichen): Bei einem Fehler wird die Datei ignoriert. |
| Die Einstellungsdatei soll zurückgesetzt werden | Schließen Sie das Programm, löschen Sie `%APPDATA%\WindowStream\settings.json` und starten Sie es erneut. |

## 19. Einschränkungen

- Pro Kopie des Programms wird ein Fenster übertragen.
- Kein Ton.
- Keine Steuerung vom Tablet: nur Ansicht.
- Angezeigt wird nur der Clientbereich des Fensters (ohne Titelleiste und Rahmen).
- Ein minimiertes Fenster wird nicht übertragen: Auf dem Tablet bleibt das letzte Bild stehen.
- Ein Teil des Fensters außerhalb des Bildschirmrands wird nicht aktualisiert.
- Im Modus `printwindow` liefern manche Programme mit GPU-Darstellung ein schwarzes Bild; kopiergeschütztes Video wird in keinem Modus gezeigt.
- Kein Passwort und keine Verschlüsselung (nur einfaches `http://`).
- Die Oberfläche des Programms gibt es auf Englisch und Russisch (Einstellung `language`), nicht auf Deutsch.

## 20. Häufige Fragen

**Brauche ich Internet?**
Nein. Ein lokales Netzwerk zwischen Computer und Tablet genügt. Das Programm nutzt das Internet nicht.

**Kann ich vom Smartphone oder von einem anderen Computer aus zusehen?**
Ja. Jedes Gerät mit einem aktuellen Browser im selben Netzwerk ist geeignet.

**Wie viele Geräte können gleichzeitig zusehen?**
Mehrere. Die Anzahl der Verbindungen steht im Tooltip des Symbols.

**Schließt das Programm das Fenster oder stört es die Arbeit darin?**
Nein. Es nimmt nur den Inhalt des Fensters auf. Sie können am Computer wie gewohnt darin arbeiten. Die einzige Aktion am Fenster ist, es nach vorn zu bringen, wenn Sie es im Menü wählen oder den Punkt **Bring window to front** verwenden.

**Was passiert, wenn ich das übertragene Fenster schließe?**
Das Programm läuft weiter und findet das Fenster wieder, sobald es erscheint. Bis dahin zeigt das Tablet das letzte Bild.

**Was passiert, wenn sich der Fenstertitel ändert?**
Das Programm findet das Fenster über den Programmnamen (das größte Fenster dieses Programms). Der Tab-Titel auf dem Tablet wird aktualisiert.

**Wie ändere ich den Port?**
Ändern Sie `port` in der Einstellungsdatei und starten Sie das Programm neu. Verwenden Sie auf dem Tablet die neue Adresse, zum Beispiel `http://192.168.1.20:9000/`.

**Warum unterscheidet sich die Adresse im Tooltip von meiner Erwartung?**
Der Computer kann mehrere Netzwerkadapter haben (WLAN, Ethernet, virtuelle). Wählen Sie mit `ipconfig` die Adresse der Verbindung, über die der Computer mit dem Tablet verbunden ist.

**Wo sehe ich die Einstellungen und was sich darin ändern lässt?**
Über den Menüpunkt **Open settings file** und in [Abschnitt 9](#9-die-einstellungsdatei).

**Wie beende ich das Programm ganz?**
Rechtsklick auf das Symbol → **Exit**. Ein Fenster muss man nicht schließen: Das Programm hat kein Fenster, nur ein Symbol.
