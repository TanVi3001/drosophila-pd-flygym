"""Drosophila PD FlyGym computational research package."""

from importlib.metadata import PackageNotFoundError, version


try:
    __version__ = version("drosophila-pd-flygym")
except PackageNotFoundError:  # Source checkouts before editable installation.
    __version__ = "0+unknown"

from .automation import (  # noqa: E402
    ArtifactManager,
    BenchmarkCenter,
    DatasetCatalog,
    DatasetCatalogEntry,
    DeveloperToolkit,
    ExperimentQueueManager,
    ProjectHealthMonitor,
    PublicationBuilder,
    ReproducibilityCenter,
    ResearchAutomationPlatform,
)
from .digital_twin_platform import (  # noqa: E402
    CollaborationLayer,
    DigitalTwinManager,
    DigitalTwinPlatform,
    DigitalTwinRecord,
    KnowledgeGraph,
    ScenarioRecord,
    ScenarioWorkspace,
    StateDiff,
    StateDiffEngine,
    TemporalExplorer,
    TwinAnnotation,
    VirtualLaboratorySession,
)
from .research_campaign import (  # noqa: E402
    CampaignEvent as ResearchCampaignEvent,
    CampaignHistory as ResearchCampaignHistory,
    CampaignManager as ResearchCampaignManager,
    CampaignManifest as ResearchCampaignManifest,
    CampaignState as ResearchCampaignState,
    ExperimentSpec as ResearchExperimentSpec,
)

__all__ = [
    "__version__",
    "ArtifactManager",
    "BenchmarkCenter",
    "DatasetCatalog",
    "DatasetCatalogEntry",
    "DeveloperToolkit",
    "ExperimentQueueManager",
    "ProjectHealthMonitor",
    "PublicationBuilder",
    "ReproducibilityCenter",
    "ResearchAutomationPlatform",
    "CollaborationLayer",
    "DigitalTwinManager",
    "DigitalTwinPlatform",
    "DigitalTwinRecord",
    "KnowledgeGraph",
    "ScenarioRecord",
    "ScenarioWorkspace",
    "StateDiff",
    "StateDiffEngine",
    "TemporalExplorer",
    "TwinAnnotation",
    "VirtualLaboratorySession",
    "ResearchCampaignEvent",
    "ResearchCampaignHistory",
    "ResearchCampaignManager",
    "ResearchCampaignManifest",
    "ResearchCampaignState",
    "ResearchExperimentSpec",
]
