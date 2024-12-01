const CACHE_NAME = "retronintendo-cache-v1";
const urlsToCache = [
    "/",
    "/static/css/estilos.css",
    "/static/media/classic-games.jpg",
    "/static/media/worldwide-shipping.jpg",
    "/static/media/welcome.jpg",
    "/static/media/icon-192x192.png",
    "/static/media/icon-512x512.png"
];

// Instalación del Service Worker
self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(urlsToCache);
        })
    );
});

// Activación del Service Worker
self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cache) => {
                    if (cache !== CACHE_NAME) {
                        return caches.delete(cache);
                    }
                })
            );
        })
    );
});

// Intercepción de solicitudes
self.addEventListener("fetch", (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request);
        })
    );
});
