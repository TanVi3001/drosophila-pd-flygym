export const PLAYBACK_STATES = Object.freeze({
    STOPPED: 'Stopped',
    PAUSED: 'Paused',
    PLAYING: 'Playing',
});

export class PlaybackController {
    constructor(workspace) {
        this.workspace = workspace;
        if (!Object.values(PLAYBACK_STATES).includes(this.workspace.playbackState)) {
            this.workspace.playbackState = PLAYBACK_STATES.STOPPED;
        }
    }

    play() {
        return this.setState(PLAYBACK_STATES.PLAYING);
    }

    pause() {
        return this.setState(PLAYBACK_STATES.PAUSED);
    }

    stop() {
        return this.setState(PLAYBACK_STATES.STOPPED);
    }

    resume() {
        return this.setState(PLAYBACK_STATES.PLAYING);
    }

    setState(state) {
        this.workspace.playbackState = state;
        return this.workspace.playbackState;
    }
}
