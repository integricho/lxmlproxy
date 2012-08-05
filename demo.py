# -*- coding: utf-8 -*-
from lxml import etree

from lxmlproxy import LXMLProxyFactory


def ruin_data(key):
    return ['intercepted'], {}


def to_str(input_data, encoding='utf-8'):
    print 'stringify'
    try:
        return str(input_data)
    except Exception:
        try:
            return unicode(input_data).encode('utf-8')
        except Exception:
            return input_data

pre_processors = {'get': ruin_data}
post_processors = {'get': to_str,
                   'text': to_str,
                   'findtext': to_str}
class_types_to_wrap = (etree._Element,)

factory = LXMLProxyFactory(pre_processors,
                           post_processors,
                           class_types_to_wrap)

e = etree.fromstring(u'''<xml version="1.0" intercepted="intercepted">
                     <root><tree><leaf1 type="fresh">ättß</leaf1>
                     <leaf2 type="fresh">Üdsö</leaf2></tree></root></xml>''')
p = factory.make(e)
# test new element wrapper
(leaf,) = p.xpath('//leaf1')
print type(leaf)

# test text property post-processor
leaf_text = leaf.text
print type(leaf_text), leaf_text

# test findtext method post-processor
leaf_text = p.findtext('.//leaf2')
print type(leaf_text), leaf_text

# test get pre-processor
intercepted = p.get('version')
print intercepted

# test result list wrapper
list_of_results = p.xpath('//*[@type="fresh"]')
print list_of_results

# go deeper, see if the newly wrapped object runs the post-processors
for e in list_of_results:
    t = e.text
    print type(t), t
