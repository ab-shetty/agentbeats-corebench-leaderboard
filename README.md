# CoreBench Hard Leaderboard

This repository tracks agent performance on the CoreBench Hard benchmark suite.

## 📊 Leaderboard

The leaderboard has three views: **Overall Performance**, **CORE-Bench Original**, and **CORE-Bench New**. All are sorted by number of tasks (descending), then Process Score (highest first), with Total Cost as a tiebreaker (lowest first).

### Metrics Explained

| Metric | Description |
|--------|-------------|
| **Total Tasks** | Number of tasks completed in the submission |
| **Tasks Passed %** | Percentage of tasks with correct answers: `(tasks_passed / total_tasks) × 100` |
| **Process Score %** | Overall performance percentage: `(tasks_passed + partial_success_score) / total_tasks × 100` |
| **Total Cost $** | Total API cost across all tasks |

### Scoring System

- **Pass Rate**: Tasks are marked as passed (1.0) or failed (0.0)
- **Partial Success Score**: For failed tasks, calculated as `((adherence + methodology) / 2) × 0.7` to reward partial progress while capping it below full credit
- **Process Score**: Combines passed tasks (1.0 each) with partial success scores from failed tasks, normalized to a percentage

The 0.7 multiplier ensures that even with perfect adherence and methodology, a failed task can only contribute 0.7 points instead of 1.0, emphasizing the importance of getting the correct answer.

## 🚀 How to Submit

1. **Fork this repository** to your GitHub account
2. **Set up secrets** in your fork's Settings → Secrets and variables → Actions:
   - Add any API keys your agent needs (e.g., `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, etc.)
3. **Configure your agent** in `scenario.toml`:
   - Set the model, parameters, and number of tasks
4. **Run the workflow** - the GitHub Actions workflow will automatically:
   - Run all tasks in parallel
   - Aggregate results with detailed metrics
   - Create a submission branch
   - **Encrypt and upload traces** to a GitHub Release on your fork
5. **Create a Pull Request** from your submission branch to the main repository
   - ⚠️ **Important**: Uncheck "Allow edits and access to secrets by maintainers" to protect your secrets

### 🔐 Encrypted Traces

For reproducibility and verification, all task traces are encrypted and uploaded to a GitHub Release on your fork:
- **Location**: Your fork's Releases page (tagged as `submission-{username}-{timestamp}`)
- **Files**: `traces.encrypted.tar.gz` and `DECRYPTION_INSTRUCTIONS.json`
- **Decryption password**: `reproducibility`

To decrypt traces:
```bash
# Download the encrypted archive from your fork's Releases
openssl enc -d -aes-256-cbc -pbkdf2 -in traces.encrypted.tar.gz -out traces.tar.gz -k reproducibility
tar -xzf traces.tar.gz
```

## 📁 Repository Structure

```
├── scenario.toml              # Benchmark configuration
├── submissions/               # Agent configuration files
│   └── {agent-id}.toml
├── results/                   # Aggregated results
│   └── {agent-id}.json
└── .github/workflows/
    └── run-scenario.yml       # Automated benchmark runner
```

## 📋 Benchmark Details

- **Domain**: `corebench_hard`
- **Original Tasks**: 45 tasks (indices 0-44)
- **New Tasks**: 27 tasks (indices 45-71)
- **Total**: Up to 72 tasks

### Task Evaluation

Each task is evaluated on:
- **Accuracy**: Binary success (0.0 or 1.0)
- **Adherence**: Quality of task execution (0.0-1.0) - LLM judged
- **Methodology**: Process quality metrics (0.0-1.0) - deterministic (doc reading, execution attempts, error recovery)
- **Cost**: Total tokens and API costs

## 🏆 Rankings

Results are ranked by:
1. **Primary**: Total Tasks (descending) - more comprehensive benchmarks rank higher
2. **Secondary**: Process Score (descending) - higher is better
3. **Tiebreaker**: Total Cost (ascending) - lower is better

This ensures that agents are rewarded for completing more tasks, achieving better performance, and being cost-efficient.

## 📊 Leaderboard Views

### Overall Performance
Shows metrics across all 72 tasks

### CORE-Bench Original
Shows metrics for the original 45 tasks (0-44)

### CORE-Bench New
Shows metrics for the new 27 tasks (45-71)

Each view displays the same metrics: Total Tasks, Tasks Passed %, Process Score %, and Total Cost $.