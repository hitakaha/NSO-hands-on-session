{# Story 6.3 — print-site cover; context: config (MkDocs), page (print page). #}
<div class="pdf-cover">
  <div class="pdf-cover__classification" role="status">Cisco Confidential</div>
  {% if config.site_name %}
  <h1 class="pdf-cover__title">{{ config.site_name }}</h1>
  {% endif %}
  <p class="pdf-cover__meta">
    <strong>Presenter</strong> David Quezada Rivero
  </p>
  <p class="pdf-cover__meta">
    <strong>Team</strong> Internet and Mass Scale Infrastructure
  </p>
  {% if config.extra and config.extra.pdf_build_date %}
  <p class="pdf-cover__meta pdf-cover__meta--date">
    <strong>Date: </strong> {{ config.extra.pdf_build_date }}
  </p>
  {% endif %}
</div>
