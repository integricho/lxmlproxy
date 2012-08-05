lxmlproxy
=========

lxml wrapper to decorate it's methods, or pre/post process it's return values.

Motivated by a goal to override or decorate some methods of the famous lxml
library, this little spell is created for that exact task.

It's worth to note that this pattern can actually be used to wrap any kind
of classes, not just lxml, but as the the goal was to make that happen, the
more generic path was abandoned.

Sets up a factory to create wrappers for the chosen lxml element types.

Usage
=====

pre_processors and post_processors are both a dictionary, where the chosen attributes of the victim class are the keys, and the values are the functions which will wrap the input or return values from the victim class.

class_types_to_wrap is a tuple or list (it will be converted to a tuple anyway) which holds the list of the chosen classes that should be wrapped with our proxy class.

Example:

```python
pre_processors = {'get': ruin_input_data}  
post_processors = {'get': to_str,  
                   'text': to_str,  
                   'findtext': to_str}  
  
class_types_to_wrap = (etree._Element, html.HtmlElement)  
factory = LXMLProxyFactory(pre_processors,  
                           post_processors,  
                           class_types_to_wrap)  
victim_object = etree.fromstring('<xml><root><leaf></leaf></root></xml>')  
proxy = factory.make(victim_object)  
```

After this point, use proxy as you would use any regular lxml object, the methods / properties specified for the factory will process the input or output values automatically.

The demo.py included has some examples, to show a basic usage.