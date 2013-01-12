/* Copyright 2013, Martin Zimmermann <info@posativ.org>. All rights reserved.
 * License: BSD Style, 2 clauses. See LICENSE for details.
 */

/*
 * Searches the (lowercase) term in suffix tree.  Returns either a valid query
 * or undefined for no match.
 */
var search = function(term) {

    var keyword = term.toLowerCase(), haystack, prefix;

    if (keyword.length < 2)
        return;

    if (!(keyword[0] in search.tree)) {
        prefix = keyword.charCodeAt(0) < 123 ? keyword[0] : "_";

        search.req.abort();
        search.req.open("GET", search.path + prefix + ".js", false);
        search.req.send()

        if (search.req.status != 200)
            return;

        haystack = JSON.parse(search.req.response);
        if (prefix == "_") {
            for (var attr in haystack) {
                search.tree[attr] = haystack[attr];
            }
        } else {
            search.tree[prefix] = haystack;
        }
    }

    return search.query(keyword.substring(1), search.tree[keyword[0]]);
}

/*
 * Search `needle` in `haystack` in something around O(m).  Returns a tuple
 * with first, the exact matches, and last the partial matches.
 */
search.query = function (needle, haystack) {

    // find partial matches
    function find(node) {

        var rv = [];

        if (typeof node == "undefined")
            return rv;

        if (node.length == 2) {
            for (var item in node[1])
                rv.push(node[1][item]);
        }

        for (var key in node[0]) {
            rv += find(node[0][key]);
        }

        return rv;
    }

    var node = haystack, partials = [],
        i = 0, j = 0;

    while (j < needle.length) {
        if (node[0][needle.substring(i,j+1)]) {
            node = node[0][needle.substring(i,j+1)]
            i = j + 1;
        }

        j++;
    }

    if (i != j) // no suffix found
        return;

    for (var key in node[0])
        partials = partials.concat(find(node[0][key]));

    return [node[1], partials];
}

/*
 * Return context around `keyword` from `id`, you can use `limit` to receive
 * up to N paragraphs containing `keyword`.  Returns an array or undefined.
 */
search.context = function(keyword, id, limit) {

    var req = new XMLHttpRequest(),
        rv  = new Array(), source;

    if (typeof limit == "undefined") {
        limit = 1;
    }

    req.open("GET", search.path + "src/" + id + ".txt", false);
    req.send();

    if (req.status != 200)
        return;

    source = req.response.split(/\n\n/);
    for (var chunk in source) {
        if (source[chunk].toLowerCase().indexOf(keyword.toLowerCase()) > -1) {
            if (limit == 0)
                break;

            rv.push(source[chunk]);
            limit--;
        }
    }

    return rv;
}

search.req = new XMLHttpRequest();
search.tree = {}

search.path = %% PATH %%;
search.lookup = %% ENTRYLIST %%;
