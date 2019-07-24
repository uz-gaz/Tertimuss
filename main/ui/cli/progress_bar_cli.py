from main.ui.common.AbstractProgressBar import AbstractProgressBar
from progress.bar import Bar


class ProgressBarCli(AbstractProgressBar):
    def __init__(self):
        super().__init__()
        self.bar = None

    def _phase_changed(self, phase: str):
        if self.bar is not None:
            self.bar.finish()

        self.bar = Bar(phase, max=100)
        self.progress = 0

    def _progress_changed(self, phase: str, progress: float):
        self.bar.next(int(progress) - self.progress)
        self.progress = int(progress)

    def close(self):
        self.bar.finish()
