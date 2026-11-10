"""
API integration tests (run against the real PostgreSQL database).

Every test creates its own customer and the fixture deletes it afterwards
(calls, follow-ups and predictions are removed by ON DELETE CASCADE),
so the loaded dataset is never modified.

Run from the project root:
    python -m pytest tests -v
"""
import uuid

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


@pytest.fixture()
def customer():
    payload = {
        "name": "Test Customer",
        "phone": "900000000",
        "email": f"test-{uuid.uuid4().hex[:8]}@example.com",
        "company": "Test Co",
        "age": 35,
        "status": "Active",
    }
    res = client.post("/customers/", json=payload)
    assert res.status_code == 201
    created = res.json()
    yield created
    client.delete(f"/customers/{created['id']}")


def register_call(customer_id: int, **overrides) -> dict:
    payload = {
        "customer_id": customer_id,
        "duration_seconds": 420,
        "outcome": "Interested",
        "interest": "High",
        "requested_info": True,
        "accepted_followup": True,
        "notes": "test call",
    }
    payload.update(overrides)
    res = client.post("/calls/", json=payload)
    assert res.status_code == 201, res.text
    return res.json()


def predict(customer: dict, call: dict, **overrides) -> dict:
    payload = {
        "customer_id": customer["id"],
        "call_id": call["id"],
        "duration_seconds": call["duration_seconds"],
        "outcome": call["outcome"],
        "interest": call["interest"],
        "requested_info": call["requested_info"],
        "accepted_followup": call["accepted_followup"],
        "age": customer["age"],
        "customer_status": customer["status"],
        "has_followup": call["accepted_followup"],
    }
    payload.update(overrides)
    res = client.post("/predictions/", json=payload)
    assert res.status_code == 201, res.text
    return res.json()


# ── Root ─────────────────────────────────────────────────────────
def test_health():
    assert client.get("/health").json() == {"status": "ok"}


# ── Customers ────────────────────────────────────────────────────
def test_customer_crud(customer):
    got = client.get(f"/customers/{customer['id']}")
    assert got.status_code == 200 and got.json()["name"] == "Test Customer"

    upd = client.put(f"/customers/{customer['id']}", json={"status": "VIP"})
    assert upd.status_code == 200 and upd.json()["status"] == "VIP"

    found = client.get("/customers/", params={"q": "Test Co"}).json()["items"]
    assert any(c["id"] == customer["id"] for c in found)


def test_customer_not_found():
    assert client.get("/customers/999999999").status_code == 404


# ── Call simulation ──────────────────────────────────────────────
def test_simulate_random_customer():
    res = client.post("/calls/simulate", json={})
    assert res.status_code == 200
    body = res.json()
    assert {"customer_id", "name", "phone", "company", "status", "age"} <= body.keys()


def test_simulate_specific_customer(customer):
    res = client.post("/calls/simulate", json={"customer_id": customer["id"]})
    assert res.status_code == 200 and res.json()["customer_id"] == customer["id"]


def test_simulate_unknown_customer():
    assert client.post("/calls/simulate", json={"customer_id": 999999999}).status_code == 404


# ── Calls ────────────────────────────────────────────────────────
def test_register_and_filter_calls(customer):
    call = register_call(customer["id"])
    assert call["customer_name"] == "Test Customer"

    by_customer = client.get("/calls/", params={"customer_id": customer["id"]}).json()["items"]
    assert [c["id"] for c in by_customer] == [call["id"]]

    assert client.get(f"/calls/{call['id']}").status_code == 200
    assert client.get("/calls/", params={"customer_id": customer["id"], "outcome": "Busy"}).json()["items"] == []


def test_call_rejects_negative_duration(customer):
    res = client.post("/calls/", json={
        "customer_id": customer["id"], "duration_seconds": -5, "outcome": "Busy",
    })
    assert res.status_code == 422


# ── Prediction + automatic follow-up (the core demo flow) ────────
def test_high_probability_creates_priority_followup(customer):
    call = register_call(customer["id"])
    pred = predict(customer, call)

    assert pred["classification"] == "High"
    assert pred["probability"] >= 0.65

    followups = client.get("/followups/", params={"customer_id": customer["id"]}).json()["items"]
    assert len(followups) == 1
    assert followups[0]["status"] == "Pending"
    assert followups[0]["call_id"] == call["id"]


