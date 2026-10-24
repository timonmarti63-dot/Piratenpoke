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
