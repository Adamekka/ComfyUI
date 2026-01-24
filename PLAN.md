# Plan: Align Local Asset/Tag Endpoints with Cloud

## Endpoint Comparison

| Endpoint | Cloud (openapi.yaml) | Local (routes.py) |
|----------|---------------------|-------------------|
| `GET /api/assets` | ✅ + `include_public` param | ✅ |
| `POST /api/assets` | ✅ multipart + JSON URL upload | ✅ multipart only |
| `GET /api/assets/{id}` | ✅ | ✅ |
| `PUT /api/assets/{id}` | ✅ (`name`, `mime_type`, `preview_id`, `user_metadata`) | ✅ (`name`, `tags`, `user_metadata`) |
| `DELETE /api/assets/{id}` | ✅ | ✅ |
| `GET /api/assets/{id}/content` | ❌ | ✅ |
| `POST /api/assets/{id}/tags` | ✅ | ✅ |
| `DELETE /api/assets/{id}/tags` | ✅ | ✅ |
| `PUT /api/assets/{id}/preview` | ❌ | ✅ |
| `POST /api/assets/from-hash` | ✅ | ✅ |
| `HEAD /api/assets/hash/{hash}` | ✅ | ✅ |
| `GET /api/assets/remote-metadata` | ✅ | ❌ |
| `POST /api/assets/download` | ✅ (background download) | ❌ |
| `GET /api/assets/tags/refine` | ✅ (tag histogram) | ❌ |
| `GET /api/tags` | ✅ + `include_public` param | ✅ |
| `POST /api/assets/scan/seed` | ❌ | ✅ (local only) |

---

## Phase 1: Add Missing Cloud Endpoints to Local

### 1.1 `GET /api/assets/remote-metadata` *(deferred)*
Fetch metadata from remote URLs (CivitAI, HuggingFace) without downloading the file.

**Status:** Not supported yet. Add stub/placeholder that returns 501 Not Implemented.

**Parameters:**
- `url` (required): Download URL to retrieve metadata from

**Returns:** Asset metadata (name, size, hash if available, etc.)

### 1.2 `POST /api/assets/download` *(deferred)*
Initiate background download job for large files from HuggingFace or CivitAI.

**Status:** Not supported yet. Add stub/placeholder that returns 501 Not Implemented.

**Request body:**
- `source_url` (required): URL to download from
- `tags`: Optional tags for the asset
- `user_metadata`: Optional metadata
- `preview_id`: Optional preview asset ID

**Returns:**
- 200 if file already exists (returns asset immediately)
- 202 with `task_id` for background download tracking via `GET /api/tasks/{task_id}`

### 1.3 `GET /api/assets/tags/refine`
Get tag histogram for filtered assets (useful for search refinement UI).

**Parameters:**
- `include_tags`: Filter assets with ALL these tags
- `exclude_tags`: Exclude assets with ANY of these tags
- `name_contains`: Filter by name substring
- `metadata_filter`: JSON filter for metadata fields
- `limit`: Max tags to return (default 100)
- `include_public`: Include public/shared assets

**Returns:** List of tags with counts for matching assets

---

## Phase 2: Update Existing Endpoints for Parity

### 2.1 `GET /api/assets`
- Add `include_public` query parameter (boolean, default true)

### 2.2 `POST /api/assets`
- Add JSON body upload path for URL-based uploads:
  ```json
  {
    "url": "https://...",
    "name": "model.safetensors",
    "tags": ["models", "checkpoints"],
    "user_metadata": {},
    "preview_id": "uuid"
  }
  ```
- Keep existing multipart upload support

### 2.3 `PUT /api/assets/{id}`
- Add `mime_type` field support
- Add `preview_id` field support
- Remove direct `tags` field (recommend using dedicated `POST/DELETE /api/assets/{id}/tags` endpoints instead)

### 2.4 `GET /api/tags`
- Add `include_public` query parameter (boolean, default true)

---

## Phase 3: Local-Only Endpoints

These endpoints exist locally but not in cloud.

### 3.1 `GET /api/assets/{id}/content`
Download asset file content. Cloud uses signed URLs instead. **Keep for local.**

### 3.2 `PUT /api/assets/{id}/preview`
**Remove this endpoint.** Merge functionality into `PUT /api/assets/{id}` by adding `preview_id` field support (aligns with cloud).

### 3.3 `POST /api/assets/scan/seed`
Filesystem seeding/scanning for local asset discovery. Not applicable to cloud. **Keep as local-only.**

---

## Phase 4: Testing

Add tests for all new and modified endpoints to ensure functionality matches cloud behavior.

### 4.1 New Endpoint Tests
- `GET /api/assets/remote-metadata` – Test with valid/invalid URLs, various sources (CivitAI, HuggingFace)
- `POST /api/assets/download` – Test background download initiation, existing file detection, task tracking
- `GET /api/assets/tags/refine` – Test histogram generation with various filter combinations

### 4.2 Updated Endpoint Tests
- `GET /api/assets` – Test `include_public` param filtering
- `POST /api/assets` – Test JSON URL upload path alongside existing multipart tests
- `PUT /api/assets/{id}` – Test `mime_type` and `preview_id` field updates
- `GET /api/tags` – Test `include_public` param filtering

### 4.3 Removed Endpoint Tests
- Remove tests for `PUT /api/assets/{id}/preview`
- Add tests for `preview_id` in `PUT /api/assets/{id}` to cover the merged functionality

---

## Implementation Order

1. Phase 2.1, 2.4 – Add `include_public` params (low effort, high compatibility)
2. Phase 2.3 – Update PUT endpoint fields + remove preview endpoint
3. Phase 2.2 – Add JSON URL upload to POST
4. Phase 1.3 – Add tags/refine endpoint
5. Phase 1.1, 1.2 – Add stub endpoints returning 501 (deferred implementation)
6. Phase 4 – Add tests for each phase as implemented
