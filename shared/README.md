# Project Echo Shared Libraries

Python libraries shared across channel repositories and the central orchestration system.

## Installation

**Development mode (from central repo):**
```bash
pip install -e .
```

**From Git (in channel repos):**
```bash
pip install git+https://github.com/user/project-echo-orchestration.git#subdirectory=shared
```

## Structure

```
shared/
├── src/
│   ├── scraping/            # Video scraping utilities
│   ├── transformation/      # Video transformation utilities
│   ├── publication/         # YouTube publication utilities
│   └── common/              # Common utilities
└── setup.py                 # Package configuration
```

## Usage

```python
from shared.scraping import video_discovery
from shared.transformation import ffmpeg_wrapper
from shared.publication import youtube_uploader

# Use shared utilities in your code
```

## Development

**Install in development mode:**
```bash
pip install -e .
```

Changes to shared libraries are immediately available after installation.

## Versioning

Shared libraries are versioned with the main project. Update version in `setup.py` and `__init__.py` when making breaking changes.
