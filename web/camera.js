export class Camera {
    constructor() {
        this.target = "center";
        this.zoom = 1.0;
        this.presets = ["Top", "Side", "Front", "Free"];
    }

    setPreset(preset) {
        if (this.presets.includes(preset)) {
            console.log("Camera preset set to:", preset);
        }
    }
}
