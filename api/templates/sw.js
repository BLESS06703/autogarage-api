// AutoGarage Pro Service Worker
const CACHE_NAME = 'autogarage-v2';
const ASSETS = [
    '/api/auth/login-page/',
    '/api/dashboard-page/',
    '/api/offline/',
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS);
        })
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        fetch(event.request)
            .then((response) => {
                // Cache successful responses
                const clone = response.clone();
                caches.open(CACHE_NAME).then((cache) => {
                    cache.put(event.request, clone);
                });
                return response;
            })
            .catch(() => {
                // Return cached version or offline page
                return caches.match(event.request)
                    .then((cached) => cached || caches.match('/api/offline/'));
            })
    );
});
