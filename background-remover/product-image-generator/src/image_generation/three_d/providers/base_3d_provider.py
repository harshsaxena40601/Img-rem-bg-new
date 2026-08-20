from abc import ABC, abstractmethod
from pathlib import Path


class Base3DProvider(ABC):
    """
    Base interface for every Image-to-3D provider.

    Any provider we use later must implement
    the generate() method.

    Examples:
    - Google Colab worker
    - RunPod worker
    - Local GPU
    - Future cloud provider
    """

    @abstractmethod
    def generate(
        self,
        request_data: dict,
        output_dir: Path,
    ) -> dict:
        """
        Generate a 3D model from the product request.

        Parameters
        ----------
        request_data:
            Data loaded from 3d_request.json.

        output_dir:
            Directory where the generated
            3D files should be saved.

        Returns
        -------
        dict
            Information about the generated
            3D model and output files.
        """

        pass