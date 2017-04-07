import re #for Regex

def contain_number(word):
    """Returns Boolean whether a text contains a number"""
    return any(i.isdigit() for i in word)

def get_words_with_number(text):
    """Returns an iterator of the words that contains number in the text
    usefull to extract Bus No (i.e. 417A) or Bus Stop No
    """    
    return (word for word in text.split() if contain_number(word))
    
def get_urls(text):    
    """Returns an iterator of the URLs in the text, URL must start with http:// or https://"""
    regex = re.compile(("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"))
    return (url for url in re.findall(regex, text))

def get_emails(text):
    """Returns an iterator of matched emails found in the text"""
    # Removing lines that start with '//' because the regular expression
    # mistakenly matches patterns like 'http://foo@bar.com' as '//foo@bar.com'.
    regex = re.compile(("([a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`"
                "{|}~-]+)*(@|\sat\s)(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(\.|"
                "\sdot\s))+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)"))
    return (email[0] for email in re.findall(regex, text) if not email[0].startswith('//'))

def get_ip_address(text):
    """Returns an iterator of matched emails found in the text"""
    regex = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
    return (ip for ip in re.findall(regex, text))
