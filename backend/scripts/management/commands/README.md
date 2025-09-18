# Django Management Commands for Scripts App

This directory contains Django management commands for seeding and managing data in the scripts app.

## TitleTone Seeding Commands

### Basic Seeder: `seed_title_tones`

Seeds the TitleTone model with the basic predefined tone values used in the API validation.

```bash
# Run the basic seeder
python manage.py seed_title_tones
```

**Tones included:**

- Controversial
- Shocking
- Persuasive
- Mysterious
- Dramatic
- Question-based
- Sarcastic
- Witty
- Neutral

### Comprehensive Seeder: `seed_all_tones`

More advanced seeder with additional options and extended tone list.

```bash
# Basic usage
python manage.py seed_all_tones

# Clear existing tones first (WARNING: Deletes all existing tones)
python manage.py seed_all_tones --clear

# Dry run to see what would be created
python manage.py seed_all_tones --dry-run

# Clear and reseed everything
python manage.py seed_all_tones --clear
```

**Additional tones included:**

- Educational
- Inspirational
- Urgent

## Usage Examples

1. **First time setup:**

   ```bash
   python manage.py seed_title_tones
   ```

2. **Reset all tones:**

   ```bash
   python manage.py seed_all_tones --clear
   ```

3. **Preview changes:**
   ```bash
   python manage.py seed_all_tones --dry-run
   ```

## After Seeding

1. **Admin Interface**: Manage tones at `/admin/scripts/titletone/`
2. **API Validation**: The API will automatically validate against database tones
3. **Adding New Tones**: Add through Django admin or extend the seeder scripts

## Notes

- The seeders use `get_or_create()` so running them multiple times won't create duplicates
- Existing tones are preserved unless you use the `--clear` flag
- The API serializer automatically fetches valid tones from the database
