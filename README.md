# DevMatic
![Build and Test](https://github.com/yourusername/DevMatic/actions/workflows/build.yml/badge.svg)

A multi-purpose development environment installer tool for Windows that manages installations in a single SDK folder without requiring admin privileges.

## Features

- 📦 Single SDK folder for all tools
- 🔒 No admin privileges required
- 🔄 Automatic updates
- 🛠️ Easy installations
- 📝 Environment management

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/DevMatic.git
cd DevMatic

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Build executable
python -m build
```

## Usage

```bash
# List available tools
devmatic list

# Install a tool
devmatic install <tool-name>

# Update a tool
devmatic update <tool-name>
```

## Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
pytest

# Format code
black src/
isort src/

# Run linting
flake8 src/
```

## License

MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
