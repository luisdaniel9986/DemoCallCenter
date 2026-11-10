"""
export_postman.py
=================
Generates docs/call_center.postman_collection.json (Postman v2.1).
Requests follow the demo flow. Test scripts store ids in collection variables,
so the whole collection can be run top to bottom with the Collection Runner.

Usage (from the project root):
    python docs/export_postman.py
"""
import json
import os

OUT = os.path.join(os.path.dirname(__file__), "call_center.postman_collection.json")


def req(name, method, path, body=None, tests=None):
    item = {
        "name": name,
        "request": {
            "method": method,
            "header": [{"key": "Content-Type", "value": "application/json"}],
            "url": {"raw": "{{baseUrl}}" + path, "host": ["{{baseUrl}}"], "path": path.lstrip("/").split("?")[0].split("/")},
        },
    }
    if "?" in path:
        query = path.split("?", 1)[1]
        item["request"]["url"]["query"] = [
            {"key": k, "value": v} for k, v in (q.split("=", 1) for q in query.split("&"))
        ]
    if body is not None:
        item["request"]["body"] = {"mode": "raw", "raw": json.dumps(body, indent=2)}
    if tests:
        item["event"] = [{"listen": "test", "script": {"type": "text/javascript", "exec": tests}}]
    return item


def status_test(code):
    return [f'pm.test("Status {code}", () => pm.response.to.have.status({code}));']


call_body = {
    "customer_id": "{{customerId}}", "duration_seconds": 420, "outcome": "Interested",
    "interest": "High", "requested_info": True, "accepted_followup": True, "notes": "Postman test call",
}
prediction_body = {
    "customer_id": "{{customerId}}", "call_id": "{{callId}}", "duration_seconds": 420,
    "outcome": "Interested", "interest": "High", "requested_info": True, "accepted_followup": True,
    "age": 35, "customer_status": "Active", "has_followup": True,
}

collection = {
    "info": {
        "name": "Call Center CRM API",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
    },
    "variable": [
        {"key": "baseUrl", "value": "http://localhost:8000"},
        {"key": "customerId", "value": ""},
        {"key": "callId", "value": ""},
    ],
    "item": [
        {"name": "0. Health", "item": [req("Health", "GET", "/health", tests=status_test(200))]},
        {"name": "1. Customers", "item": [
            req("List customers (search)", "GET", "/customers/?q=tech&page=1&page_size=5&sort_by=name&sort_dir=asc", tests=status_test(200)),
            req("Create customer", "POST", "/customers/", {
                "name": "Postman Customer", "phone": "900111222", "email": "postman@example.com",
                "company": "Postman Co", "age": 35, "status": "Active",
            }, tests=status_test(201) + ['pm.collectionVariables.set("customerId", pm.response.json().id);']),
            req("Get customer", "GET", "/customers/{{customerId}}", tests=status_test(200)),
            req("Update customer", "PUT", "/customers/{{customerId}}", {"status": "VIP"}, tests=status_test(200)),
        ]},
        {"name": "2. Call (demo flow)", "item": [
            req("Simulate incoming call", "POST", "/calls/simulate", {}, tests=status_test(200)),
            req("Register call", "POST", "/calls/", call_body,
                tests=status_test(201) + ['pm.collectionVariables.set("callId", pm.response.json().id);']),
            req("List calls of customer", "GET", "/calls/?customer_id={{customerId}}", tests=status_test(200)),
        ]},
        {"name": "3. ML prediction + automatic follow-up", "item": [
            req("Predict (creates follow-up if High/Medium)", "POST", "/predictions/", prediction_body,
                tests=status_test(201) + [
                    'pm.test("Has classification", () => pm.expect(["High","Medium","Low"]).to.include(pm.response.json().classification));',
                ]),
            req("Predictions of customer", "GET", "/predictions/?customer_id={{customerId}}", tests=status_test(200)),
            req("Follow-ups of customer", "GET", "/followups/?customer_id={{customerId}}", tests=status_test(200)),
        ]},
        {"name": "4. Dashboard", "item": [
            req(name, "GET", f"/dashboard/{path}", tests=status_test(200))
            for name, path in [
                ("Metrics", "metrics"), ("Pending follow-ups", "pending-followups"),
                ("Calls per day", "calls-per-day"), ("Call outcomes", "call-outcomes"),
                ("Customers by status", "customers-by-status"), ("Predictions by class", "predictions-by-class"),
                ("Probability distribution", "probability-distribution"), ("Priority customers", "priority-customers"),
            ]
        ]},
        {"name": "5. Cleanup", "item": [
            req("Delete test customer (cascades calls, follow-ups, predictions)", "DELETE",
                "/customers/{{customerId}}", tests=status_test(204)),
        ]},
    ],
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(collection, f, indent=2, ensure_ascii=False)
print(f"Saved {OUT}")
