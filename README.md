# B12 Application Submission

Automated B12 job application submission via GitHub Actions.

## Setup (5 minutes)

### 1. Create the repository on GitHub
Push this folder to a new **public** GitHub repository.

### 2. Add the signing secret
Go to **Settings → Secrets and variables → Actions → New repository secret**:
| Name | Value |
|---|---|
| `SIGNING_SECRET` | `hello-there-from-b12` |

### 3. Edit `submit.yml` — replace the 3 placeholders
Open `.github/workflows/submit.yml` and update:
- `RESUME_LINK` — public URL to your resume (LinkedIn, hosted PDF, etc.)
- `REPOSITORY_LINK` — full URL of this GitHub repository
- `ACTION_RUN_LINK` — already uses `${{ github.run_id }}`, just replace the username/repo

### 4. Trigger the workflow
Go to **Actions → B12 Application Submission → Run workflow → Run workflow**

### 5. Copy the receipt
After the run completes, open the run logs. You'll see a line like:
```
✅  Submission successful!
    Receipt: your-submission-receipt
```
Paste that receipt into the B12 application form.
