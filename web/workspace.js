export class Workspace {
    constructor() {
        this.data = {};
        this.selectedNode = null;
    }

    load(data = null) {
        if (data !== null) {
            this.data = data;
            this.selectedNode = null;
            console.log('Workspace updated.');
            return this.data;
        }

        console.log('Workspace loaded.');
        return this.data;
    }

    selectNode(node) {
        this.selectedNode = node || null;
        return this.selectedNode;
    }

    save() {
        console.log("Workspace saved.");
    }
}
