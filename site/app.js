const label = document.querySelector('#deployment');
fetch('./deployment.json', { cache: 'no-store' }).then(response => {
  if (!response.ok) throw new Error('Metadata unavailable');
  return response.json();
}).then(({ sha, date }) => {
  if (!/^[a-f0-9]{40}$/.test(sha ?? '') || !date || !Number.isFinite(Date.parse(date))) return;
  label.textContent = `Content revision ${sha.slice(0, 12)} · deployed ${new Date(date).toISOString()}`;
}).catch(() => { /* Keep the honest static fallback when metadata is unavailable. */ });
