const CACHE_VERSION = 'evening-anchor-' + Date.now();
let CACHE_NAME;

const PRECACHE_ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icon-192.svg',
  './icon-512.svg'
];

// Install: always fetch fresh, then cache
self.addEventListener('install', e => {
  CACHE_NAME = CACHE_VERSION;
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache =>
      fetch('./index.html').then(r => {
        if (!r.ok) throw new Error('fetch failed');
        return cache.put('./index.html', r);
      })
    ).catch(() => {})  // offline install: use old cache
  );
  self.skipWaiting();
});

// Activate: delete ALL old caches on every update
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.map(k => {
        if (k !== CACHE_NAME) return caches.delete(k);
      }))
    ).then(() => self.clients.claim())
  );
});

// Fetch: NETWORK-FIRST for index.html (always get latest),
//        CACHE-FIRST for static assets (icons, manifest)
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (url.origin !== location.origin) return;

  // index.html: always try network first
  if (url.pathname === '/' || url.pathname === '/index.html') {
    e.respondWith(
      fetch(e.request).then(res => {
        const clone = res.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
        return res;
      }).catch(() => caches.match(e.request))
    );
    return;
  }

  // Static assets: cache-first
  e.respondWith(
    caches.match(e.request).then(r => r || fetch(e.request).then(res => {
      const clone = res.clone();
      caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
      return res;
    }))
  );
});