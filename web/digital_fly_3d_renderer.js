const BACKGROUND = '#0b0b0b';
const GRID = '#26313a';
const AXIS_X = '#d26a6a';
const AXIS_Y = '#78c091';
const AXIS_Z = '#6f9ee8';
const BONE = '#58c4dd';
const JOINT = '#f0b429';
const SELECTED = '#ffcc66';
const TEXT = '#d8dee5';

export class DigitalFly3DRenderer {
    constructor() {
        this.target = [0, 0, 0];
        this.distance = 6;
        this.showGround = true;
        this.showAxes = true;
        this.showJointAxes = true;
        this.showCOM = true;
        this.showTrajectory = true;
        this.showSkeleton = true;
        this.showBodySegments = true;
    }

    resetCamera() {
        this.target = [0, 0, 0];
        this.distance = 6;
    }

    focusSelectedNode(model, selectedNode) {
        const id = selectedNode?.id?.replace(/^flygym-/, '') ?? selectedNode?.name;
        const bone = model?.skeleton.bones.get(id) ?? model?.skeleton.bonesInOrder().find((item) => item.name === selectedNode?.name);
        if (bone) this.target = [...bone.worldTransform.translation];
    }

    render(context, width, height, model, camera = {}) {
        if (!context || !model) return;
        context.save();
        context.fillStyle = BACKGROUND;
        context.fillRect(0, 0, width, height);
        const projection = (point) => projectPoint(point, width, height, camera, this.target, this.distance);
        if (this.showGround) this.drawGround(context, width, height, projection);
        if (this.showAxes) this.drawAxes(context, width, height, projection);
        if (this.showTrajectory) this.drawTrajectory(context, width, height, projection, model);
        if (this.showSkeleton) this.drawSkeleton(context, projection, model, camera.selectedNode);
        if (this.showCOM) this.drawCOM(context, projection, model);
        this.drawLabel(context, width, model, camera.frame);
        context.restore();
    }

    drawGround(context, width, height, projection) {
        context.save();
        context.strokeStyle = GRID;
        context.lineWidth = 1;
        for (let value = -4; value <= 4; value += 0.5) {
            drawProjectedLine(context, projection, [[value, -1.1, -4], [value, -1.1, 4]]);
            drawProjectedLine(context, projection, [[-4, -1.1, value], [4, -1.1, value]]);
        }
        context.restore();
    }

    drawAxes(context, width, height, projection) {
        const origin = [0, -1.1, 0];
        drawProjectedLine(context, projection, [origin, [1.2, -1.1, 0]], AXIS_X, 2);
        drawProjectedLine(context, projection, [origin, [0, 0.1, 0]], AXIS_Y, 2);
        drawProjectedLine(context, projection, [origin, [0, -1.1, 1.2]], AXIS_Z, 2);
    }

    drawTrajectory(context, width, height, projection, model) {
        const records = model.fly.trajectories.list().filter((record) => ['thorax', 'com'].includes(record.metadata?.channel));
        records.forEach((record) => {
            const points = Array.from({ length: seriesLength(record.data) }, (_, frame) => sampleVector(record.data, frame)).filter(Boolean);
            if (points.length < 2) return;
            context.save();
            context.strokeStyle = '#708090';
            context.globalAlpha = 0.65;
            context.lineWidth = 1.5;
            context.beginPath();
            points.forEach((point, index) => {
                const screen = projection(point);
                if (!screen) return;
                if (index === 0) context.moveTo(screen.x, screen.y);
                else context.lineTo(screen.x, screen.y);
            });
            context.stroke();
            context.restore();
        });
    }

    drawSkeleton(context, projection, model, selectedNode) {
        const selectedId = selectedNode?.id?.replace(/^flygym-/, '') ?? selectedNode?.name;
        model.skeleton.bonesInOrder().forEach((bone) => {
            const start = projection(bone.worldTransform.translation);
            if (!start) return;
            bone.children.forEach((childId) => {
                const child = model.skeleton.bones.get(childId);
                const end = projection(child.worldTransform.translation);
                if (end) drawProjectedLine(context, projection, [bone.worldTransform.translation, child.worldTransform.translation], BONE, 2);
            });
            context.beginPath();
            context.arc(start.x, start.y, bone.id === selectedId ? 6 : 4, 0, Math.PI * 2);
            context.fillStyle = bone.id === selectedId ? SELECTED : JOINT;
            context.fill();
            if (this.showJointAxes) this.drawJointAxis(context, projection, bone);
        });
    }

