/**
 * Cloudflare Worker for REDLINE API Proxy
 * Routes API requests to backend service (Render/Railway)
 * Handles CORS and request forwarding
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const backendUrl = env.BACKEND_URL || 'https://redline-xxxx.onrender.com';
    
    // Handle CORS preflight requests
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-License-Key',
          'Access-Control-Max-Age': '86400',
        },
      });
    }
    
    // Proxy API requests to backend
    const apiPaths = [
      '/api/',
      '/data/',
      '/payments/',
      '/download/',
      '/analysis/',
      '/converter/',
      '/settings/',
      '/tasks/',
      '/api-keys/',
      '/user-data/',
      '/health',
      '/status',
      '/register',
    ];
    
    const shouldProxy = apiPaths.some(path => url.pathname.startsWith(path));
    
    if (shouldProxy) {
      try {
        // Forward request to backend
        const backendRequest = new Request(
          `${backendUrl}${url.pathname}${url.search}`,
          {
            method: request.method,
            headers: request.headers,
            body: request.body,
          }
        );
        
        // Remove host header to avoid issues
        backendRequest.headers.delete('host');
        
        const response = await fetch(backendRequest);
        
        // Clone response to modify headers
        const newResponse = new Response(response.body, {
          status: response.status,
          statusText: response.statusText,
          headers: response.headers,
        });
        
        // Add CORS headers
        newResponse.headers.set('Access-Control-Allow-Origin', '*');
        newResponse.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
        newResponse.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-License-Key');
        
        return newResponse;
      } catch (error) {
        return new Response(
          JSON.stringify({ error: 'Backend service unavailable', message: error.message }),
          {
            status: 503,
            headers: {
              'Content-Type': 'application/json',
              'Access-Control-Allow-Origin': '*',
            },
          }
        );
      }
    }
    
    // For static assets, return 404 (handled by Cloudflare Pages)
    return new Response('Not Found', { status: 404 });
  },
};

