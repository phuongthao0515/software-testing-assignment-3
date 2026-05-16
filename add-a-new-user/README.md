# Data Driven Testing Guide for "Add a New User" feature


## 1. Installation Guide

### (a) Install Google Chrome

Download and install Google Chrome: https://www.google.com/chrome/

After installation, verify Chrome is installed successfully.

### (b) Install Python

Make sure Python 3 is installed on your system.

Check the installation using:

```bash
python --version
```

If Python is not installed, download it from: https://www.python.org/downloads/


### (c) Install Required Python Packages

Install all required Python libraries using the following command:

```bash
python -m pip install selenium pandas openpyxl colorama
```

Alternatively, install all dependencies from the `requirements.txt` file:

```bash
python -m pip install -r requirements.txt
```


## 2. Execute the Testing Scripts

Follow the steps below to execute the automated testing scripts.

### (a) Navigate to the Testing Directory

Change the current working directory to either the `level-1` or `level-2` folder.

```bash
cd level-1
```

or

```bash
cd level-2
```

### (b) Run the Testing Scripts

The framework supports executing multiple testing techniques using command-line options.

- Boundary Value Analysis (BVA)

```bash
python ts-003-bva-ecp-dt.py --bva
```

- Equivalence Class Partitioning (ECP)

```bash
python ts-003-bva-ecp-dt.py --ecp
```

- Decision Table Testing (DT)

```bash
python ts-003-bva-ecp-dt.py --dt
```

- Execute All Testing Techniques

```bash
python ts-003-bva-ecp-dt.py
```

- Use Case Testing

```bash
python ts-003-uc.py
```