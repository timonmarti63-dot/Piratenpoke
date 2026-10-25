# Federjagd

Arcade-Schiesser für das Handy (HTML5 Canvas, eine Datei, keine Abhängigkeiten). `index.html` im Browser öffnen oder per Capacitor in eine App verpacken.

## Inhalt
- **6 Spielmodi:** Klassik, Tages-Challenge, Blitz, Überleben, Boss-Kampf, Scharfschütze
- **20 Orte in 10 Ländern** (Schweiz, Österreich, Deutschland, Frankreich, Italien, Spanien, Grossbritannien, Niederlande, Griechenland, Norwegen). Hühner auf dem Land, Tauben in den Städten. Orte werden über Sterne freigeschaltet, weiter hinten ist es schwerer und gibt mehr Münzen.
- **5 Waffen** mit je 3 Upgrades und sichtbarem Lauf, Rückstoss und Mündungsfeuer
- **40 Waffen-Skins**, nur aus Kisten (Federbox, Alpen-Kiste, Gold-Kiste, pro Land eine eigene Länder-Kiste), mit CS:GO-artiger Walze
- **Fieber, Power-ups, Nuke** (bei 30er Serie), Goldrausch-Events, Schwärme, Bosse mit Angriffen
- **Fortschritt:** Rang/XP, 7 Perks, Tagesmissionen, 14 Erfolge, Tagesbonus-Serie, Vogeldex, Profil
- **Komfort:** Pause, Optionen (Lautstärke, Vibration, Steuerung Direkt/Zielen, Grafik), Tutorial-Hinweise, automatische Grafik-Reduktion bei schwachen Geräten
- **Sound:** synthetisierte Schüsse pro Waffe, Musik je nach Stimmung (Menü, Land, Stadt, Boss), Umgebungsgeräusche

## Werbung einbinden
Alle Werbe-Stellen laufen über `AdBridge.show(grund)` (Suche in `index.html`). Aktuell zeigt es eine 3-Sekunden-Testanzeige. Für echte Werbung die Funktion durch ein AdMob-Belohnungsvideo ersetzen, das `true` liefert, wenn das Video fertig geschaut wurde. Stellen: `double` (Münzen verdoppeln), `revive` (weiterspielen), `chest` (Gratis-Federbox, 3 pro Tag), `challenge` (Extra-Versuch).

## Speicherstand
`localStorage` unter `federjagd.save.v2`. In einer nativen App auf `@capacitor/preferences` umstellen.
