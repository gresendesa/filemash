# Filemesh

This program brings together files that links to each other into one file.

## How it works
	
A file (a) references another (b) through the expression:
```
	@> "[file_path_b]"
```
Once this expression is put inside file (a), the content of file (b) will replace the expression that refers it.

The file paths used in this expression must be related to the file itself.

## How to call the program

The syntax of the program calling is:
```
	python3 filemash.py main_file_path.foo
```

The program will output the result. So it's possible to pipe it:

```
	python3 filemash.py main_file_path.foo | cat
```
## Test the embedded sample

Just run:
```
	python3 filemash.py sample/animals_and_fruits.txt > output.txt
```