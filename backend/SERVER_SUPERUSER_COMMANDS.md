# Creating Superuser on Server (Nix Environment)

## Based on your environment:

You have Python available at `/root/.nix-profile/bin/python` (Nix-managed environment).

## Try these commands in order:

### 1. Check if Django is available:

```bash
python3 -c "import django; print(django.__version__)"
```

### 2. If Django is installed, create superuser:

```bash
python3 manage.py createsuperuser
```

### 3. If Django is NOT installed, try installing via pip:

```bash
# Check if pip is available through python
python3 -m pip --version

# If pip works, install dependencies
python3 -m pip install -r requirements.txt

# Then create superuser
python3 manage.py createsuperuser
```

### 4. Alternative: If you need to use Nix to install packages:

Since you're in a Nix environment, you might need to use Nix package manager to install dependencies.
