# AutoMarker Plus

Original project forked (https://github.com/scmmmh/automarking.git) 

Automaker plus intends to include some quality of life improvements and additional capabilities (overtime).



## Requirements
- Python 3 (tested on Python 3.9.15)
- pip

## Installation
```shell
pip install git+https://github.com/Edge-Hill-Univeristy-Web/Automarker-Plus.git
```


## Change log:
- Removed political statements from student feedback
- Added support for HTML validator [link](https://teaching.computing.edgehill.ac.uk/validator/html/).
- Added support for CSS validator
- Added `GradeBookFix` class
  - fix_zips usage => `GradebookFix(task_id, module_code, task_file_extensions, gradebook_path, cwd).fix_zips()`
  - Utlra submission fix => `GradebookFix(task_id, module_code, task_file_extensions, gradebook_path, cwd)ultra_gradebook_submission_download_fix()`