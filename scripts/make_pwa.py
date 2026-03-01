import os
import json
import pygame as pg
from pathlib import Path


def make_pwa():
    build_dir = Path("build/web")
    if not build_dir.exists():
        print("Build directory does not exist.")
        return

    # 1. Generate icons
    # We use pg.display.set_mode temporarily just to ensure pygame can scale images in headless environments
    # if required, though image module usually works without it.
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pg.init()
    pg.display.set_mode((1, 1))

    duck_img_path = Path("assets/sprites/duck.png")
    if duck_img_path.exists():
        try:
            img = pg.image.load(str(duck_img_path)).convert_alpha()
            icon_192 = pg.transform.smoothscale(img, (192, 192))
            icon_512 = pg.transform.smoothscale(img, (512, 512))
            pg.image.save(icon_192, str(build_dir / "icon-192.png"))
            pg.image.save(icon_512, str(build_dir / "icon-512.png"))
            # Apple touch icon
            pg.image.save(icon_192, str(build_dir / "apple-touch-icon.png"))
            print("PWA icons generated successfully.")
        except Exception as e:
            print(f"Error generating icons: {e}")
    else:
        print("Duck image not found for PWA icons.")

    # 2. Generate manifest.json
    manifest = {
        "name": "Duck Jump",
        "short_name": "Duck Jump",
        "start_url": "./index.html",
        "display": "standalone",
        "background_color": "#7f7f7f",
        "theme_color": "#7f7f7f",
        "description": "A duck jumping game!",
        "icons": [
            {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
        ],
    }
    with open(build_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=4)
    print("manifest.json generated successfully.")

    # 3. Generate sw.js (Service Worker)
    sw_content = """
const CACHE_NAME = 'duck-jump-v1';
const ASSETS = [
  './',
  './index.html',
  './tie-and-jon-pygame.apk',
  './favicon.png',
  './icon-192.png',
  './icon-512.png',
  './manifest.json'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(ASSETS);
    }).catch(err => {
      console.warn('SW Install caching failed:', err);
    })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});
"""
    with open(build_dir / "sw.js", "w") as f:
        f.write(sw_content.strip())
    print("sw.js generated successfully.")

    # 4. Modify index.html
    index_path = build_dir / "index.html"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            html = f.read()

        head_injection = """<head>
<meta charset="utf-8">
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#7f7f7f">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<script>
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('sw.js').then(function(registration) {
      console.log('ServiceWorker registration successful with scope: ', registration.scope);
    }, function(err) {
      console.log('ServiceWorker registration failed: ', err);
    });
  });
}
</script>
</head>"""

        if '<html lang="en-us">' in html:
            html = html.replace(
                '<html lang="en-us">', f'<html lang="en-us">\n{head_injection}\n'
            )
        elif "<html>" in html:
            html = html.replace("<html>", f"<html>\n{head_injection}\n")
        else:
            html = head_injection + "\n" + html

        with open(index_path, "w", encoding="utf-8") as f:
            f.write(html)
        print("index.html modified for PWA successfully.")
    else:
        print("index.html not found.")


if __name__ == "__main__":
    make_pwa()
