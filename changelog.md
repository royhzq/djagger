# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.4] - 2022-10-25

### Removed

- Removed support for DRF `NullBooleanField` field for compatibility with the latest DRF version 3.14.
- Removed mapping of DRF serializer `label` to pydantic Field `alias` parameter.

### Fixed

- Bug where documentation for generic views are duplicated.

## [1.1.3] - 2022-04-17

### Fixed

- Fixed bug where authorizations and security schemes were not being rendered. `components` parameter passed was not being proceessed in `Document.generate`.

## [1.1.2] - 2022-04-06

### Added
- Added `url_names` parameter to `get_url_patterns` to allow `DJAGGER_DOCUMENT` to filter API endpoints that should be documented via their url names.
- Added missing `.gitignore` file.

### Fixed
- Fixed date typos in this changelog file.

## [1.1.1] - 2022-02-06
### Added
- Rest framework ``serializers.ChoiceField`` and ``serializers.MultipleChoiceField`` will now be represented as ``Enum`` types with enum values correctly reflected in the schema.
- Documentation for using Tags.

### Fixed
- Fix bug where schema examples are not generated correctly.
- Fix bug where the request URL for the objects are generated with an incorrect prefix.

## [1.1.0] - 2022-01-04
### Added
- Added documentation.
- Support for generic views and viewsets.
- Support for DRF Serializer to pydantic model conversion.
- Support for multiple responses and different response content types.
- Support for function-based views via ``schema`` decorator.
- Added option for a global prefix to all Djagger attributes.
- Generated schema fully compatible with OpenAPI 3.

### Removed
- `djagger.swagger.*` pydantic models. Removed support for Swagger 2.0 specification.

## [1.0.3] - 2021-12-11

### Changed
- More template changes.

## [1.0.2] - 2021-12-11

### Changed
- Fixed more template bugs.

## [1.0.1] - 2021-12-11

### Changed
- Fixed template bugs.

## [1.0.0] - 2021-12-11

### Changed
- Renamed `types.py` to more appropriate `schema.py`.
- Removed `.egg-info` files from version control.

## [0.1.1] - 2021-12-11

### Added
- Added this `changelog.md` file.

### Changed
- Updated `get_url_patterns` to include all installed apps if an empty list is provided to `app_names` parameter.
