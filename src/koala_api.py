import requests
import json
import os

blog_type = 'blog_post'

headers = {
    'Authorization': f"Bearer {os.environ.get('KOALA_API_KEY')}",
    'Content-Type': 'application/json',
}
body = {
    "articleType": blog_type,

}
