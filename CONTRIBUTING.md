# Contributing to ED1 Home Assistant Integration

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Ways to Contribute

- Report bugs
- Suggest new features
- Improve documentation
- Submit pull requests
- Share your automations and dashboard configs

## Reporting Issues

### Bug Reports

When reporting a bug, please include:

1. **Description**: Clear description of the issue
2. **Steps to Reproduce**: How to trigger the bug
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**:
   - ESPHome version
   - Home Assistant version
   - ED1 board revision
6. **Logs**: Relevant log output (remove sensitive data)

### Feature Requests

For new features:

1. Check existing issues to avoid duplicates
2. Describe the use case
3. Explain the proposed solution
4. Consider alternatives

## Pull Requests

### Before You Start

1. Open an issue to discuss significant changes
2. Fork the repository
3. Create a feature branch from `main`

### Code Style

#### YAML Files

- Use 2-space indentation
- Add comments for non-obvious configurations
- Group related configurations with section headers
- Use meaningful IDs and names

```yaml
# Good
sensor:
  - platform: adc
    pin: GPIO34
    name: "ED1 Light Sensor"
    id: light_sensor
    update_interval: 1s

# Bad
sensor:
  - platform: adc
    pin: GPIO34
    name: "sensor1"
```

#### Documentation

- Use clear, concise language
- Include code examples where helpful
- Update table of contents if adding sections
- Test all code examples

### Commit Messages

Use clear, descriptive commit messages:

```
feat: Add accelerometer sensor support
fix: Correct touch button threshold for rev 2.3
docs: Add automation examples for matrix display
refactor: Simplify pixel mapper logic
```

Prefixes:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `refactor`: Code change without feature/fix
- `test`: Adding tests
- `chore`: Maintenance tasks

### Pull Request Process

1. **Update documentation** for any user-facing changes
2. **Test your changes** on actual hardware if possible
3. **Fill out the PR template** completely
4. **Request review** from maintainers

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Self-reviewed the code
- [ ] Added comments for complex logic
- [ ] Updated relevant documentation
- [ ] Tested on ED1 hardware (if applicable)
- [ ] No sensitive data (WiFi passwords, API keys)

## Development Setup

### Local Testing

1. Install ESPHome CLI:
   ```bash
   pip install esphome
   ```

2. Validate configuration:
   ```bash
   esphome config ed1-rev23-a.yaml
   ```

3. Compile without uploading:
   ```bash
   esphome compile ed1-rev23-a.yaml
   ```

### Testing Changes

1. Create `secrets.yaml` from template
2. Compile and upload to ED1 board
3. Monitor logs:
   ```bash
   esphome logs ed1-rev23-a.yaml
   ```

## Adding New Hardware Support

When adding support for unused ED1 hardware:

1. Reference the schematic in `docs/ED1 2.3/`
2. Check datasheets in `docs/ED1 2.3/DOC/`
3. Test thoroughly on hardware
4. Document the new feature
5. Update README feature list

### Template for New Sensor

```yaml
# ==========================================
# N. NEW SENSOR NAME
# ==========================================
sensor:
  - platform: <platform>
    name: "ED1 Sensor Name"
    id: sensor_id
    # Configuration specific to sensor
```

## Documentation Contributions

Documentation improvements are always welcome:

- Fix typos and grammar
- Clarify confusing sections
- Add missing information
- Translate to other languages
- Add diagrams or images

## Community

- Be respectful and inclusive
- Help others in issues and discussions
- Share your setups and automations
- Credit others' contributions

## License

By contributing, you agree that your contributions will be licensed under the project's Apache License 2.0.

## Questions?

Open an issue with the "question" label if you need help getting started.
