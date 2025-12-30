const CACHE_NAME = 'opic-portal-v1';
const ASSETS_TO_CACHE = [
    '/',
    '/static/css/modern-theme.css',
    '/static/manifest.json',
    '/static/icons/icon-192x192.png',
    '/static/galaxyAI.ico',
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap',
    'https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/js/bootstrap.bundle.min.js'
];

// Install Event: Cache Static Assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('[Service Worker] Caching static assets');
            return cache.addAll(ASSETS_TO_CACHE);
        })
    );
    self.skipWaiting();
});

// Activate Event: Cleanup Old Caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keyList) => {
            return Promise.all(
                keyList.map((key) => {
                    if (key !== CACHE_NAME) {
                        console.log('[Service Worker] Removing old cache', key);
                        return caches.delete(key);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

// Fetch Event: Network First for HTML, Cache First for Assets
self.addEventListener('fetch', (event) => {
    const requestUrl = new URL(event.request.url);

    // APIs: Network Only (Do not cache API responses logic here, or use StaleWhileRevalidate if needed)
    if (requestUrl.pathname.startsWith('/api/')) {
        return;
    }

    // HTML Pages: Network First -> Cache Fallback -> Offline Page
    if (event.request.mode === 'navigate') {
        event.respondWith(
            fetch(event.request)
                .then((response) => {
                    return caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, response.clone());
                        return response;
                    });
                })
                .catch(() => {
                    return caches.match(event.request).then((response) => {
                        if (response) return response;
                        // Ideally return an /offline.html here
                        return caches.match('/');
                    });
                })
        );
        return;
    }

    // Static Assets (CSS, JS, Images, Fonts): Cache First -> Network
    if (
        event.request.destination === 'style' ||
        event.request.destination === 'script' ||
        event.request.destination === 'image' ||
        event.request.destination === 'font'
    ) {
        event.respondWith(
            caches.match(event.request).then((response) => {
                return response || fetch(event.request).then((networkResponse) => {
                    return caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, networkResponse.clone());
                        return networkResponse;
                    });
                });
            })
        );
        return;
    }

    // Default: Network First
    event.respondWith(
        fetch(event.request).catch(() => caches.match(event.request))
    );
});
