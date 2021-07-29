from microWebSrv.microWebSrv import MicroWebSrv

@MicroWebSrv.route('/tester/test-redir')
def _httpHandlerTestGet(httpClient, httpResponse):
	httpResponse.WriteResponseRedirect('/tester/pdf.png')

# ----------------------------------------------------------------------------

# test get page [/test-post]
@MicroWebSrv.route('/tester/test-post')
def _httpHandlerTestGet(httpClient, httpResponse):
	content = """\
	<!DOCTYPE html>
	<html lang=en>
        <head>
        	<meta charset="UTF-8" />
            <title>TEST GET</title>
        </head>
        <body>
            <h1>TEST GET</h1>
            Client IP address = %s
            <br />
			<form action="/tester/test-post" method="post" accept-charset="ISO-8859-1">
				First name: <input type="text" name="firstname"><br />
				Last name: <input type="text" name="lastname"><br />
				<input type="submit" value="Submit">
			</form>
        </body>
    </html>
	""" % httpClient.GetIPAddr()
	httpResponse.WriteResponseOk(headers=None,
								  contentType="text/html",
								  contentCharset="UTF-8",
								  content=content)

# ----------------------------------------------------------------------------

# test post data [/test-post]
@MicroWebSrv.route('/tester/test-post', 'POST')
def _httpHandlerTestPost(httpClient, httpResponse):
	formData = httpClient.ReadRequestPostedFormData()
	firstname = formData["firstname"]
	lastname = formData["lastname"]
	content = """\
	<!DOCTYPE html>
	<html lang=en>
		<head>
			<meta charset="UTF-8" />
            <title>TEST POST</title>
        </head>
        <body>
            <h1>TEST POST</h1>
            Firstname = %s<br />
            Lastname = %s<br />
        </body>
    </html>
	""" % (MicroWebSrv.HTMLEscape(firstname),
		    MicroWebSrv.HTMLEscape(lastname))
	httpResponse.WriteResponseOk(headers=None,
								  contentType="text/html",
								  contentCharset="UTF-8",
								  content=content)

# ----------------------------------------------------------------------------

# test get query parameters [/send?name=yaniv&last=cohen]
@MicroWebSrv.route('/tester/send')
def _httpHandlerEditWithArgs(httpClient, httpResponse):
	args = httpClient.GetRequestQueryParams()
	# print('QueryParams', args)
	content = """\
	<!DOCTYPE html>
	<html lang=en>
        <head>
        	<meta charset="UTF-8" />
            <title>TEST EDIT</title>
        </head>
        <body>
	"""
	content += "<h1>EDIT item with {} query arguments</h1>".format(len(args))
	if 'name' in args:
		content += "<p>name = {}</p>".format(args['name'])

	# if 'last' in args :
	#	content += "<p>last name = {}</p>".format(args['last'])

	for key in args:
		if key != "name": content += "<p>{key} = {val}</p>".format(
		    key=key, val=args[key])

	content += """
        </body>
    </html>
	"""
	httpResponse.WriteResponseOk(headers=None,
								  contentType="text/html",
								  contentCharset="UTF-8",
								  content=content)

# ----------------------------------------------------------------------------

# test path variable [see comments]
# <IP>/edit/123           ->   args['index']=123
@MicroWebSrv.route('/tester/edit/<index>')
# <IP>/edit/123/abc/bar   ->   args['index']=123  args['foo']='bar'
@MicroWebSrv.route('/tester/edit/<index>/abc/<foo>')
# <IP>/edit               ->   args={}
@MicroWebSrv.route('/tester/edit')
def _httpHandlerEditWithArgs(httpClient, httpResponse, args={}):
	content = """\
	<!DOCTYPE html>
	<html lang=en>
        <head>
        	<meta charset="UTF-8" />
            <title>TEST EDIT</title>
        </head>
        <body>
	"""
	content += "<h1>EDIT item with {} variable arguments</h1>".format(len(args))

	if 'index' in args:
		content += "<p>index = {}</p>".format(args['index'])

	if 'foo' in args:
		content += "<p>foo = {}</p>".format(args['foo'])

	content += """
        </body>
    </html>
	"""

	httpResponse.WriteResponseOk(headers=None,
								  contentType="text/html",
								  contentCharset="UTF-8",
								  content=content)

# ----------------------------------------------------------------------------