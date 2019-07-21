import abc


class AbstractProgressBar(object, metaclass=abc.ABCMeta):
    def __init__(self):
        self.__phase = ""
        self.__progress = 0

    def update(self, phase: str, progress: float):
        if phase != self.__phase:
            self._phase_changed(phase)

        if self.__progress != progress:
            self._progress_changed(phase, progress)

        self.__phase = phase
        self.__progress = progress

    def update_progress(self, progress: float):
        if self.__progress != progress:
            self._progress_changed(self.__phase, progress)

        self.__progress = progress

    @abc.abstractmethod
    def _phase_changed(self, phase: str):
        pass

    @abc.abstractmethod
    def _progress_changed(self, phase: str, progress: float):
        pass

    @abc.abstractmethod
    def close(self):
        pass
