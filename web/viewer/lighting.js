import * as THREE from 'three';

export function addViewerLighting(scene) {
    const ambient = new THREE.AmbientLight(0x9fb3c5, 0.34);
    ambient.name = 'ambient-light';
    const hemisphere = new THREE.HemisphereLight(0xe5f4ff, 0x3b302d, 1.18);
    hemisphere.name = 'hemisphere-light';
    const key = new THREE.DirectionalLight(0xfff4e6, 2.7);
    key.position.set(5.5, 7.5, 7);
    key.name = 'key-light';
    key.castShadow = true;
    key.shadow.mapSize.width = 2048;
    key.shadow.mapSize.height = 2048;
    key.shadow.camera.near = 0.5;
    key.shadow.camera.far = 60;
    key.shadow.camera.left = -12;
    key.shadow.camera.right = 12;
    key.shadow.camera.top = 12;
    key.shadow.camera.bottom = -12;
    key.shadow.bias = -0.0001;
    key.shadow.normalBias = 0.018;
    key.shadow.radius = 4;
    const fill = new THREE.DirectionalLight(0x9bbcff, 0.58);
    fill.position.set(-5, 2, 3);
    fill.name = 'fill-light';
    const rim = new THREE.DirectionalLight(0xffc995, 0.42);
    rim.position.set(-3, 4, 6);
    rim.name = 'rim-light';
    scene.add(ambient, hemisphere, key, fill, rim);
    return { ambient, hemisphere, key, fill, rim };
}
