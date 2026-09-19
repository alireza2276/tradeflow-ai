# TradeFlowAI Load Test

Run from the project root while the backend is running at `http://127.0.0.1:8000`:

```powershell
python performance\run_load_test.py
```

Enter an existing TradeFlowAI username/password when prompted. The script logs in once, probes accessible endpoints, and then performs GET-only authenticated load. It does not create, edit, approve, settle, or delete business records.

Default stages: 10, 50, 100, 250, 500, 1000 concurrent workers, 15 seconds each. It automatically stops escalation if error rate exceeds 20% or p95 exceeds 10 seconds.

The report is written to `performance/load_test_report.json`.

Important: results against Django `runserver` are useful for finding application/query bottlenecks, but are not production capacity numbers.
