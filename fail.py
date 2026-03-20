(generic) ubuntu@192.168.52.214 ~/rubin $ pixi run build-app
✨ Pixi task (build-app in default): python scripts/build_app_html.py: (React-App bauen: Libraries herunterladen und in rubin_ui.html einbetten (einmalig, braucht Internet))   
[build_app_html] CDN-Libraries inlinen ...

  Gelesen: /mnt/rubin/app/frontend/index.html (179,536 bytes)

  WARNUNG: Weder CDN-Tag noch Inline-Block fuer react gefunden!
  WARNUNG: Weder CDN-Tag noch Inline-Block fuer react-dom gefunden!
  WARNUNG: Weder CDN-Tag noch Inline-Block fuer babel gefunden!

  FEHLER: 3 Library(s) fehlen: react, react-dom, babel

  Manueller Fallback:
    mkdir -p /mnt/rubin/app/frontend/lib
    # react:
    #   Download: https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js
    #   Speichern: /mnt/rubin/app/frontend/lib/react.min.js
    # react-dom:
    #   Download: https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js
    #   Speichern: /mnt/rubin/app/frontend/lib/react-dom.min.js
    # babel:
    #   Download: https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.23.9/babel.min.js
    #   Speichern: /mnt/rubin/app/frontend/lib/babel.min.js

  Dann erneut: python scripts/build_app_html.py
