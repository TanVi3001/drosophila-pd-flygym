import { Timeline } from './timeline.js';
import { Sidebar } from './sidebar.js';
import { Toolbar } from './toolbar.js';
import { Workspace } from './workspace.js';
import { Layout } from './layout.js';
import { JSONLoader } from './json_loader.js';
import { Inspector } from './inspector.js';
import { ViewportRenderer } from './viewport_renderer.js';

export class App {
    constructor() {
        this.workspace = new Workspace();
        this.layout = new Layout();
        this.viewportRenderer = new ViewportRenderer(this.workspace);
        this.timeline = new Timeline();
        this.sidebar = new Sidebar({ onSelectNode: (node) => this.selectNode(node) });
        this.inspector = new Inspector(this.workspace);
        this.toolbar = new Toolbar({
            onLoadJSON: (file) => this.loadSceneFile(file),
            onResetView: () => this.viewportRenderer.resetView(),
        });
    }

    init() {
        console.log("Fly Studio Web Platform initializing...");
        this.workspace.load();
        this.viewportRenderer.init(document.getElementById('viewer'));
        this.timeline.init(document.getElementById('timeline'));
        this.sidebar.init(document.getElementById('sidebar'));
        this.inspector.init(document.getElementById('inspector'));
        this.toolbar.init(document.getElementById('toolbar'));

        this.setupKeyboardShortcuts();
    }

    async loadSceneFile(file) {
        try {
            const data = await JSONLoader.parseFile(file);
            const summary = JSONLoader.summarizeScene(data);

            // Commit the new state only after parsing and validation succeed.
            this.workspace.load(data);
            this.sidebar.render(this.workspace.data, this.workspace.selectedNode);
            this.inspector.render();
            this.viewportRenderer.render();

            console.info('Loaded scene', file.name);
            console.info('Node count:', summary.nodeCount);
            console.info('Camera count:', summary.cameraCount);
            console.info('Trajectory count:', summary.trajectoryCount);
        } catch (error) {
            console.error('Failed to load scene JSON:', error);
            window.alert(`Unable to load scene JSON: ${error.message}`);
        }
    }

    selectNode(node) {
        this.workspace.selectNode(node);
        this.sidebar.render(this.workspace.data, this.workspace.selectedNode);
        this.inspector.render();
        this.viewportRenderer.render();
        console.info('Selected node:', node.name ?? node.id ?? node.type ?? node.kind ?? 'Unnamed node');
    }

    setupKeyboardShortcuts() {
        window.addEventListener('keydown', (e) => {
            if (e.code !== 'Space' || e.repeat) return;
            e.preventDefault();
        });
        window.addEventListener('keyup', (e) => {
            if (e.code !== 'Space') return;
            if (!this.viewportRenderer.consumeSpacePan()) {
                this.timeline.togglePlayback();
            }
        });
    }
}
