TMPDIR != mktemp -d /tmp/acrylamid.XXX
MESSAGES := "`pwd`/.po"
LOCALE := "`pwd`/acrylamid/locale"

NIKOLA = "https://github.com/ralsina/nikola/archive/master.zip"

.PHONY: doc view upload i18n

.END:
	rm -rf $(TMPDIR)

.INTERRUPT:
	rm -rf $(TMPDIR)

doc:
	cd docs/ && make html

view:
	cd docs/_build/html && python2 -m SimpleHTTPServer

upload:
	rsync -ruv docs/_build/html/* www@morloch:~/posativ.org/acrylamid/

i18n: i18n-fetch i18n-compile

i18n-fetch: .IGNORE
	wget $(NIKOLA) -P $(TMPDIR)
	unzip "$(TMPDIR)/nikola-master.zip" -d $(TMPDIR)
	
	rm -rf $(MESSAGES)
	mv "$(TMPDIR)/nikola-master/translations/nikola.messages" $(MESSAGES)
	mv "$(TMPDIR)/nikola-master/LICENSE.txt" "$(MESSAGES)/LICENSE"
	
i18n-compile:
	for msg in `ls .po/ | grep -v LICENSE`; do \
		CODE=`echo $$msg | cut -d '.' -f 1`; \
		mkdir -p "$(LOCALE)/$${CODE}/LC_MESSAGES"; \
		msgfmt -o "$(LOCALE)/$${CODE}/LC_MESSAGES/nikola.mo" "$(MESSAGES)/$$msg"; \
	done
