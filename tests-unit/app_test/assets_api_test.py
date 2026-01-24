"""Tests for Assets API endpoints (app/assets/api/routes.py)

Tests cover:
- Schema validation for query parameters and request bodies
"""

import pytest
from pydantic import ValidationError

from app.assets.api import schemas_in, schemas_out


class TestListAssetsQuery:
    """Tests for ListAssetsQuery schema."""

    def test_defaults(self):
        """Test default values."""
        q = schemas_in.ListAssetsQuery()
        assert q.include_tags == []
        assert q.exclude_tags == []
        assert q.limit == 20
        assert q.offset == 0
        assert q.sort == "created_at"
        assert q.order == "desc"
        assert q.include_public == True

    def test_include_public_false(self):
        """Test include_public can be set to False."""
        q = schemas_in.ListAssetsQuery(include_public=False)
        assert q.include_public == False

    def test_csv_tags_parsing(self):
        """Test comma-separated tags are parsed correctly."""
        q = schemas_in.ListAssetsQuery.model_validate({"include_tags": "a,b,c"})
        assert q.include_tags == ["a", "b", "c"]

    def test_metadata_filter_json_string(self):
        """Test metadata_filter accepts JSON string."""
        q = schemas_in.ListAssetsQuery.model_validate({"metadata_filter": '{"key": "value"}'})
        assert q.metadata_filter == {"key": "value"}


class TestTagsListQuery:
    """Tests for TagsListQuery schema."""

    def test_defaults(self):
        """Test default values."""
        q = schemas_in.TagsListQuery()
        assert q.prefix is None
        assert q.limit == 100
        assert q.offset == 0
        assert q.order == "count_desc"
        assert q.include_zero == True
        assert q.include_public == True

    def test_include_public_false(self):
        """Test include_public can be set to False."""
        q = schemas_in.TagsListQuery(include_public=False)
        assert q.include_public == False


class TestUpdateAssetBody:
    """Tests for UpdateAssetBody schema."""

    def test_requires_at_least_one_field(self):
        """Test that at least one field is required."""
        with pytest.raises(ValidationError):
            schemas_in.UpdateAssetBody()

    def test_name_only(self):
        """Test updating name only."""
        body = schemas_in.UpdateAssetBody(name="new name")
        assert body.name == "new name"
        assert body.mime_type is None
        assert body.preview_id is None

    def test_mime_type_only(self):
        """Test updating mime_type only."""
        body = schemas_in.UpdateAssetBody(mime_type="image/png")
        assert body.mime_type == "image/png"

    def test_preview_id_only(self):
        """Test updating preview_id only."""
        body = schemas_in.UpdateAssetBody(preview_id="550e8400-e29b-41d4-a716-446655440000")
        assert body.preview_id == "550e8400-e29b-41d4-a716-446655440000"

    def test_preview_id_invalid_uuid(self):
        """Test invalid UUID for preview_id."""
        with pytest.raises(ValidationError):
            schemas_in.UpdateAssetBody(preview_id="not-a-uuid")

    def test_all_fields(self):
        """Test all fields together."""
        body = schemas_in.UpdateAssetBody(
            name="test",
            mime_type="application/json",
            preview_id="550e8400-e29b-41d4-a716-446655440000",
            user_metadata={"key": "value"}
        )
        assert body.name == "test"
        assert body.mime_type == "application/json"


class TestUploadAssetFromUrlBody:
    """Tests for UploadAssetFromUrlBody schema (JSON URL upload)."""

    def test_valid_url(self):
        """Test valid HTTP URL."""
        body = schemas_in.UploadAssetFromUrlBody(
            url="https://example.com/model.safetensors",
            name="model.safetensors"
        )
        assert body.url == "https://example.com/model.safetensors"
        assert body.name == "model.safetensors"

    def test_http_url(self):
        """Test HTTP URL (not just HTTPS)."""
        body = schemas_in.UploadAssetFromUrlBody(
            url="http://example.com/file.bin",
            name="file.bin"
        )
        assert body.url == "http://example.com/file.bin"

    def test_invalid_url_scheme(self):
        """Test invalid URL scheme raises error."""
        with pytest.raises(ValidationError):
            schemas_in.UploadAssetFromUrlBody(
                url="ftp://example.com/file.bin",
                name="file.bin"
            )

    def test_tags_normalized(self):
        """Test tags are normalized to lowercase."""
        body = schemas_in.UploadAssetFromUrlBody(
            url="https://example.com/model.safetensors",
            name="model",
            tags=["Models", "LORAS"]
        )
        assert body.tags == ["models", "loras"]


class TestTagsRefineQuery:
    """Tests for TagsRefineQuery schema."""

    def test_defaults(self):
        """Test default values."""
        q = schemas_in.TagsRefineQuery()
        assert q.include_tags == []
        assert q.exclude_tags == []
        assert q.limit == 100
        assert q.include_public == True

    def test_include_public_false(self):
        """Test include_public can be set to False."""
        q = schemas_in.TagsRefineQuery(include_public=False)
        assert q.include_public == False


class TestTagHistogramResponse:
    """Tests for TagHistogramResponse schema."""

    def test_empty_response(self):
        """Test empty response."""
        resp = schemas_out.TagHistogramResponse()
        assert resp.tags == []

    def test_with_entries(self):
        """Test response with entries."""
        resp = schemas_out.TagHistogramResponse(
            tags=[
                schemas_out.TagHistogramEntry(name="models", count=10),
                schemas_out.TagHistogramEntry(name="loras", count=5),
            ]
        )
        assert len(resp.tags) == 2
        assert resp.tags[0].name == "models"
        assert resp.tags[0].count == 10
