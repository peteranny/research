all:

mk:
	python mk_$(m).py $(v)

clean:
	rm *~ .*
