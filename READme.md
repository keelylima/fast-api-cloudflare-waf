# 🔐 Cloudflare WAF Governance API

> ⚠️ Work in Progress  
> This project is under active development. Features and structure may evolve.

Internal tool designed to manage, export, and organize Cloudflare WAF rules in a structured and scalable way.

The goal is to provide governance, visibility, and operational control over custom and managed rulesets across Cloudflare zones.

---

## 🎯 Purpose

Managing WAF rules directly in the Cloudflare console becomes complex when:

- Multiple zones exist
- Rule order impacts behavior
- Naming standards are not consistently followed
- There is no centralized visibility
- Teams need structured exports for analysis

This API provides a structured backend abstraction layer over the Cloudflare Rulesets API.

---

## 🚀 Current Features

### 📌 1. List Zones
```
GET /cloudflare/zones
```
Returns all accessible zones for the configured account token.

---

### 📌 2. List Rulesets by Zone
```
GET /cloudflare/rulesets/{zone_id}
```
Returns all rulesets associated with a zone.

---

### 📌 3. Get Ruleset Details
```
GET /cloudflare/rulesets/{zone_id}/{ruleset_id}
```
Returns full ruleset definition including rules.

---

### 📌 4. Create Ruleset
```
POST /cloudflare/rulesets/{zone_id}
```
Creates a new custom ruleset in the `http_request_firewall_custom` phase.

---

### 📌 5. Delete Ruleset
```
DELETE /cloudflare/rulesets/{zone_id}/{ruleset_id}
```
Removes an existing ruleset.

---

### 📌 6. Add Rule to Ruleset
```
PATCH /cloudflare/rulesets/{zone_id}/{ruleset_id}/rules
```
Supports:
- `block`
- `skip`

Includes validation logic:
- `skip` requires `action_parameters`
- `block` cannot include `action_parameters`

---

### 📌 7. Delete Rule
```
DELETE /cloudflare/rulesets/{zone_id}/{ruleset_id}/rules/{rule_id}
```
Removes a specific rule from a ruleset.

---

### 📌 8. Reorder Rule
```
PATCH /cloudflare/rulesets/{zone_id}/{ruleset_id}/rules/{rule_id}/reorder
```
Supports Cloudflare positioning logic:
- `before`
- `after`
- `index`

Only one position field allowed per request.

---

### 📌 9. Export Rules by Zone (Governance Endpoint)
```
GET /cloudflare/rules/export/{zone_id}?kind=zone
```
Returns a structured inventory of rules including:
- zone_name
- zone_id
- ruleset_id
- rule_id
- description
- action
- expression
- enabled
- index (execution order inside ruleset)

Query parameter:

| Param | Values | Description |
|-------|--------|-------------|
| kind  | zone / managed / all | Filters ruleset type |

Default behavior: `zone` (custom rules only).

---

## 🧠 Architectural Design

The project follows a layered structure:
```
app/
├── routes/ # API layer
├── services/ # Business logic & Cloudflare integration
├── schemas/ # Request/response validation models
├── core/ # Configuration
└── main.py # Application entrypoint
```


Separation of concerns ensures:

- Maintainability
- Scalability
- Testability
- Clear ownership of responsibilities

---

## 🔐 Authentication

Requires Cloudflare API Token via environment variable:

export CLOUDFLARE_API_TOKEN=your_token_here


Recommended permissions:

- Zone: Read
- Account WAF: Write

---

## 📈 Future Improvements (Roadmap)

- Rule naming validation (regex enforcement)
- Governance reports (block vs skip distribution)
- Diff between environments (QA vs PROD)
- Pagination support for large zones
- Performance optimization with parallel requests
- Rule audit metadata (BU / squad / context tagging)
- Export in CSV or JSON file format

---

## 🛠 Tech Stack

- FastAPI
- Pydantic
- httpx (async)
- Cloudflare Rulesets API

---

## 📌 Disclaimer

This tool is intended for internal governance and operational automation.  
Use with caution in production environments, especially when modifying rule order.

---

## 👩‍💻 Author
keelylima
