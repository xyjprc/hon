# HON
Code for generating Higher Order Network (HON) from data with higher order dependencies

## Requirements
Use Common Lisp to compile and run. SBCL recommended.
http://www.sbcl.org/
Some libraries may require Quicklisp.
http://www.quicklisp.org/

## Workflow
### Rule extraction
Use build-rules.lisp to extract rules from trajectories (or other types of data).
This corresponds to Algorithm 1 in paper.
### Network wiring
Use build-network.lisp to convert rules into High Order Network (HON) representation.
This corresponds to Algorithm 2 in paper.

## Notes
A test trajectory file test-trace.csv has been provided.