all:

mk:
	python mk_$(m).py $(v)
ls:
	ls -lXp --group-directories-first
clean:
	rm *~ .*

