import { Timeline } from './timeline.js';
import { Sidebar } from './sidebar.js';
import { Toolbar } from './toolbar.js';
import { Workspace } from './workspace.js';
import { Layout } from './layout.js';
import { JSONLoader } from './json_loader.js';
import { Inspector } from './inspector.js';
import { ViewportRenderer } from './viewport_renderer.js';
import { PlaybackController } from './playback_controller.js';

export class App {
    constructor() {
        this.workspace = new Workspace();
        this.layout = new Layout();
        this.viewportRenderer = new ViewportRenderer(this.workspace);
        this.timeline = new Timeline(this.workspace, () => this.handleTimelineChange());
        this.sidebar = new Sidebar({ onSelectNode: (node) => this.selectNode(node) });
        this.inspector = new Inspector(this.workspace, () => this.handleInspectorChange());
        this.playbackController = new PlaybackController(this.workspace);
        this.toolbar = new Toolbar({
            onLoadJSON: (file) => this.loadSceneFile(file),
            onResetView: () => this.viewportRenderer.resetView(),
            onUndo: () => this.undo(),
            onRedo: () => this.redo(),
            onInsert: () => this.insertKeyframe(),
            onDuplicate: () => this.duplicateKeyframes(),
            onDelete: () => this.deleteKeyframes(),
            onFramePrevious: () => this.nudgeSelectedKeyframe(-1),
            onFrameNext: () => this.nudgeSelectedKeyframe(1),
        });
        this.keyDownHandler = (event) => this.handleKeyDown(event);
    }

    init() {
        console.log("Fly Studio Web Platform initializing...");
        this.workspace.load();
        this.viewportRenderer.init(document.getElementById('viewer'));
        this.timeline.init(document.getElementById('timeline'));
        this.sidebar.init(document.getElementById('sidebar'));
        this.inspector.init(document.getElementById('inspector'));
        this.toolbar.init(document.getElementById('toolbar'));
        window.addEventListener('keydown', this.keyDownHandler);

    }

    async loadSceneFile(file) {
        try {
            const data = await JSONLoader.parseFile(file);
            const summary = JSONLoader.summarizeScene(data);

            // Commit the new state only after parsing and validation succeed.
            this.workspace.load(data);
            this.timeline.render();
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

    handleTimelineChange() {
        this.inspector.render();
        this.viewportRenderer.render();
    }

    handleInspectorChange() {
        this.timeline.render();
        this.inspector.render();
        this.viewportRenderer.render();
    }

    insertKeyframe() {
        this.runEdit(() => this.workspace.insertKeyframe());
    }

    duplicateKeyframes() {
        this.runEdit(() => this.workspace.duplicateSelectedKeyframes());
    }

    deleteKeyframes() {
        this.runEdit(() => this.workspace.deleteSelectedKeyframes());
    }

    nudgeSelectedKeyframe(delta) {
        const frame = this.workspace.selectedKeyframe?.frame;
        if (!Number.isInteger(frame)) return;
        this.runEdit(() => this.workspace.moveSelectedKeyframe(frame + delta));
    }

    undo() {
        if (this.workspace.undo()) this.refreshEditor();
    }

    redo() {
        if (this.workspace.redo()) this.refreshEditor();
    }

    runEdit(operation) {
        const result = operation();
        if (result?.updated) this.refreshEditor();
        return result;
    }

    refreshEditor() {
        this.timeline.render();
        this.inspector.render();
        this.viewportRenderer.render();
    }

    handleKeyDown(event) {
        if (event.isComposing) return;
        const target = event.target;
        const editingText = target && (
            target.tagName === 'INPUT' || target.tagName === 'TEXTAREA'
        );
        if (editingText) return;

        const modifier = event.ctrlKey || event.metaKey;
        if (modifier && event.shiftKey && event.key.toLowerCase() === 'z') {
            event.preventDefault();
            this.redo();
        } else if (modifier && event.key.toLowerCase() === 'z') {
            event.preventDefault();
            this.undo();
        } else if (modifier && event.key.toLowerCase() === 'd') {
            event.preventDefault();
            this.duplicateKeyframes();
        } else if (modifier && event.key.toLowerCase() === 'c') {
            event.preventDefault();
            this.workspace.copySelectedKeyframes();
        } else if (modifier && event.key.toLowerCase() === 'v') {
            event.preventDefault();
            this.runEdit(() => this.workspace.pasteKeyframes());
        } else if (!modifier && event.key === 'Delete') {
            event.preventDefault();
            this.deleteKeyframes();
        } else if (!modifier && event.key === 'Escape') {
            this.workspace.clearKeyframeSelection();
            this.refreshEditor();
        } else if (!modifier && event.key.toLowerCase() === 'a' && !editingText) {
            event.preventDefault();
            this.workspace.selectAllKeyframes();
            this.refreshEditor();
        } else if (!modifier && event.key.toLowerCase() === 'f' && !editingText) {
            event.preventDefault();
            this.viewportRenderer.resetView();
        }
    }

}
