# OrangeHRM Assessment (Selenium + Python + behave BDD + Allure)

## 1.Prerequisites
- Python 3.10+
- Google Chrome (the matching driver is downloaded automatically by Selenium Manager)
- [Allure command-line tool](https://allurereport.org/docs/install/) (needs Java 8+), e.g.
  `brew install allure`, `scoop install allure` or `npm install -g allure-commandline`

## 2.Setup
```bash
git clone "https://github.com/OratilweBoitumelo/Assessments.git"
cd assessments
cd amrod_orangehrm

python -m venv .venv             
.\.venv\Scripts\Activate.ps1        # <<powershell command to activate VM
pip install -r requirements.txt
cp .env.example .env             # Windows: copy .env.example .env
```

## 3.Run
```bash
behave                                        # all features
```

If `behave` does not pick up `behave.ini` for some reason, this is the equivalent command:
```bash
behave -f allure_behave.formatter:AllureFormatter -o reports -f pretty
```

## 4.View the Allure report
```bash
allure serve reports
```

## 5.Project structure
```
features/
  employee_management.feature   # E2E scenario (Gherkin)
  negative_scenarios.feature    # negative scenarios (Gherkin)
  environment.py                # browser setup/teardown, failure screenshots
  steps/                        # step definitions (thin, call page objects)
pages/                          # page objects (all selectors live here)
reports/                        # Allure results, screenshots, logs (generated, git-ignored)
config.py                       # env/config loading
logger.py                       # logging setup (reports/logs/test_run.log)
employee_data.py                # test data (unique employee name per run)
```
