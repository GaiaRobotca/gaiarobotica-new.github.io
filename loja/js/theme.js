try { document.documentElement.dataset.theme = localStorage.getItem('gaia-theme') || (matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark'); } catch {}
