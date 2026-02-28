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