// CommonJS mock proxy for frontend testing
// Usage: node dev-proxy.cjs
const http = require('http');
const port = process.env.PORT || 3001;

const server = http.createServer((req, res) => {
  if (req.method === 'POST' && req.url === '/api/chat') {
    let body = '';
    req.on('data', (chunk) => (body += chunk));
    req.on('end', () => {
      try {
        const data = body ? JSON.parse(body) : {};
        const userMessage = data.messages && data.messages[0] && data.messages[0].content ? data.messages[0].content : 'no content';
        console.log('[dev-proxy.cjs] /api/chat received:', userMessage);

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
        console.error('[dev-proxy.cjs] error parsing request:', err);
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
  console.log(`[dev-proxy.cjs] Mock chat proxy listening on http://localhost:${port}`);
});
