from pathlib import Path


ROOT = Path(__file__).parents[1]
WEB = ROOT / "web"


def test_experiment_workspace_modules_are_present_and_export_core_api():
    required = {
        "experiment_workspace.js": ["ExperimentManager", "DatasetManager", "ComparisonWorkspace", "SnapshotStore", "LayoutManager", "PluginRegistry"],
        "experiment_analytics.js": ["buildAnalyticsDashboard", "AnalyticsDashboard"],
        "experiment_reports.js": ["ExperimentReportGenerator", "toMarkdown", "toHTML", "toCSV"],
        "experiment_comparison.js": ["ExperimentComparisonModel", "buildComparisonReport"],
        "experiment_workspace_panel.js": ["ExperimentWorkspacePanel", "Import rollout"],
    }
    for filename, markers in required.items():
        text = (WEB / filename).read_text(encoding="utf-8")
        assert all(marker in text for marker in markers), filename


def test_experiment_workspace_keeps_computational_scope_explicit():
    for filename in ("experiment_analytics.js", "experiment_reports.js"):
        text = (WEB / filename).read_text(encoding="utf-8")
        assert "no biological" in text.lower()


def test_app_wires_manager_dashboard_and_persistence():
    text = (WEB / "app.js").read_text(encoding="utf-8")
    assert "ExperimentWorkspace" in text
    assert "AnalyticsDashboard" in text
    assert "ExperimentReportGenerator" in text
    assert "renderExperimentWorkspace" in text
