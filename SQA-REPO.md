# SQA Activities and Lessons Learned

## 1. Activities Performed

Our team focused on integrating software quality assurance activities into the `MLForensics` project, specifically targeting fuzz testing and code robustness.

### Part 4A — Hybrid Fuzz Testing Implementation
We implemented a hybrid fuzzing system located in `fuzz.py` to automate defect detection.
* **Methodology:** We utilized a dual-strategy approach:
    * **Property-based fuzzing:** Leveraging the `Hypothesis` library to test logical invariants and data structures.
    * **Randomized input generation:** Injecting noise and malformed data to test raw resilience.
* **CI/CD Integration:** The script is configured as a GitHub Action, ensuring that fuzz testing occurs automatically on every push and pull request.
* **Logging:** All detected failures are automatically recorded in `fuzz_crashes.log` for asynchronous analysis.
* **Targeted Functions:**
    * `getPythonParseObject`
    * `getPythonAtrributeFuncs`
    * `getIncompleteLoggingCount`
    * `getGitRepos`
    * `getEventFrequency`

### Part 4B — Forensics and Robustness Improvements
We refactored existing code to enhance stability and diagnosability using defensive programming techniques.
* **Objectives:** To prevent crashes caused by malformed or unexpected inputs and to provide clearer forensic data through better logging.
* **Enhanced Methods:**
    * `getPythonParseObject`
    * `getPythonAtrributeFuncs`
    * `getFunctionAssignments`
    * `getIncompleteLoggingCount`
    * `getFunctionDefinitions`
    * `deleteRepo`
    * `cloneRepo`
    * `cloneRepos`
    * `getMLStats`
    * `getMLLibraryUsage`
    * `deleteRepos`

---

## 2. Lessons Learned

Through the implementation of these SQA activities, we established several key takeaways regarding software reliability, maintenance, and the specific challenges of testing forensic tools.

### The "Happy Path" vs. The Real World
Traditional unit tests often suffer from confirmation bias—we tend to write tests for scenarios we expect (the "happy path") and edge cases we already know about.
* **Lesson:** Fuzz testing revealed that our code was brittle when handling inputs that were syntactically valid but semantically garbage (e.g., an object that exists but lacks expected attributes).
* **Impact:** We learned that automated, randomized testing is the only reliable way to discover "unknown unknowns"—bugs that arise from input combinations a human developer would never think to type manually.

### Defensive Programming in Data-Intensive Applications
Working with `MLForensics` highlighted that data-mining applications cannot assume data integrity. External repositories or logs often contain malformed or incomplete data.
* **Lesson:** Robustness is not just about preventing crashes; it is about **graceful degradation**. Instead of allowing the entire script to halt on a single malformed Python object in `getPythonParseObject`, we learned to implement `try-except` blocks that log the error and allow the system to skip the bad entity and continue processing.
* **Takeaway:** "Fail loudly" is good for development, but "Log loudly and fail soft" is often better for data pipeline production.

### Observability is a Quality Feature
Initial crashes during fuzzing were difficult to diagnose because the generic Python tracebacks did not include the *input* that caused the crash.
* **Lesson:** Exception handling is useless without context. We shifted our strategy from simply catching errors to logging "Forensic Evidence"—capturing the specific state of the application (e.g., the exact string or object ID) at the moment of failure.
* **Impact:** This reduced debugging time significantly. We learned that **observability** (understanding *why* it failed) is just as critical to SQA as **reliability** (preventing the failure).

### The Value of Continuous Quality (CI/CD)
Manual testing is prone to "drift"—as time passes, developers stop running local tests before committing.
* **Lesson:** By integrating `fuzz.py` into GitHub Actions, we enforced a quality gate. The tests run whether we remember them or not.
* **Takeaway:** Automation creates a "ratchet effect" for quality; once a test is added to the CI pipeline, the code quality can strictly only go up (or stay the same), never down, because regressions are caught immediately.