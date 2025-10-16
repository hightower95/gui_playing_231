"""
Configuration Migration Script

Migrates document scanner configurations from old location to new .tool_config directory.
Run this once to migrate existing configurations.
"""
from pathlib import Path
import json
import shutil
from datetime import datetime


def migrate_document_scanner_config():
    """Migrate document scanner configuration from old to new location"""

    # Old location
    old_config_dir = Path("document_scanner_cache")
    old_config_file = old_config_dir / "documents_config.json"

    # New location
    new_config_dir = Path(".tool_config")
    new_config_file = new_config_dir / "document_scanner.json"

    print("="*70)
    print("CONFIGURATION MIGRATION")
    print("="*70)

    # Check if old config exists
    if not old_config_file.exists():
        print("ℹ️  No old configuration found to migrate")
        print(f"   Looking for: {old_config_file}")
        return

    # Create new config directory
    new_config_dir.mkdir(exist_ok=True)
    print(f"✓ Created new config directory: {new_config_dir.absolute()}")

    try:
        # Load old configuration
        with open(old_config_file, 'r') as f:
            old_documents = json.load(f)

        print(f"✓ Loaded old configuration: {len(old_documents)} document(s)")

        # Create new configuration structure
        new_config = {
            "documents": old_documents,
            "migrated_from": str(old_config_file),
            "migration_date": datetime.now().isoformat()
        }

        # Save to new location
        with open(new_config_file, 'w') as f:
            json.dump(new_config, f, indent=2)

        print(f"✓ Saved to new location: {new_config_file.absolute()}")

        # Create backup of old file
        backup_file = old_config_file.with_suffix('.json.backup')
        shutil.copy2(old_config_file, backup_file)
        print(f"✓ Created backup: {backup_file}")

        print("\n" + "="*70)
        print("MIGRATION SUMMARY")
        print("="*70)
        print(f"Documents migrated: {len(old_documents)}")
        print(f"Old location: {old_config_file}")
        print(f"New location: {new_config_file}")
        print(f"Backup created: {backup_file}")
        print("\n✅ Migration completed successfully!")
        print("\nYou can safely delete the old 'document_scanner_cache' directory")
        print("after verifying the migration worked correctly.")

    except Exception as e:
        print(f"\n❌ ERROR during migration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    migrate_document_scanner_config()
