# Assignment 3 – Third-Party API Integration

## Overview

A Flask REST service that integrates with the public
[JSONPlaceholder](https://jsonplaceholder.typicode.com/) API to expose
**Posts**, **Users**, and an enriched **User + Todo stats** endpoint.

The implementation demonstrates production-grade integration patterns:
- Automatic **retries with exponential back-off** (via `tenacity`)
- Per-request **timeouts** to prevent hanging connections
- Clean **error handling** — raw exceptions never leak to HTTP responses
- **Unit tests with fully mocked HTTP calls** (via `responses`)

---

## Project Structure

```
assignment-3/
├── main.py                          # App factory & dev-server entry point
├── config.py                        # Centralised configuration
├── requirements.txt                 # Python dependencies
├── pytest.ini                       # Test configuration
├── models/
│   └── schemas.py                   # Post, User, Todo dataclasses
├── services/
│   └── external_api_service.py      # HTTP client: retry, timeout, auth
├── routes/
│   ├── posts.py                     # /api/posts blueprint
│   └── users.py                     # /api/users blueprint
└── tests/
    ├── conftest.py                  # Shared fixtures & sample data
    ├── test_external_api_service.py # Unit tests for the HTTP client
    ├── test_posts_route.py          # Route tests for /api/posts
    └── test_users_route.py          # Route tests for /api/users
```

---


## Quick Start

```bash
# 1 – Install dependencies
pip install -r requirements.txt

# 2 – Set environment variables (optional, for production-style secrets)
# Example (Windows PowerShell):
$env:SECRET_KEY="your-secret-key"
$env:JSONPLACEHOLDER_API_KEY=""

# 3 – Run the server
python main.py
```

The server starts at `http://localhost:5000`.

---


## Configuration

This app uses environment variables to control its settings. An environment variable is a value you set outside the code, so you don't have to change the code to change how the app works.

For example, to set an environment variable in Windows PowerShell, you can use:

```powershell
$env:SECRET_KEY="your-secret-key"
```

If you don't set a variable, the app uses a safe default (except for `SECRET_KEY`, which you must set for security).

Here are the main environment variables you can use:

| Env Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | *(must set)* | Flask session signing key (required, no default) |
| `FLASK_DEBUG` | `False` | Enable Flask debug mode (shows errors in browser, not for production) |
| `JSONPLACEHOLDER_BASE_URL` | `https://jsonplaceholder.typicode.com` | External API root URL |
| `JSONPLACEHOLDER_API_KEY` | `""` | API key (empty — JSONPlaceholder is public) |
| `REQUEST_TIMEOUT_SECONDS` | `10` | Max seconds to wait for a response |
| `MAX_RETRY_ATTEMPTS` | `3` | How many times to retry on failure |
| `RETRY_WAIT_SECONDS` | `1` | Base wait between retries (doubles each attempt) |

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/posts/` | List all posts |
| GET | `/api/posts/<id>` | Get post by ID |
| GET | `/api/users/` | List all users |
| GET | `/api/users/<id>` | Get user by ID |
| GET | `/api/users/<id>/todos` | Get todos for a user |
| GET | `/api/users/<id>/enriched` | User + todo completion statistics |

### Sample Requests & Responses

#### `GET /api/posts/1`
```json
{
  "id": 1,
  "user_id": 1,
  "title": "sunt aut facere repellat provident occaecati",
  "body": "quia et suscipit\nsuscipit recusandae..."
}
```

#### `GET /api/users/1/enriched`
```json
{
  "user": {
    "id": 1,
    "name": "Leanne Graham",
    "username": "Bret",
    "email": "Sincere@april.biz",
    "phone": "1-770-736-8031 x56442",
    "website": "hildegard.org",
    "address": {
      "street": "Kulas Light",
      "suite": "Apt. 556",
      "city": "Gwenborough",
      "zipcode": "92998-3874"
    }
  },
  "todo_stats": {
    "total": 20,
    "completed": 11,
    "pending": 9,
    "completion_rate_pct": 55.0
  }
}
```

#### Error response (404)
```json
{ "error": "Resource not found: https://jsonplaceholder.typicode.com/posts/999" }
```

#### Error response (502 / gateway timeout)
```json
{ "error": "Max retries exceeded for https://jsonplaceholder.typicode.com/posts" }
```

---

## Integration Flow

```
Client
  │
  ▼
Flask Route  (routes/posts.py  |  routes/users.py)
  │  ← reads config from app.config (config.py)
  ▼
ExternalAPIService  (services/external_api_service.py)
  │  ← injects Bearer token if JSONPLACEHOLDER_API_KEY is set
  │  ← enforces REQUEST_TIMEOUT_SECONDS per call
  │  ← retries up to MAX_RETRY_ATTEMPTS on ConnectionError / 5xx
  │     with exponential back-off (base: RETRY_WAIT_SECONDS)
  ▼
JSONPlaceholder REST API  (https://jsonplaceholder.typicode.com)
  │
  ▼
Raw JSON  →  dataclass (Post / User / Todo)  →  JSON response to client
```

---

## Security Considerations

### 1 – API Key Management
- The `JSONPLACEHOLDER_API_KEY` is stored in `config.py`, not scattered across the codebase.
- JSONPlaceholder is a public API so the key is empty — but the pattern is in place for any API that requires authentication (e.g. Stripe, SendGrid).

### 2 – Authorization Header Injection
```python
if api_key:
    self._session.headers["Authorization"] = f"Bearer {api_key}"
```
- The header is only added when a key is present, preventing an empty
  `Bearer ` header from being sent to public endpoints.

### 3 – Timeout Enforcement
```python
response = self._session.get(url, timeout=self._timeout)
```
- Every outbound request has an explicit timeout (default: 10 s).
- Prevents hanging threads from exhausting the server's worker pool.

### 4 – Retry with Exponential Back-off
- Uses [tenacity](https://tenacity.readthedocs.io/) to retry on
  `ConnectionError`, `Timeout`, and HTTP 5xx responses.
- Exponential back-off avoids thundering-herd against a struggling upstream.
- `MAX_RETRY_ATTEMPTS` is configurable in `config.py`.

### 5 – Typed Error Propagation
- `ExternalAPIError` and `ExternalAPINotFoundError` wrap raw `requests`
  exceptions, ensuring internal implementation details never surface in
  HTTP responses.

### 6 – Test Isolation
- `TestingConfig` sets `JSONPLACEHOLDER_BASE_URL = "https://test.invalid"`.
- Any unmocked HTTP call in tests fails with a `ConnectionError` immediately
  rather than silently reaching production.

---

## Running Tests

```bash
pytest -v
```

**Result: 27 tests, all passing.**

| Test File | Tests | What it covers |
|---|---|---|
| `test_external_api_service.py` | 12 | HTTP client — happy path, 404, 500, retry logic, auth header |
| `test_posts_route.py` | 6 | `/api/posts/` and `/api/posts/<id>` routes |
| `test_users_route.py` | 9 | `/api/users/` routes including the enriched endpoint |

### How Mocking Works

All tests use the `responses` library — **no real network requests are made during testing**.

```python
@responses.activate
def test_returns_list_of_posts(self):
    responses.add(responses.GET, "https://test.invalid/posts",
                  json=[SAMPLE_POST], status=200)
    result = service.get_posts()
    assert result[0]["id"] == 1
```

`TestingConfig` points `JSONPLACEHOLDER_BASE_URL` to `https://test.invalid`. Any test that accidentally skips mocking fails immediately with a connection error.

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `Flask` | 3.1.0 | Web framework |
| `requests` | 2.32.3 | HTTP client |
| `tenacity` | 9.0.0 | Retry logic with back-off |
| `pytest` | 8.3.5 | Test runner |
| `pytest-flask` | 1.3.0 | Flask test utilities |
| `responses` | 0.25.3 | Mock HTTP calls in tests |

---

## GitHub Copilot Usage Notes


## How GitHub Copilot Helped

GitHub Copilot is an AI tool that suggests code and comments as you type. It helped make this project faster and easier to build. Here’s how Copilot was used in this project:

1. **Building the ExternalAPIService:**
  - Copilot wrote the code to connect to the external API, including the retry logic (using tenacity) and the helper function for making requests.
2. **Making Error Classes:**
  - Copilot generated the special error classes (`ExternalAPIError` and `ExternalAPINotFoundError`) so errors are handled in a clear way.
3. **Writing Test Mocks:**
  - Copilot suggested how to use `responses.activate` and `unittest.mock.patch` to fake API calls in tests, so no real network requests are made.
4. **Explaining Security:**
  - Copilot helped write the section about security, including code examples for how secrets and timeouts are handled safely.
