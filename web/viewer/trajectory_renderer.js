/** Minimal canvas adapter for trajectory data supplied by the imported pose. */

export class TrajectoryRenderer {
    clear(context, canvas) {
        if (!context || !canvas) return;
        context.clearRect(0, 0, canvas.width, canvas.height);
    }

    render(context, canvas, trajectory, transform = {}) {
        if (!context || !canvas || !Array.isArray(trajectory) || trajectory.length < 2) return 0;
        const zoom = Number(transform.zoom) || 1;
        const offsetX = Number(transform.offsetX) || 0;
        const offsetY = Number(transform.offsetY) || 0;
        context.beginPath();
        trajectory.forEach((point, index) => {
            const x = Number(point?.[0]);
            const y = Number(point?.[1]);
            if (!Number.isFinite(x) || !Number.isFinite(y)) return;
            const px = canvas.width / 2 + (x + offsetX) * zoom;
            const py = canvas.height / 2 - (y + offsetY) * zoom;
            if (index === 0) context.moveTo(px, py);
            else context.lineTo(px, py);
        });
        context.stroke();
        return trajectory.length;
    }
}
