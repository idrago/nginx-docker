#!/usr/bin/env python3
import sys
import json
from jinja2 import Template

template = Template("""
{%- for u in upstreams %}
upstream {{ u.name }} {
    server {{ u.ip }}:{{ u.port }};
}

{%- if not loop.last %}

{%- endif %}
{% endfor %}

""".lstrip())

def main():
	if len(sys.argv) != 3:
		print(f"Usage: {sys.argv[0]} <input.json> <output.conf>", file=sys.stderr)
		sys.exit(1)

	in_json, out_conf = sys.argv[1], sys.argv[2]

	with open(in_json) as f:
		data = json.load(f)

	upstreams = [
		{
			"name": str(x["name"]).strip(),
			"ip": str(x["ip"]).strip(),
			"port": str(x["port"]).strip(),
		}
		for x in data
	]

	rendered = template.render(upstreams=upstreams)

	with open(out_conf, "w") as f:
			f.write(rendered)

if __name__ == "__main__":
    main()
