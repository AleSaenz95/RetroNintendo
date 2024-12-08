const CACHE_NAME = "RetroNintendo-cache-v1";
const urlsToCache = ["/", "/index.html", "/css/styles.css", "/js/app.js", "/static/media/icon-192x192.png"];

// Instalar el Service Worker y cachear recursos
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log("Archivos cacheados");
      return cache.addAll(urlsToCache);
    })
  );
});

// Interceptar solicitudes y responder desde la caché
self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});

// Actualizar la caché
self.addEventListener("activate", (event) => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then((cacheNames) =>
      Promise.all(
        cacheNames.map((cacheName) => {
          if (!cacheWhitelist.includes(cacheName)) {
            return caches.delete(cacheName);
          }
        })
      )
    )
  );
});
