from output_generation.abstract_progress_bar import AbstractProgressBar


class ProgressBarCli(AbstractProgressBar):

    def __init__(self):
        super().__init__()

    def _phase_changed(self, phase: str):
        print("phase ended", phase)

    def _progress_changed(self, phase: str, progress: float):
        print("Progress changed", phase, progress)

    def close(self):
        pass
