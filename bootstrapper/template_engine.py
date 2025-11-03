"""
Template Engine for Bootstrap Application
Handles loading and rendering of file templates
"""
from pathlib import Path
from typing import Dict, Any
from constants import TEMPLATES_DIR


class TemplateEngine:
    """Simple template engine for rendering application files"""

    def __init__(self, template_dir: Path = None):
        if template_dir is None:
            template_dir = Path(__file__).parent / TEMPLATES_DIR
        self.template_dir = Path(template_dir)

        if not self.template_dir.exists():
            raise FileNotFoundError(
                f"Template directory not found: {self.template_dir}")

    def render(self, template_name: str, **kwargs) -> str:
        """
        Render a template with the given variables

        Args:
            template_name: Name of the template file (with or without .template extension)
            **kwargs: Variables to substitute in the template

        Returns:
            Rendered template content as string
        """
        # Ensure .template extension
        if not template_name.endswith('.template'):
            template_name += '.template'

        template_path = self.template_dir / template_name

        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        # Read template content
        template_content = template_path.read_text(encoding='utf-8')

        # Render template with provided variables
        try:
            return template_content.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing template variable: {e}")

    def render_all(self, template_variables: Dict[str, Any]) -> Dict[str, str]:
        """
        Render all available templates with the same variables

        Args:
            template_variables: Dictionary of variables to substitute in all templates

        Returns:
            Dictionary mapping output filename to rendered content
        """
        rendered = {}

        # Get all .template files in the template directory
        template_files = list(self.template_dir.glob("*.template"))

        for template_file in template_files:
            # Output filename is template name without .template extension
            output_name = template_file.stem

            try:
                rendered_content = self.render(
                    template_file.name, **template_variables)
                rendered[output_name] = rendered_content
            except (FileNotFoundError, ValueError) as e:
                # Log error but continue with other templates
                print(
                    f"Warning: Failed to render template {template_file.name}: {e}")
                continue

        return rendered

    def get_available_templates(self) -> list:
        """Get list of available template names (without .template extension)"""
        template_files = list(self.template_dir.glob("*.template"))
        return [template_file.stem for template_file in template_files]

    def template_exists(self, template_name: str) -> bool:
        """Check if a template exists"""
        if not template_name.endswith('.template'):
            template_name += '.template'

        template_path = self.template_dir / template_name
        return template_path.exists()


# Global template engine instance for easy access
template_engine = TemplateEngine()
