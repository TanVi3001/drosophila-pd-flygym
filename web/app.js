import { Viewer } from './viewer.js';
import { Timeline } from './timeline.js';
import { Sidebar } from './sidebar.js';
import { Toolbar } from './toolbar.js';
import { Workspace } from './workspace.js';
import { Layout } from './layout.js';

export class App {
    constructor() {
        this.workspace = new Workspace();
        this.layout = new Layout();
        this.viewer = new Viewer();
        this.timeline = new Timeline();
        this.sidebar = new Sidebar();
        this.toolbar = new Toolbar();
    }

    init() {
        console.log("Fly Studio Web Platform initializing...");
        this.workspace.load();
        this.viewer.init(document.getElementById('viewer'));
        this.timeline.init(document.getElementById('timeline'));
        this.sidebar.init(document.getElementById('sidebar'));
        this.toolbar.init(document.getElementById('toolbar'));

        this.setupKeyboardShortcuts();
    }

    setupKeyboardShortcuts() {
        window.addEventListener('keydown', (e) => {
            if (e.code === 'Space') {
                this.timeline.togglePlayback();
            }
        });
    }
}
