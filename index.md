---
---
## Used Cars

{{page.latest-ucd}}
{% for item in site.data.used.{{page.latest-ucd}} %}
***\[{{item.state}}\]***
**{{item.manufacturer}}** {{item.name}}
**Cr. {{item.cr}}**


{% endfor %}

## Legend Cars

{{page.latest-legend}}
{% for item in site.data.legend.{{page.latest-legend}} %}
***\[{{item.state}}\]***
**{{item.manufacturer}}** {{item.name}}
**Cr. {{item.cr}}**


{% endfor %}

## Menu Book Rewards

Coming soon!

## Menu Book Used Cars

Coming soon!