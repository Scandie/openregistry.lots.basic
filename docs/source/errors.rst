.. _errors:

Responses
=========

After processing API always provides response, reporting either success
or failure.

Status Codes
------------
In all cases, the API should return an `HTTP Status Code
<http://en.wikipedia.org/wiki/List_of_HTTP_status_codes>`_ that indicates
the nature of the failure (see below), with a response body in JSON format
containing additional information.

200
  Success. If data was requested, it will be available in the `data` field
  at the top level of the response body.

201
  Success (for object creation). Its information is available in the `data`
  field at the top level of the response body.  The API URL where the object
  can be retrieved is also returned in the `Location` header of the
  response.

400
  Invalid request. This usually occurs because of a missing or malformed
  parameter.  Check the documentation and the syntax of your request and try
  again.

401
  No authorization. A valid API key was not provided with the request, so
  the API could not associate a user with the request.

403
  Forbidden. The API key and request syntax was valid but the server is
  refusing to complete the request.  This can happen if you are trying to
  read or write to objects or properties that you do not have access to.

404
  Not found. Either the request method and path supplied do not specify a
  known action in the API, or the object specified by the request does not
  exist.
  
412
  Precondition Failed. See :ref:`API in cluster mode <cluster>`.

429
  Rate Limit Enforced. See :ref:`Rate control <performance>`.
  
500
  Server error. There was a problem on OpenProcurement's end.

Success Response
----------------
Every successful get, create, update, replace request results in response
that contains `data` attribute.  That `data` attribute contains full JSON
object representation after the operation.  If some data were generated in
the result of processing (like new object IDs, or `modified` date) they are
present in the respose.

The listing requests result in similar responses, but instead of single
object in `data` attribute, the JSON response contains collection of
objects.

Example Success Response
~~~~~~~~~~~~~~~~~~~~~~~~
Here is a response that describes lot




Error Response
--------------
In the event of an error, the response body will contain an `errors` field
at the top level.  It contains an array of at least one error object,
described below:

:location:
   Part of the request causing the error. Possible values are `header` and `body`.

:name:
    * Specific header name that caused the problem (in case of `header` location)
    * The field name causing the error (in case of `body` location)

:description:
    Verbose (human readable) description of the error.

.. message
  *totalValue.amount: Missing input* - Message providing more detail about the
  error that occurred, if available.

.. messageUID
  Unique message id. Will stay the same even if content of the message can
  change, depending on other parameters.

.. *id*
  Unique correlation identifier of the error response for audit and issue
  reporting purposes.

Example Error Response
~~~~~~~~~~~~~~~~~~~~~~
Sample below indicates incomplete request.

