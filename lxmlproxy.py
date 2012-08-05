# -*- coding: utf-8 -*-
"""
Motivated by a goal to override or decorate some methods of the famous lxml
library, this little spell is created for that exact task.
It's worth to note that this pattern can actually be used to wrap any kind
of classes, not just lxml, but as the the goal was to make that happen, the
more generic path was abandoned.
"""


class LXMLProxyFactory(object):
    """
    Sets up a factory to create wrappers for the chosen lxml element types.
    
    pre_processors and post_processors are both a dictionary, where the chosen
    attributes of the victim class are the keys, and the values are the
    functions which will wrap the input or return values from the victim class.

    class_types_to_wrap is a tuple or list (it will be converted to a tuple
    anyway) which holds the list of the chosen classes that should be wrapped
    with our proxy class.

    e.g.:
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

    After this point, use proxy as you would use any regular lxml object, the
    methods / properties specified for the factory will process the input or
    output values automatically.
    """
    def __init__(self, pre_processors, post_processors, class_types_to_wrap):
        self._pre_processors = pre_processors
        self._post_processors = post_processors
        self._class_types_to_wrap = tuple(class_types_to_wrap)

    def _wrap(self, result):
        """
        Check if the returned value's type is on the _class_types_to_wrap
        list, and if so, wrap it with the proxy class.
        """
        if isinstance(result, self._class_types_to_wrap):
            # passing 'self' as a reference to the parent factory
            return self._ElementProxy(self, result)
        
        return result

    def _pre_process_input(self, name, *args, **kwargs):
        """
        Before passing the input value(s) to the lxml method, if the function
        name which requires them is on the pre-processors list, run the
        specified pre-processor function over the data.
        """
        try:
            # see if the name of the attribute is in our pre-processor list
            processor_func = self._pre_processors[name]
        except KeyError:
            # if no pre-processor was defined just return the input data
            return args, kwargs
        # pass the input data to the processor function and return the result
        return processor_func(*args, **kwargs)
        
    def _post_process_result(self, name, result):
        """
        After an lxml method/property returned a result, run the _post_processor
        method over it.
        The result type will be checked no matter what, if it has to be wrapped
        in a proxy or not.
        """
        try:
            # see if the name of the attribute is in our post_processor list
            processor_func = self._post_processors[name]
        except KeyError:
            # if no post-processor was defined don't touch the result
            pass
        else:
            # pass the result to the processor function
            result = processor_func(result)

        if isinstance(result, list):
            return map(self._wrap, result)

        return self._wrap(result)

    class _ElementProxy(object):
        """The actual Element wrapper class."""
        def __init__(self, factory, victim_object):
            self._factory = factory
            self._victim_object = victim_object

        def __getattribute__(self, name):
            """
            Get the attribute from the victim_object by the given name,  
            if it's a callable, decorate it with the pre/post processor 
            functions, if it's a property, run the post-processor on
            the return value.
            """
            victim_object = object.__getattribute__(self, '_victim_object')
            factory = object.__getattribute__(self, '_factory')
            
            attr = victim_object.__getattribute__(name)
            if hasattr(attr, '__call__'):
                def decorated(*args, **kwargs):
                    # be careful as the pre_processor function must return a
                    # list and a dictionary for args and kwargs in any case.
                    args, kwargs = factory._pre_process_input(name, *args, **kwargs)
                    result = attr(*args, **kwargs)
                    return factory._post_process_result(name, result)
                        
                return decorated
            
            return factory._post_process_result(name, attr)

    def make(self, victim_object):
        """
        The only publicly accessible method, which will wrap the given
        victim_object with the _ElementProxy class.
        """
        return self._ElementProxy(self, victim_object)

