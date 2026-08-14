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


def test_parkinson_analytics_engine_contract_is_additive_and_scoped():
    required = {
        "parkinson_features.js": ["extractFeatureBundle", "FeatureCache", "trajectoryCurvature", "jointAcceleration"],
        "parkinson_segmentation.js": ["Walking", "Turning", "Standing", "Grooming", "Unknown"],
        "parkinson_statistics.js": ["median", "variance", "percentiles", "histogram"],
        "parkinson_comparison.js": ["difference", "correlation", "similarity", "distance", "ranking"],
        "parkinson_score.js": ["weightedFeatures", "not a diagnosis", "confidence"],
        "parkinson_visualization.js": ["trajectorySVG", "matrixSVG", "renderCanvas"],
        "parkinson_export.js": ["toJSON", "toCSV", "toMarkdown", "toHTML", "toSVG", "exportPNG"],
        "parkinson_engine.js": ["ParkinsonAnalyticsEngine", "getFeatures", "getStatistics", "getSegmentation"],
    }
    for filename, markers in required.items():
        text = (WEB / filename).read_text(encoding="utf-8")
        assert all(marker.lower() in text.lower() for marker in markers), filename


def test_frozen_scientific_paths_are_not_part_of_milestone_changes():
    import subprocess

    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1"],
        capture_output=True,
        text=True,
        check=False,
    )
    changed = set(result.stdout.splitlines()) if result.returncode == 0 else set()
    assert not any(path.startswith(("results/", "notebooks/", "docs/report/")) for path in changed)


def test_analysis_pipeline_backend_contract():
    required = {
        "analysis_graph.js": ["FeatureGraph", "evaluateAll", "cycle detected"],
        "analysis_normalization.js": ["global", "rollout", "experiment", "joint", "bodyPart"],
        "analysis_quality.js": ["NON_FINITE_VALUES", "DUPLICATE_FRAMES", "BROKEN_TRAJECTORY"],
        "analysis_outliers.js": ["iqr", "zscore", "mad"],
        "analysis_matrix.js": ["correlationMatrix", "similarityMatrix", "distanceMatrix"],
        "analysis_cache.js": ["feature", "metric", "comparison"],
        "analysis_pipeline.js": ["AnalysisPipeline", "analyzeBatch", "parallelReady", "PipelineReport"],
    }
    for filename, markers in required.items():
        text = (WEB / filename).read_text(encoding="utf-8")
        assert all(marker.lower() in text.lower() for marker in markers), filename


def test_statistical_engine_backend_contract():
    required = {
        "statistical_descriptive.js": ["mean", "median", "variance", "quartile", "percentiles", "distribution"],
        "statistical_resampling.js": ["bootstrap", "confidenceLevel", "jackknife"],
        "statistical_tests.js": ["welch-t-test", "mann-whitney", "wilcoxon", "ks", "permutation"],
        "statistical_effects.js": ["cohensD", "glassDelta", "cliffsDelta", "rankBiserial"],
        "statistical_corrections.js": ["bonferroni", "holm", "benjamini-hochberg", "falseDiscoveryRate"],
        "statistical_correlation.js": ["pearson", "spearman", "kendall", "partialCorrelation"],
        "statistical_regression.js": ["linearRegression", "polynomialRegression", "robustRegression", "residualAnalysis"],
        "statistical_validation.js": ["normality", "varianceEquality", "missingData", "outlierSensitivity"],
        "statistical_engine.js": ["StatisticalEngine", "compare", "report", "benchmark"],
        "statistical_report.js": ["toJSON", "toMarkdown", "toHTML", "toCSV"],
    }
    for filename, markers in required.items():
        text = (WEB / filename).read_text(encoding="utf-8")
        assert all(marker.lower() in text.lower() for marker in markers), filename
