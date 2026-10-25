import physicalquantities
import csv
import sys

with open("tests.csv", newline="") as test_file:
    reader = csv.reader(test_file, skipinitialspace=True, strict=True)
    fail_count = 0
    count = 0
    for row in reader:
        thing = physicalquantities.process_input(row[0]).to_string()
        if thing != row[1]:
            print(f"Test failed: {row}, program output: \"{thing}\"", file=sys.stderr)
            fail_count += 1
        count += 1

    print(f"Failed {fail_count} tests out of {count}")