    drawJointAxis(context, projection, bone) {
        const start = bone.worldTransform.translation;
        const direction = rotateVector(bone.worldTransform.quaternion, bone.joint.axis);
        drawProjectedLine(context, projection, [start, add(start, scale(direction, 0.18))], AXIS_Z, 1);
    }

    drawCOM(context, projection, model) {
        const position = model.lastFrameState?.com ?? model.skeleton.getBone('thorax').worldTransform.translation;
        const point = projection(position);
        if (!point) return;
        context.beginPath();
        context.arc(point.x, point.y, 5, 0, Math.PI * 2);
        context.strokeStyle = '#ffffff';
        context.lineWidth = 2;
        context.stroke();
    }

    drawLabel(context, width, model, frame) {
        context.fillStyle = TEXT;
        context.font = '12px sans-serif';
        context.textAlign = 'left';
        context.fillText(`Digital Fly 3D  |  frame ${frame ?? 0}`, 12, 18);
        context.textAlign = 'right';
        context.fillText(`${model.skeleton.bones.size} bones`, width - 12, 18);
    }
}

function projectPoint(point, width, height, camera, target, distance) {
    if (!Array.isArray(point) || point.length < 3 || point.some((value) => !Number.isFinite(Number(value)))) return null;
    const yaw = Number(camera.orbitYaw ?? 0.55);
    const pitch = Number(camera.orbitPitch ?? -0.35);
    const dx = Number(point[0]) - target[0];
    const dy = Number(point[1]) - target[1];
    const dz = Number(point[2]) - target[2];
    const cosYaw = Math.cos(yaw);
    const sinYaw = Math.sin(yaw);
    const x = cosYaw * dx + sinYaw * dz;
    const zYaw = -sinYaw * dx + cosYaw * dz;
    const cosPitch = Math.cos(pitch);
    const sinPitch = Math.sin(pitch);
    const y = cosPitch * dy - sinPitch * zYaw;
    const depth = distance + sinPitch * dy + cosPitch * zYaw;
    if (depth <= 0.05) return null;
    const scaleFactor = Math.min(width, height) * 0.42 * Number(camera.zoom ?? 1) / depth;
    return {
        x: width / 2 + Number(camera.offsetX ?? 0) + x * scaleFactor,
        y: height / 2 + Number(camera.offsetY ?? 0) - y * scaleFactor,
        depth,
    };
}

function drawProjectedLine(context, projection, points, color = GRID, width = 1) {
    const projected = points.map(projection);
    if (projected.some((point) => !point)) return;
    context.save();
    context.strokeStyle = color;
    context.lineWidth = width;
    context.beginPath();
    context.moveTo(projected[0].x, projected[0].y);
    projected.slice(1).forEach((point) => context.lineTo(point.x, point.y));
    context.stroke();
    context.restore();
}

function sampleVector(data, frame) {
    const values = Array.isArray(data) ? data : Array.isArray(data?.points) ? data.points : [];
    const value = values[Math.min(values.length - 1, frame)];
    if (Array.isArray(value) && value.length >= 3) return value.slice(0, 3).map(Number);
    if (value && typeof value === 'object') {
        const position = value.position ?? value.translation ?? value;
        if ([position.x, position.y, position.z].every((item) => Number.isFinite(Number(item)))) return [Number(position.x), Number(position.y), Number(position.z)];
    }
    return null;
}

function seriesLength(data) { return Array.isArray(data) ? data.length : Array.isArray(data?.points) ? data.points.length : 0; }
function rotateVector(quaternion, vector) { const [x, y, z, w] = quaternion; const q = [-x, -y, -z, w]; const p = [vector[0], vector[1], vector[2], 0]; return multiply(multiply(quaternion, p), q).slice(0, 3); }
function multiply(left, right) { const [x1, y1, z1, w1] = left; const [x2, y2, z2, w2] = right; return [w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2, w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2, w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2, w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2]; }
function add(left, right) { return left.map((value, index) => value + right[index]); }
function scale(value, factor) { return value.map((item) => item * factor); }
