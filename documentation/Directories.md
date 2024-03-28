### This is where [Chief](#chief) and [Workers](#workers) will write files to in their docker containers

##### Chief
```md
chief/app/
	resources/
		module-archives/
			module-name.tar
			...
		modules/
			module-name/
				Processor/
					Processor.py
					...
				Butcher/
					Split.py
					Merge.py
					...
			...
		jobs/
			job-name/
				module
				data-files/
					dataset file(s)
					...
				fragment-cache/
					fragment files
					...
				results/
					result file(s)
					...
			...
```

##### Workers
```md
worker/app/
	resources/
		processors/
			module-name/
				Processor.py
				...
		jobs/
			job-name/
				processor.name
				cache/
					fragment files
					...
```