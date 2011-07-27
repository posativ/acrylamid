# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see lilith.py

tt_item = """
<div id="disqus_thread"></div>
<script type="text/javascript">
    var disqus_shortname = '{{ disqus_shortname }}'; // required: replace example with your forum shortname

    // The following are highly recommended additional parameters. Remove the slashes in front to use.
    var disqus_identifier = "{{ url }}";
    var disqus_url = "{{ url }}";

    /* * * DON'T EDIT BELOW THIS LINE * * */
    (function() {
        var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
        dsq.src = '{{ protocol }}://' + disqus_shortname + '.disqus.com/embed.js';
        (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
    })();
</script>
<noscript>
    <p>Please enable JavaScript to view the <a href="https://disqus.com/?ref_noscript">comments powered by Disqus.</a></p>
</noscript>
<a href="{{ protocol }}://disqus.com" class="dsq-brlink">
    blog comments powered by <span class="logo-disqus">Disqus</span>
</a>""".strip()

# counter script
tt_script = """
<script type="text/javascript">
    /* * * CONFIGURATION VARIABLES: EDIT BEFORE PASTING INTO YOUR WEBPAGE * * */
    var disqus_shortname = '{{ disqus_shortname }}'; // required: replace example with your forum shortname

    /* * * DON'T EDIT BELOW THIS LINE * * */
    (function () {
        var s = document.createElement('script'); s.async = true;
        s.type = 'text/javascript';
        s.src = '{{ protocol }}://' + disqus_shortname + '.disqus.com/count.js';
        (document.getElementsByTagName('HEAD')[0] || document.getElementsByTagName('BODY')[0]).appendChild(s);
    }());
</script>""".strip()

tt_counter = """<a href="{{ url }}#disqus_thread">Kommentieren</a>"""

def cb_start(request):
    
    env = request._env    
    env['disqus_thread'] = tt_item
    env['disqus_script'] = tt_script
    env['disqus_counter'] = tt_counter
    
    return request
    
def cb_prepare(request):
    """Disqus cannot handle relative urls..."""
    
    conf = request._config
    data = request._data
    
    for i, entry in enumerate(data['entry_list']):
        url = conf['www_root'] + '/' + str(entry.date.year) + \
              '/' + tools.safe_title(entry['title']) + '/'
        data['entry_list'][i]['url'] = url
        
    return request    
