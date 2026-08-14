export class RolloutComparisonViewer {
    constructor() {
        this.container = null;
        this.comparison = null;
        this.currentFrame = 0;
    }

    render(container, comparison) {
        this.container = container;
        this.comparison = comparison;
        if (!container) return;
        const conditions = comparison?.conditions ?? [];
        container.innerHTML = `
            <section class="comparison-viewer" aria-label="Rollout comparison">
                <div class="comparison-toolbar">
                    <strong>Rollout Comparison</strong>
                    <span class="comparison-current-frame">Frame 0</span>
                </div>
                <div class="comparison-columns">
                    ${conditions.map((condition) => `
                        <article class="comparison-condition">
                            <h4>${escapeText(condition.label)}</h4>
                            <p>${condition.rollout?.frameCount ?? 0} frames</p>
                            <p>Speed: ${formatMetric(condition.statistics?.summary?.speed?.mean)}</p>
                            <p>Yaw rate: ${formatMetric(condition.statistics?.summary?.angularVelocity?.mean)}</p>
                        </article>
                    `).join('')}
                </div>
                <div class="comparison-differences">
                    ${(comparison?.differences ?? []).map((difference) => `
                        <div><strong>${escapeText(difference.label)}</strong> - error heatmap rows: ${difference.jointErrorHeatmap?.length ?? 0}</div>
                    `).join('')}
                </div>
            </section>
        `;
    }

    setFrame(frame) {
        this.currentFrame = Math.max(0, Math.round(Number(frame) || 0));
        const readout = this.container?.querySelector('.comparison-current-frame');
        if (readout) readout.textContent = `Frame ${this.currentFrame}`;
    }
}

function formatMetric(value) {
    return Number.isFinite(Number(value)) ? Number(value).toFixed(4) : 'n/a';
}

function escapeText(value) {
    return String(value).replace(/[&<>"']/g, (character) => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
    }[character]));
}

