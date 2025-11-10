from typing import List, Dict, Any
from configparser import ConfigParser


class InstallLibaryStep(BaseStep):
    def __init__(self, installation_settings: ConfigParser, shared_state: Dict[str, Any], libaries_to_install: List[str]):
        """Initialize the InstallLibaryStep

        Args:
            installation_settings: Configuration from install_settings.ini
            shared_state: Dictionary of state variables shared between steps
            libaries_to_install: List of library names to install in the venv
        """
        super().__init__(installation_settings, shared_state)
        self.libaries_to_install = self._get_libraries_to_install(
            libaries_to_install)

    def _get_libraries_to_install(self) -> List[str]:
        """Get the list of libraries to install in the venv

        Returns:
            List of library names to install
        """
        core_libraries = self.installation_settings.get(
            'Step_Install_Libraries', 'core_library', fallback='')
        additional_packages = self.installation_settings.get(
            'Step_Install_Libraries', 'additional_packages', fallback='')
        all_libraries = core_libraries.split(',')
        if additional_packages:
            all_libraries += additional_packages.split(',')
        return all_libraries

    def create_widgets(self) -> QWidget:
        """"""
        # Widget List:
        # "venv location"
        # "libraries to install"
        # "install libraries button"
        # "terminal view"
        # "validate install button"

    def validate_installation(self) -> bool:
        """"""
        # Check if all libraries are installed in the venv
        # Return True if all installed, False otherwise

        # There was an issue with pip being blown up silently by a library. In that event pip show library returned nothing.
        #

    def get_library_versions(self) -> str:
        """"""
        # Get the installed version of a library in the venv
        # Return version string or empty if not installed

    def complete_step(self):

        self.update_shared_state({
            'libraries_installed': True,
            'library_versions': self.get_library_versions()
        })
