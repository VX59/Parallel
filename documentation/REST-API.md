# REST API descriptions

## Web-UI hosted on Chief
```
POST    connect/
        -password
        response:   200, served /webui-index.html
```
```
POST    upload/data/
        -data-files
        response: 200, successfully uploaded data
```
```
POST    upload/module/
        -module-package-files
        response: 200, successfully uploaded module package
```
```
POST    initiate/job/
        -module-name
        -fragments-endpoint
        response: 200, network activation successful
```
```        
POST    submit/work
        -result-fragment (.tar)
        -job-id
        response: 200, successfully uploaded result
```
```
GET     retrieve/work/
        response: 200, results
```

## Worker http server
```
POST    upload/processor
        -processor-module
        response: 200, sucessfully uploaded processor
```
```
POST    activate
        -fragment   (.tar)
        -job-id
        response: 200, successfully uploaded fragment
```