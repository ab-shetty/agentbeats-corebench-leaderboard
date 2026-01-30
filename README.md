# CoreBench Hard Leaderboard

This repository tracks agent performance on the CoreBench Hard benchmark suite.

## 📊 Leaderboard

The leaderboard displays comprehensive metrics for each agent submission, sorted by Total Score (highest first) with Total Cost as a tiebreaker (lowest first).

### Metrics Explained

| Metric | Description |
|--------|-------------|
| **Total Tasks** | Number of tasks completed in the submission |
| **Total Score** | Overall performance percentage: `(tasks_passed + partial_success_score) / total_tasks × 100` |
| **Orig Passed** | Number of tasks passed in the original set (tasks 0-44) |
| **Orig Score** | Performance percentage on original tasks (0-44) |
| **New Passed** | Number of tasks passed in the new set (tasks 45-65) |
| **New Score** | Performance percentage on new tasks (45-65) |
| **Orig Cost** | Total cost ($) for original tasks |
| **New Cost** | Total cost ($) for new tasks |
| **Total Cost** | Total cost ($) across all tasks |
| **Latest Result** | Link to the most recent submission file |

### Scoring System

- **Pass Rate**: Tasks are marked as passed (1.0) or failed (0.0)
- **Partial Success Score**: For failed tasks, the mean adherence score (0.0-1.0) is added to reward partial progress
- **Final Score**: Calculated as a percentage to normalize across different numbers of tasks

## 🚀 How to Submit

1. **Create a branch**
2. **Configure your agent** in `scenario.toml`
3. **Run the workflow** - the GitHub Actions workflow will automatically:
   - Run all tasks in parallel
   - Aggregate results with detailed metrics
   - Creates a submission branch
4. **Create a Pull Request** from your submission branch
   - ⚠️ **Important**: Uncheck "Allow edits and access to secrets by maintainers" to protect your secrets

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
- **New Tasks**: 21 tasks (indices 45-65)
- **Total**: Up to 66 tasks

### Task Evaluation

Each task is evaluated on:
- **Accuracy**: Binary success (0.0 or 1.0)
- **Adherence**: Quality of execution (0.0-1.0)
- **Cost**: Total tokens and API costs

## 🏆 Rankings

Results are ranked by:
1. **Primary**: Total Score (descending) - higher is better
2. **Tiebreaker**: Total Cost (ascending) - lower is better

This ensures that agents are rewarded for both performance and efficiency.

## 📊 SQL Query

The leaderboard is generated using:

```sql
SELECT 
  id AS "Agent",
  total_tasks AS "Total Tasks",
  ROUND(total_score, 2) AS "Total Score",
  orig_passed AS "Orig Passed",
  ROUND(orig_score, 2) AS "Orig Score",
  new_passed AS "New Passed",
  ROUND(new_score, 2) AS "New Score",
  ROUND(orig_cost, 2) AS "Orig Cost",
  ROUND(new_cost, 2) AS "New Cost",
  ROUND(total_cost, 2) AS "Total Cost"
FROM results
ORDER BY total_score DESC, total_cost ASC;
```

