from abc import abstractmethod
from typing import Protocol


class Extractor(Protocol):
    @abstractmethod
    def can_extract(self, url: str) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def extract(self, url: str) -> str:
        raise NotImplementedError()


class GeneralExtractor(Extractor):
    def __init__(self, extractors: list[Extractor]) -> None:
        super().__init__()
        self.extractors = extractors

    def can_extract(self, url: str) -> bool:
        return any(e.can_extract(url) for e in self.extractors)

    def extract(self, url: str) -> str:
        for e in self.extractors:
            if e.can_extract(url):
                return e.extract(url)

        raise ValueError(f"unable to extract {url}")
