
# Python CLI

A Python command line tool that takes the architecture (amd64, arm64, mips etc.) as an argument and downloads the compressed Contents file associated with it from a Debian mirror. 

### How to Run
```
docker build -t package .    
docker run --rm package amd64
```

## Thought Process

1. Understanding the Problem: 

The script takes an architecture (amd64, arm64, etc.)

Downloads the corresponding Contents-<arch>.gz file from a Debian mirror

Parses the file to count how many file paths are associated with each package

Displays the top 10 packages with the highest number of file associations

2. Planning Components

Inputs

Outputs

Functions/Steps

3. Dockerizing

Using Docker makes the code portable and easy to run.