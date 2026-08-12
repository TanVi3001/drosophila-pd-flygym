from drosophila_pd.flystudio.asset_manager import AssetManager, Asset

def test_asset_manager():
    manager = AssetManager()
    asset = Asset(id="mesh1", type="mesh", uri="file://mesh.obj")
    manager.register_asset(asset)
    assert "mesh1" in manager.assets
    assert manager.assets["mesh1"].uri == "file://mesh.obj"
