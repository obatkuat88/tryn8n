#!/bin/bash

#!/bin/bash

# Activate virtualenv if present
if [ -f .venv/bin/activate ]; then
	# shellcheck source=/dev/null
	source .venv/bin/activate
fi

# Install dependencies (no-op if already installed)
pip install -r requirements.txt

# Allow overriding port via PORT env var, e.g. PORT=3000 ./run.sh
python app.py
