import random
from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
import time

class RotateUserAgentMiddleware:
    """Rotate user agents to avoid detection"""
    
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    def process_request(self, request, spider):
        request.headers['User-Agent'] = random.choice(self.user_agents)
        request.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        request.headers['Accept-Language'] = 'en-US,en;q=0.5'
        request.headers['Accept-Encoding'] = 'gzip, deflate'
        request.headers['DNT'] = '1'
        request.headers['Connection'] = 'keep-alive'
        request.headers['Upgrade-Insecure-Requests'] = '1'

class RandomDelayMiddleware:
    """Add random delays between requests"""
    
    def process_request(self, request, spider):
        delay = random.uniform(1, 3)
        time.sleep(delay)
        return None

class CustomRetryMiddleware(RetryMiddleware):
    """Custom retry with exponential backoff"""
    
    def process_response(self, request, response, spider):
        if response.status in [403, 429]:
            reason = response_status_message(response.status)
            time.sleep(random.uniform(5, 10))
            return self._retry(request, reason, spider) or response
        return response