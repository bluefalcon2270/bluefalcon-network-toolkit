# Changelog

All notable changes to the BlueFalcon NTK project will be documented in this file.

## [v2.0] - 2026-08-09
### Added
- Added a live progress indicator to the DNS tab (`Progress: X/Total`) that updates in real-time alongside the "Start Test" button.
- Upgraded the DNS "Status" column into a "Success" column to directly show the success rate (e.g., `10/12`) for each DNS server instead of a generic fraction.
### Fixed
- Fixed the "Copy IPs" button on the Domain tab that was previously copying an empty string; it now correctly exports all discovered IPs.
- Fixed a bug in the DNS tab where the "Sort" button crashed in the background when trying to sort success fraction text mathematically. The table now flawlessly sorts by highest success rate, followed by lowest average ping.
- Updated the "GitHub" link in the About tab to correctly route to the new `BlueFalcon-NTK` repository address.

## [v1.9] - 2026-08-09
### Fixed
- Fixed an oversight where the hardcoded SVG Version badge in `README.md` was left outdated at `v1.6`.

## [v1.8] - 2026-08-09
### Fixed
- Fixed an instant crash in the DNS scanner (`_tkinter.TclError`) that occurred when a user profile contained duplicate DNS IP addresses.
### Added
- Upgraded the Profile Manager with intelligent deduplication: When saving profiles, the app now automatically filters duplicate IPs/Domains. If duplicates exist with different alias names, the manager automatically combines their names to preserve all context.

## [v1.7] - 2026-08-09
### Changed
- Cleaned up repository tracking: Removed the obsolete `config_default.txt` file and added rules to ignore local `.agents` configurations and user-specific `Profile.txt` data from being pushed to GitHub.

## [v1.6] - 2026-08-09
### Fixed
- Fixed broken repository links in the `README.md` file.
### Added
- Added an official MIT License file to the repository.

## [v1.5] - 2026-08-09
### Changed
- Restructured `README.md` layout to use center-aligned headers, a professional badge array, and organized sections for better readability.

## [v1.4] - 2026-08-09
### Added
- Embedded high-quality application screenshot into the `README.md` to improve GitHub repository presentation.

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
