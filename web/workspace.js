export class Workspace {
    constructor() {
        this.data = {};
    }

    load(data = null) {
        if (data !== null) {
            this.data = data;
            console.log('Workspace updated.');
            return this.data;
        }

        console.log('Workspace loaded.');
        return this.data;
    }

    save() {
        console.log("Workspace saved.");
    }
}
