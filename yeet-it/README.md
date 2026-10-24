# Yeet It! – Der endlose Weitwurf

Spielbarer Hyper-Casual-Prototyp (HTML5 Canvas, eine Datei, keine Abhängigkeiten).
Starten: `yeet-it/index.html` im Browser öffnen (Maus oder Touch).

## Gameplay
- **Aufziehen & loslassen:** Katapult nach hinten ziehen, Winkel und Kraft bestimmen, loslassen.
- **Im Flug:** Tippen/Leertaste = Raketen-Boost (3 pro Flug).
- Münzen einsammeln, an Trampolinen und Ballons abprallen, Werbetafeln durchkrachen (Bonus-Münzen).
- Bodenkontakt beendet den Flug (mit Sprungkraft-Upgrade gibt es Bodenhüpfer).

## Progression
Drei Upgrades: **Abschusskraft**, **Sprungkraft (Bounce)**, **Offline-Einnahmen** (exponentiell wachsende Kosten, Zahlen als K/M/B/T).
Spielstand liegt in `localStorage`.

## Monetarisierung (Platzhalter)
- **Skins:** Dummy, Protein-Shaker, Sneaker, Amboss, Anime-Star – Kauf per Münzen oder Promo-Code (`SHAKER`, `KICKS`, `ZAP`).
- **Trails:** Regenbogen, Flammen, Energy-Nebel.
- **Billboards:** Sponsorennamen aus `SPONSORS` in `index.html` (später dynamisch ladbar).
- **Reward-Ad:** Button nach dem Flug → simulierter Spot (3 s) → Wiederbelebungs-Kick. Hier später ein echtes Ad-SDK einhängen (`#b-ad`).

## Als Mobile Game
Das Spiel ist eine installierbare **PWA** (Querformat, Vollbild, offline-fähig, Haptik per Vibration, Safe-Area-Support):
1. Ordner `yeet-it/` per HTTPS hosten (z. B. GitHub Pages) – `file://` funktioniert zum Testen, aber ohne Service Worker.
2. Auf dem Handy öffnen → **"Zum Startbildschirm hinzufügen"** (iOS Safari) bzw. **"App installieren"** (Android Chrome).

### Native App (Play Store / App Store)
Mit [Capacitor](https://capacitorjs.com/) lässt sich dieselbe Webapp einpacken:
```bash
mkdir yeetit-app && cd yeetit-app && npm init -y
npm i @capacitor/core @capacitor/cli @capacitor/android @capacitor/ios
npx cap init "Yeet It!" com.example.yeetit --web-dir=www
mkdir www && cp ../yeet-it/{index.html,manifest.webmanifest,sw.js,icon-*.png} www/
npx cap add android && npx cap add ios && npx cap sync
```
Für echte Werbung und In-App-Käufe dann ein Capacitor-Plugin (AdMob, RevenueCat) an `#b-ad` bzw. den Shop anbinden.
