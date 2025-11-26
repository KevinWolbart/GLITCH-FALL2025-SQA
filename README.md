# Forensic Anti-patterns in Machine Learning Engineering

### Team name
- Team Glitch

### Team members
- Kevin Wolbart
- Shane Banachowski
- Luis Postigo

### Objective 

The objective of this project is to integrate software quality assurance activities into an existing Python project. Whatever we learned from our workshops will be integrated in the project. 

### Details 

> Demo video for the work in progress: https://drive.google.com/file/d/14lcIbDCIfHu8chqEOS7IX-yEckDFjT8z/view?usp=sharing

## Tasks performed.

#### Part 4A — Fuzz Testing
We implemented a hybrid fuzzing system in fuzz.py that targets five functions across the MLForensics project. The fuzzer uses both property-based fuzzing (Hypothesis) and randomized input generation to detect crashes in:

- getPythonParseObject
- getPythonAtrributeFuncs
- getIncompleteLoggingCount
- getGitRepos
- getEventFrequency

All failures are recorded in fuzz_crashes.log, and the script is configured to run automatically through GitHub Actions.

#### Part 4B — Forensics and Robustness Improvements
We enhanced the robustness of five different methods by integrating defensive programming and improved exception handling. The updated methods include:

- getPythonParseObject
- getPythonAtrributeFuncs
- getFunctionAssignments
- getIncompleteLoggingCount
- getFunctionDefinitions

These updates prevent crashes on malformed or unexpected input, provide clearer forensic information through logging, and ensure the project behaves correctly under fuzzing and real-world variability.
