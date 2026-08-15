from .conftest import assert_no_runtime_errors, load_real_pose


def test_real_viewer_pose_loads(page):
    load_real_pose(page)
    assert page.locator(".three-viewer-canvas").is_visible()
    assert page.locator(".three-viewer-timeline").is_visible()
    assert "Frame 0" in page.locator(".three-viewer-timeline").inner_text()
    assert_no_runtime_errors(page)
