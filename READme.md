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


## 🆕 IP Lists (Account-Level Governance)

### 📌 10. List Account IP Lists
```
GET /cloudflare/ip-lists/{account_id}/ip-lists
```

Returns all IP Lists for a given Cloudflare account.
Includes metadata such as:
- id
- name
- description
- kind
- num_items
- num_referencing_filters
- created_on
- modified_on

---

### 📌 11. Create IP List
```
POST /cloudflare/ip-lists/{account_id}/ip-lists
```
Creates a new IP List of type ip.

Request Body
```
{
  "name": "list_name",
  "description": "optional description"
}
```

Notes
Cloudflare Free plan allows only one IP list per account.
Attempting to create additional lists may return an error.
The list is created at the account level, not zone level.

---

### 📌 12. Delete IP List
```
DELETE /cloudflare/ip-lists/{account_id}/ip-lists/{list_id}
```
Deletes an existing IP List.

Notes
Deletion will fail if the list is referenced by active rules.
Ensure the list is not in use before deletion.

---

### 📌 13. List IP List Items
```
GET /cloudflare/ip-lists/{account_id}/ip-lists/{list_id}/items
```
Returns all IP entries within a specific IP List.
Each item includes:
- id
- ip
- comment
- created_on

---

📌 14. Add IP(s) to IP List
```
POST /cloudflare/ip-lists/{account_id}/ip-lists/{list_id}/items
```
Adds one or multiple IP addresses to a list.
Request Body (Bulk Supported)
```
[
  {
    "ip": "1.1.1.1",
    "comment": "cloudflare dns"
  },
  {
    "ip": "8.8.8.8",
    "comment": "google dns"
  }
]
```

Response
Cloudflare processes additions asynchronously and returns:
```
{
  "operation_id": "..."
}
```

The operation_id can be used to track processing status via the Cloudflare API.

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
- Account Filter Lists: Write

---

## 📈 Future Improvements (Roadmap)

- Rule naming validation (regex enforcement)
- Governance reports (block vs skip distribution)
- Diff between environments (QA vs PROD)
- Pagination support for large zones

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
