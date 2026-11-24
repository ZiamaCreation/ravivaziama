# ravivaziama.com

Portfolio-Website von Raviva Nsiama.

- **Inhalte bearbeiten:** https://ravivaziama.com/admin (Anmeldung mit GitHub-Token)
- **Inhalte liegen in:** `content/` (Filme, Visual Works, Seiten & Listen)
- **Bilder:** `img/` · **Videos:** `media/`
- **Aufbau der Seite:** `template.html` (Design) + `build.py` (setzt alles zusammen)
- **Veröffentlichen:** passiert automatisch. Jede Änderung hier löst bei Cloudflare Pages einen neuen Build aus
  (Build-Befehl `python3 build.py`, Ausgabeordner `dist`).
