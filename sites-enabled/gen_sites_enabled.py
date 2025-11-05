#!/usr/bin/env python3
import sys
import json
from jinja2 import Template

template = Template(
"""
# ===========================================
# Default server - routes based on IP address
# ===========================================

# Map destination IP to backend
map $server_addr $backend_host {
    # poli-worker-01-a
    130.192.166.200  poli-worker-01-a;
    130.192.166.201  poli-worker-01-a;
    130.192.166.202  poli-worker-01-a;
    130.192.166.203  poli-worker-01-a;
    
    # poli-worker-01-b
    130.192.166.204  poli-worker-01-b;
    130.192.166.205  poli-worker-01-b;
    130.192.166.206  poli-worker-01-b;
    130.192.166.207  poli-worker-01-b;
    
    # poli-worker-01-c
    130.192.166.208  poli-worker-01-c;
    130.192.166.209  poli-worker-01-c;
    130.192.166.210  poli-worker-01-c;
    130.192.166.211  poli-worker-01-c;
    
    # poli-worker-01-d
    130.192.166.212  poli-worker-01-d;
    130.192.166.213  poli-worker-01-d;
    130.192.166.214  poli-worker-01-d;
    130.192.166.215  poli-worker-01-d;
    
    # Default fallback
    default          poli-worker-01-a;
}

# ===========================================
# HTTP server - ACME challenge and redirect
# ===========================================
server {
    listen 80;
    server_name www0.idrago.org www1.idrago.org www2.idrago.org www3.idrago.org;

    # ACME challenge location for Let's Encrypt
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

# ===========================================
# Default HTTPS server
# ===========================================
server {
    listen 443 ssl default_server;
    server_name _;
    
    # Let's Encrypt certificate
    ssl_certificate /etc/letsencrypt/live/idrago.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/idrago.org/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    access_log /var/log/nginx/default-access.log detailed;
    error_log /var/log/nginx/default-error.log warn;
    
    location / {
        proxy_pass http://$backend_host;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Request-ID $request_id;
    }
}

{% for sld, items in (data | dictsort) %}
# ===========================================
# {{ sld }} hosts
# ===========================================

{%- for it in (items | sort(attribute='thld')) %}
{% set b = {'name': it.name, 'thld': it.thld, 'sld': sld} %}
{%- if b.name.startswith('hp-') %}
# {{ b.thld }}.{{ b.sld }} (hp) -> poli-worker-01-d
{%- elif b.name.startswith('real-') %}
# {{ b.thld }}.{{ b.sld }} (real) -> poli-worker-01-c
{%- elif b.name.startswith('agent-') %}
# {{ b.thld }}.{{ b.sld }} (agent) -> poli-worker-01-a
{%- elif b.name.startswith('dummy-') %}
# {{ b.thld }}.{{ b.sld }} (dummy) -> poli-worker-01-b
{%- endif %}
server {
  listen 443 ssl;
  server_name {{ b.thld }}.{{ b.sld }};

  access_log /var/log/nginx/{{ b.sld }}/{{ b.thld }}-access.log detailed;
  access_log /var/log/nginx/{{ b.sld }}/{{ b.thld }}-access.json.log json_detailed;
  error_log /var/log/nginx/{{ b.sld }}/{{ b.thld }}-error.log warn;

  location / {
    proxy_pass http://{{ b.name }};
    {%- if b.name.startswith('hp-') %}
    proxy_set_header Host {{ b.thld }}.local;
    {%- else %}
    proxy_set_header Host $host;
    {%- endif %}
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Request-ID $request_id;
    }
}
{%- if not loop.last %}

{%- endif %}
{%- endfor %}
{% endfor %}
""".lstrip()
)

def main():
	if len(sys.argv) != 3:
		print(f"Usage: {sys.argv[0]} <input.json> <output.conf>", file=sys.stderr)
		sys.exit(1)

	in_json, out_conf = sys.argv[1], sys.argv[2]

	with open(in_json) as f:
		data = json.load(f)

	rendered = template.render(data=data)

	with open(out_conf, "w") as f:
		f.write(rendered)


if __name__ == "__main__":
  main()
