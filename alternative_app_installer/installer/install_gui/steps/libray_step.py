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

    def install_latest_version(self, library, ensure_stable: bool = True) -> str:
        """"""
        # Get the installed version of a library in the venv
        # Return version string or empty if not installed
        from installer.utilities.pip_utils import get_library_versions

    def install_libraries(self, library_list):
        """"""
        # Install each library in self.libraries_to_install
        # Use pip install in the venv
        # Log progress to terminal view widget

    def _setup(self) -> bool:
        """"""
        # Prepare for installation step
        # Validate venv path from shared state
        self.venv_python = self.shared_state.get('venv_path', None)

        if self.venv_python is None:
            raise Exception(
                "Virtual environment path not set in shared state.")

        library_to_install = core_libraries = self.installation_settings.get(
            'Step_Install_Libraries', 'core_library', fallback='')

        get_latest_stable = self.installation_settings.getboolean(
            'Step_Install_Libraries', 'get_latest_stable_version', fallback=True)

        additional_packages = self._get_libraries_to_install()

        latest_version = version_manager.get_latest(stable=get_latest_stable)

        self.hint_txt = f"Installing libraries: {', '.join(library_to_install + additional_packages)} latest version: {latest_version}"

        return True

    def do_step(self) -> bool:
        """"""

        self.install_libraries(library_to_install, get_latest_stable)

    def complete_step(self):
        self.update_shared_state({
            'libraries_installed': True,
            'library_versions': self.get_library_versions()
        })
