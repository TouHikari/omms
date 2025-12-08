self.addEventListener('install', event => {
  event.waitUntil(
    caches.open('omms-static-v1').then(cache => cache.addAll(['/video.min.mp4', '/favicon.png']))
  )
})

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== 'omms-static-v1').map(k => caches.delete(k))))
  )
})

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url)
  if (url.pathname === '/video.min.mp4') {
    event.respondWith(
      caches.match(event.request).then(cached => {
        if (cached) return cached
        return fetch(event.request).then(res => {
          const clone = res.clone()
          caches.open('omms-static-v1').then(cache => cache.put(event.request, clone))
          return res
        })
      })
    )
  }
})