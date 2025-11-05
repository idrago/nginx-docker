#!/usr/bin/env python3
import sys
import json
from jinja2 import Template

template = Template(
"""
{%- for sld, items in (data | dictsort) %}
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
