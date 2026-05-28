// Black World News — Service Worker
// Caches the shell and recently-visited pages so the app works offline.
// Bumps CACHE_NAME whenever we want the user's browser to fetch fresh files.

const CACHE_NAME = "bwn-v4";

// Core shell — pages we want available even with no internet.
const SHELL = [
    "/",
    "/index.html",
    "/about.html",
    "/search.html",
    "/manifest.json",
    "/logo.svg",
    "/favicon.svg",
    "/icons/icon-192.png",
    "/icons/icon-512.png",
    "/icons/apple-touch-icon.png"
];

// Install — pre-cache the shell
self.addEventListener("install", event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(SHELL))
    );
    self.skipWaiting();
});

// Activate — clean up old caches
self.addEventListener("activate", event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(
                keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
            )
        )
    );
    self.clients.claim();
});

// Fetch — network first, fall back to cache when offline
self.addEventListener("fetch", event => {
    const req = event.request;

    // Only handle GET requests from our own origin
    if (req.method !== "GET") return;
    if (new URL(req.url).origin !== location.origin) return;

    event.respondWith(
        fetch(req)
            .then(res => {
                // Cache a copy of every successful page response for offline
                if (res.ok && (res.type === "basic" || res.type === "default")) {
                    const copy = res.clone();
                    caches.open(CACHE_NAME).then(cache => cache.put(req, copy));
                }
                return res;
            })
            .catch(() => caches.match(req).then(hit => hit || caches.match("/index.html")))
    );
});
