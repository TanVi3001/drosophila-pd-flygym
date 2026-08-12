export class Timeline {
    constructor() {
        this.container = null;
        this.isPlaying = false;
        this.currentTime = 0;
    }

    init(container) {
        this.container = container;
        this.render();
    }

    render() {
        if (!this.container) return;
        this.container.innerHTML = `
            <div style="padding: 10px; color: var(--text-primary);">
                Timeline: ${this.currentTime.toFixed(2)}s |
                ${this.isPlaying ? 'Playing' : 'Paused'}
            </div>
        `;
    }

    togglePlayback() {
        this.isPlaying = !this.isPlaying;
        this.render();
    }
}
