import * as THREE from 'three';

export function addViewerLighting(scene) {
    const hemisphere = new THREE.HemisphereLight(0xcfe8ff, 0x172027, 1.8);
    hemisphere.name = 'hemisphere-light';
    const key = new THREE.DirectionalLight(0xffffff, 2.2);
    key.position.set(4, 7, 5);
    key.name = 'key-light';
    const fill = new THREE.DirectionalLight(0x78a8ff, 0.7);
    fill.position.set(-4, 2, -3);
    fill.name = 'fill-light';
    scene.add(hemisphere, key, fill);
    return { hemisphere, key, fill };
}
