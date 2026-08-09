# Changelog

All notable changes to the BlueFalcon NTK project will be documented in this file.

## [v1.3] - 2026-08-09
### Changed
- Improved sidebar logo typography by centering the text, increasing the title font size, and applying a cyan accent color to the subtitle.

## [v1.2] - 2026-08-09
### Changed
- Standardized all UI timeout inputs to use milliseconds (ms).
- Set default timeout configurations to 1000ms across all modules.
- Set default worker thread counts to 1000 for maximum out-of-the-box concurrency.
- Fixed an internal bottleneck limiting the maximum number of thread pool workers.

## [v1.1] - 2026-08-09
### Changed
- Refactored the Profile Manager into a streamlined single-file system (`Profile.txt`).
- Dropped multiple-profile switching in favor of a simpler workflow.
- Updated default configuration templates to include comprehensive DNS servers and common domains.
- Updated internal UI layout for the Profiles tab: added "Open Profile File" and "Reset to Default" buttons.
- Updated application branding to "BlueFalcon NTK".

## [v1.0] - 2026-08-08
### Added
- Initial release merging "Network Toolkit" and "DNS Benchmark Pro" into a single, unified suite.
- Material Design 3 UI overhaul.
- Asynchronous core processing for ICMP, TCP, and DNS scanning.
