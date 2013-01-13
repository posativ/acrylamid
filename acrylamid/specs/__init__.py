
from attest import Tests

from acrylamid.specs import (lib, readers, filters, filters_builtin, helpers,
                             imprt, views, utils, entry, content, core, search)


testsuite = Tests()
testsuite.register(lib.TestHTMLParser)
testsuite.register(readers.tt)
testsuite.register(filters.TestFilterlist)
testsuite.register(filters.TestFilterTree)
testsuite.register(filters_builtin.tt)
testsuite.register(filters_builtin.Hyphenation)
testsuite.register(helpers.Helpers)
testsuite.register(imprt.Import)
testsuite.register(imprt.RSS)
testsuite.register(imprt.Atom)
testsuite.register(imprt.WordPress)
testsuite.register(views.Tag)
testsuite.register(utils.TestMetadata)
testsuite.register(entry.TestEntry)
testsuite.register(content.SingleEntry)
testsuite.register(content.MultipleEntries)
testsuite.register(core.Cache)
testsuite.register(search.tt)
