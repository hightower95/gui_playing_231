import os
import configparser
from typing import Tuple


APP_DATA = os.getenv('APPDATA')
if not APP_DATA:
    raise EnvironmentError("APPDATA environment variable not found.")

pip_config_dir = os.path.join(APP_DATA, 'pip')
pip_config_file = os.path.join(pip_config_dir, 'pip.ini')


def get_howto_configure_index_url() -> str:
    """Get instructions on how to configure pip index-url"""
    return (
        "Click the button to open the webpage\n"
        "Click 'Set Me Up' at the top right\n"
        "Click 'Configure' tab\n"
        "Click 'Generate Token & Create Instructions' and wait for message 'The token has been generated successfully.'\n"
        "OBS: We dont want to copy just the token.\n"
        "Click 'Install' tab\n"
        "Copy all the text in the box under containing the text [global]\n"
        "Click 'Copy', and paste the index-url value into the field on this form.\n\n"
        "Alternatively, navigate to WIKI for picture based instructions."
    )


def is_valid_index_url_value(test_value: str) -> Tuple[bool, str]:
    """Validate the index-url value for pip configuration

    Args:
        test_value: The index-url value to validate

    Returns:
        True if the index-url is valid, False otherwise
    """
    if not test_value:
        return False, "index-url must not be empty"

    # Basic URL validation (can be expanded)
    if not test_value.startswith("[global]"):
        return False, "index-url must start with [global] - are you copying from the correct tab (Install)?"

    if not "index-url =" in test_value:
        return False, "index-url line missing - try clicking the 'Copy' button"

    if not "common-pypi/simple" in test_value:
        return False, "index-url must point to common-pypi/simple - confirm the dropdown selection says 'common-pypi'"

    return True, ""


def pip_exists_with_correct_sections() -> bool:
    """Check if pip config file exists and has required sections to enable further bootstrapping

    Returns:
        True if config file exists with required sections, False otherwise
    """
    global pip_config_file

    if not os.path.isfile(pip_config_file):
        return False

    config = configparser.ConfigParser()
    config.read(pip_config_file)

    if config.has_option("global", "index-url"):
        return True
    else:
        return False


def get_pip_config(create_if_not_exists: bool = False) -> configparser.ConfigParser:
    """Load or create pip configuration file

    Args:
        create_if_not_exists: If True, create the config file if it doesn't exist

    Returns:
        ConfigParser object with pip configuration
    """
    global pip_config_dir, pip_config_file

    folder_exists = os.path.isdir(pip_config_dir)
    if not folder_exists:
        if create_if_not_exists:
            os.makedirs(pip_config_dir, exist_ok=True)
        else:
            raise FileNotFoundError(
                f"Pip config directory not found: {pip_config_dir}")

    user_config = configparser.ConfigParser()
    if os.path.isfile(pip_config_file):
        user_config.read(pip_config_file)

    return user_config


def save_pip_config(config: configparser.ConfigParser) -> bool:
    """Save pip configuration to file

    Args:
        config: ConfigParser object with pip configuration

    Returns:
        True if saved successfully, False otherwise
    """
    global pip_config_dir, pip_config_file
    os.makedirs(pip_config_dir, exist_ok=True)
    try:
        with open(pip_config_file, 'w') as f:
            config.write(f)
        return True
    except Exception as e:
        print(f"Failed to save pip config: {e}")
        return False