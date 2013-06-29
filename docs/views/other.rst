Other
=====

.. _views-sitemap:

Sitemap
-------

Create an XML-Sitemap where permalinks have the highest priority (1.0) and do
never change and all other ressources have a changefreq of weekly.

.. code-block:: python

    '/sitemap.xml': {
        'view': 'Sitemap'
    }

The sitemap by default excludes any resources copied over with the entry. If
you wish to include image resources associated with the entry, the config
property ``SITEMAP_IMAGE_EXT`` can be use to define file extensions to
include. ``SITEMAP_RESOURCE_EXT`` can be used for other file types such as
text files and PDFs. Video resources are not supported, and should not be
included in the above properties.
