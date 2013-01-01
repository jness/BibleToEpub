from Bible import Bible
import os
from shutil import copyfile
import zipfile

OUTPUT_FILE = 'Holy_Bible.epub'

# Open our Bible XML file which we found at 
# http://sspc-website.googlecode.com/svn-history/r10/trunk/include/bibles/
bible = Bible('bibles/nkjv.xml')

# Copy in some static epub files
if not os.path.exists('epub/'):
    os.makedirs('epub/')
if not os.path.exists('epub/META-INF/'):
    os.makedirs('epub/META-INF/')
    copyfile('static/container.xml', 'epub/META-INF/container.xml')
copyfile('static/mimetype', 'epub/mimetype')
copyfile('static/metadata.opf_temp', 'epub/metadata.opf')
meta = open('epub/metadata.opf', 'a')
copyfile('static/toc.ncx_temp', 'epub/toc.ncx')
toc = open('epub/toc.ncx', 'a')

link = 2
bid = 1
for book in bible.bible:
    print '[INFO] Writing Book "%s"' % book
    toc.write('''
<navPoint playOrder="%s">
<navLabel>
    <text>%s</text>
</navLabel>
<content src="content/%s.html" />\n''' % (link, book, bid))
    link += 1
    for chapter in bible.bible[book]:
	toc.write('''
    <navPoint playOrder="%s">
	<navLabel>
              <text>Chapter %s</text>
	</navLabel>
            <content src="content/%s.html" />
    </navPoint>\n''' % (link, chapter, bid))
	link += 1
	
        if not os.path.exists('epub/content/'):
	    os.makedirs('epub/content/')
	copyfile('static/template.html', 'epub/content/%s.html' % bid)
	f = open('epub/content/%s.html' % bid, 'a')
	f.write('<h1>%s</h1>' % book)
	f.write('<h3>Chapter %s</h3>' % chapter)
	for verse in bible.bible[book][chapter]:
	    body = bible.bible[book][chapter][verse]
	    f.write('<p><b>%s:</b> %s</p>' % (verse, body))
	f.write('</body></html>')
	f.close()
	meta.write('     <item href="content/%s.html" id="id1.%s" media-type="application/xhtml+xml"/>\n' % \
			(bid, bid))
	bid += 1
    toc.write('</navPoint>\n')

# close our our table of contents
toc.write('''
    </navPoint>
  </navMap>
</ncx>''')
toc.close()

# Write in the Spine to our metadata.opf
meta.write('<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>\n')
meta.write('</manifest>\n')
meta.write('  <spine toc="ncx">\n')
for i in range(1, bid):
    meta.write('     <itemref idref="id1.%s"/>\n' % i)
meta.write('</spine>\n')
meta.write('</package>')
meta.close()

# Zip up the content and make a epub
target_dir = 'epub'
zip = zipfile.ZipFile(OUTPUT_FILE, 'w', zipfile.ZIP_DEFLATED)
rootlen = len(target_dir) + 1
for base, dirs, files in os.walk(target_dir):
   for file in files:
      fn = os.path.join(base, file)
      zip.write(fn, fn[rootlen:])
