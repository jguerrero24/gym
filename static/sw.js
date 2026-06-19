const CACHE = 'gymlog-v1';

const STATIC = [
  '/',
  '/index.html',
  '/manifest.json',
  '/icon.svg',
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(STATIC)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((ks) => Promise.all(ks.map((k) => { if (k !== CACHE) return caches.delete(k); })))
  );
});

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);

  // API calls: network only, no cache
  if (url.pathname.startsWith('/api/')) {
    return;
  }

  // Static assets: cache first, network fallback
  e.respondWith(
    caches.match(e.request).then((cached) => cached || fetch(e.request))
  );
});
