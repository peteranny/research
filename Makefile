all:

mk:
	python mk_$(m).py $(v)
ls:
	ls -lXp --group-directories-first
run:
	sh run.sh
clean:
	rm *~ .*

