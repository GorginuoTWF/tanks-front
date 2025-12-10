// Simple mock proxy server for frontend testing
// Usage: node dev-proxy.js
// Responds to POST /api/chat with a mocked chat completion JSON

const http = require('http');
const port = process.env.PORT || 3001;

const server = http.createServer((req, res) => {
  if (req.method === 'POST' && req.url === '/api/chat') {
    let body = '';
    req.on('data', (chunk) => (body += chunk));
    req.on('end', () => {
      try {
        const data = body ? JSON.parse(body) : {};
        const userMessage = data.messages?.[0]?.content || 'no content';

        console.log('[dev-proxy] /api/chat received:', userMessage);

        const reply = `Mock reply: I predict the winner based on name comparison. Received: ${userMessage}`;
        const resp = {
          choices: [
            {
              message: {
                content: reply
              }
            }
          ]
        };

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(resp));
      } catch (err) {
        console.error('[dev-proxy] error parsing request:', err);
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Server error', details: err.message }));
      }
    });
  } else {
    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Not found' }));
  }
});

server.listen(port, () => {
  console.log(`[dev-proxy] Mock chat proxy listening on http://localhost:${port}`);
});