def test_low_probability_creates_no_followup(customer):
    call = register_call(
        customer["id"], duration_seconds=30, outcome="Not interested", interest="No interest",
        requested_info=False, accepted_followup=False,
    )
    pred = predict(customer, call)

    assert pred["classification"] == "Low"
    assert pred["probability"] < 0.35
    assert client.get("/followups/", params={"customer_id": customer["id"]}).json()["items"] == []


def test_prediction_is_listed_for_customer(customer):
    call = register_call(customer["id"])
    predict(customer, call)
    listed = client.get("/predictions/", params={"customer_id": customer["id"]}).json()["items"]
    assert len(listed) == 1 and listed[0]["call_id"] == call["id"]


def test_prediction_with_unknown_category_does_not_crash(customer):
    call = register_call(customer["id"])
    pred = predict(customer, call, interest="Something new")
    assert 0 <= pred["probability"] <= 1


# ── Follow-ups ───────────────────────────────────────────────────
def test_followup_lifecycle(customer):
    res = client.post("/followups/", json={
        "customer_id": customer["id"], "scheduled_date": "2026-12-01",
        "reason": "Deal closing",
    })
    assert res.status_code == 201
    fid = res.json()["id"]
    assert res.json()["status"] == "Pending"

    got = client.get(f"/followups/{fid}")
    assert got.status_code == 200 and got.json()["id"] == fid

    done = client.put(f"/followups/{fid}", json={"status": "Completed"})
    assert done.status_code == 200 and done.json()["status"] == "Completed"

    pending = client.get("/followups/", params={"customer_id": customer["id"], "status": "Pending"}).json()["items"]
    assert pending == []


# ── Dashboard ────────────────────────────────────────────────────
def test_dashboard_metrics_change_after_a_call(customer):
    before = client.get("/dashboard/metrics").json()
    call = register_call(customer["id"])
    predict(customer, call)
    after = client.get("/dashboard/metrics").json()

    assert after["total_calls"] == before["total_calls"] + 1
    assert after["pending_followups"] == before["pending_followups"] + 1
    assert after["high_predictions"] == before["high_predictions"] + 1


@pytest.mark.parametrize("endpoint", [
    "pending-followups", "calls-per-day", "call-outcomes", "customers-by-status",
    "predictions-by-class", "probability-distribution", "priority-customers",
])
def test_dashboard_endpoints_return_lists(endpoint):
    res = client.get(f"/dashboard/{endpoint}")
    assert res.status_code == 200 and isinstance(res.json(), list)


def test_probability_distribution_has_ten_buckets():
    assert len(client.get("/dashboard/probability-distribution").json()) == 10


def test_followup_not_found():
    assert client.get("/followups/999999999").status_code == 404


# ── Server-side pagination ───────────────────────────────────────
@pytest.mark.parametrize("endpoint", ["/customers/", "/calls/", "/followups/", "/predictions/"])
def test_pagination_envelope_and_page_size(endpoint):
    body = client.get(endpoint, params={"page": 1, "page_size": 3}).json()
    assert set(body) == {"items", "total", "page", "page_size", "pages"}
    assert len(body["items"]) <= 3
    assert body["page"] == 1 and body["page_size"] == 3
    assert body["pages"] == max(1, -(-body["total"] // 3))


def test_pagination_pages_do_not_overlap():
    first = client.get("/customers/", params={"page": 1, "page_size": 5}).json()["items"]
    second = client.get("/customers/", params={"page": 2, "page_size": 5}).json()["items"]
    assert {c["id"] for c in first}.isdisjoint({c["id"] for c in second})


def test_pagination_sorting_and_whitelist():
    asc = client.get("/customers/", params={"sort_by": "age", "sort_dir": "asc", "page_size": 20}).json()["items"]
    ages = [c["age"] for c in asc if c["age"] is not None]
    assert ages == sorted(ages)

    # an unknown sort column must not break the query (falls back to the default)
    res = client.get("/customers/", params={"sort_by": "id; DROP TABLE customers", "page_size": 1})
    assert res.status_code == 200


def test_pagination_search_filters_total(customer):
    body = client.get("/customers/", params={"q": customer["email"]}).json()
    assert body["total"] == 1 and body["items"][0]["id"] == customer["id"]


def test_page_size_is_capped():
    assert client.get("/customers/", params={"page_size": 1000}).status_code == 422
    assert client.get("/customers/", params={"page": 0}).status_code == 422


def test_beyond_last_page_returns_empty_items():
    body = client.get("/customers/", params={"page": 999999, "page_size": 10}).json()
    assert body["items"] == [] and body["total"] > 0
