---
---
## Used Cars

_Last updated string: {{page.latest-ucd}} (YY-MM-DD-hhmm)_

{% for item in site.data.used[page.latest-ucd] %}
***\[{{item.state}}\]***
**{{item.manufacturer}}** {{item.name}}
    {% assign crlength = item.cr.size | append: "" | size %}
    crlength {{crlength}}
    {% if crlength <= 3 %}
**Cr. {{item.cr}}**
    {% elsif crlength <= 6 %}
**Cr. {{item.cr | divided_by: 1000}},{{item.cr | modulo: 1000}}**
    {% else %}
**Cr. {{item.cr | divided_by: 1000000}},{{item.cr | divided_by: 1000 | modulo: 1000}},{{item.cr | modulo: 1000}}**
    {% endif %}


{% endfor %}

## Legend Cars

_Last updated string: {{page.latest-legend}} (YY-MM-DD-hhmm)_

{% for item in site.data.legend[page.latest-legend] %}
***\[{{item.state}}\]***
**{{item.manufacturer}}** {{item.name}}
    {% assign crlength = item.cr.size | append: "" | size %}
    crlength {{crlength}}
    {% if crlength <= 3 %}
**Cr. {{item.cr}}**
    {% elsif crlength <= 6 %}
**Cr. {{item.cr | divided_by: 1000}},{{item.cr | modulo: 1000}}**
    {% else %}
**Cr. {{item.cr | divided_by: 1000000}},{{item.cr | divided_by: 1000 | modulo: 1000}},{{item.cr | modulo: 1000}}**
    {% endif %}


{% endfor %}

## Menu Book Rewards

Coming soon!

## Menu Book Used Cars

Coming soon!