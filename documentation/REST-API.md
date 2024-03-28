# REST API descriptions
<br>

## Chief HTTP Server

### POST    connect/
> ##### Body parameters
> > - `password`
> ##### Response
> > - 200: served `/webui-index.html`

### POST    upload/data/
> ##### Body parameters
> > - `data`
> > - `files`
> ##### Response
> > - 200: successfully uploaded data

### POST    upload/module/
> ##### Body parameters
> > - `module` 
> > - `package`
> > - `files`
> ##### Response
> >- 200: successfully uploaded module package

### POST    initiate/job/
> ##### Body parameters
> > - `module name`
> > - `fragments endpoint`
> ##### Response
> >- 200: network activation successful
        
### POST    submit/work
> ##### Body parameters
> > - `result fragment`: `.tar` file
> > - `job-id`
> ##### Response
> >- 200: successfully uploaded result

### GET     retrieve/work/
> ##### Response
> > - 200: `results`

<br>

# Worker HTTP Server

### POST    upload/processor
> ##### Body parameters
> > - `processor`
> > - `module`
> ##### Response
> > - 200: sucessfully uploaded processor

### POST    activate
> ##### Body parameters
> > - `fragment`: `.tar` file
> > - `job-id`
> ##### Response
> > - 200: successfully uploaded fragment