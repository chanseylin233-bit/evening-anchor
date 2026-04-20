const CACHE_NAME = 'evening-anchor-v3';

const PRECACHE_ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icon-192.svg',
  './icon-512.svg'
];

// Install: precache the app shell.
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(PRECACHE_ASSETS))
      .catch(() => {}) // offline install: keep any existing cache
  );
  self.skipWaiting();
});

// Activate: delete old Evening Anchor caches on update.
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.map(k => {
        if (k.startsWith('evening-anchor-') && k !== CACHE_NAME) return caches.delete(k);
        return undefined;
      }))
    ).then(() => self.clients.claim())
  );
});

// Fetch: NETWORK-FIRST for index.html (always get latest),
//        CACHE-FIRST for static assets (icons, manifest).
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (url.origin !== location.origin) return;

  if (url.pathname === '/' || url.pathname.endsWith('/index.html')) {
    e.respondWith(
      fetch(e.request).then(res => {
        const clone = res.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
        return res;
      }).catch(() => caches.match(e.request).then(res => res || caches.match('./index.html')))
    );
    return;
  }

  e.respondWith(
    caches.match(e.request).then(r => r || fetch(e.request).then(res => {
      const clone = res.clone();
      caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
      return res;
    }))
  );
});
