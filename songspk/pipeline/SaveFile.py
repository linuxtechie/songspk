from scrapy import signals
from scrapy.exceptions import DropItem
import pdb, sqlite3, os, tempfile, stat
from subprocess import Popen, PIPE
from hurry.filesize import size
from songspk.settings import USER_AGENT
from scrapy import log


class SaveFilePipeline(object):

    def process_item(self, item, spider):
        self.con = sqlite3.connect("songspk.db")
        self.cur = self.con.cursor()
        self.cur.execute("select * from songspk where title=:who", {"who": item['title']})
        if self.cur.fetchone() != None:
            print "%s is already downloaded" % item['title']
            self.cur.close()
            return item;
        print "Downloading %s ..." % item['title']

        args = ['aria2c',
                    '--file-allocation=none',
                    '--split=4',
                    '--max-concurrent-downloads=4',
                    '--max-connection-per-server=4']
        ctext = ""
        for c in item['cookie']:
          ctext = ctext + "%s: %s;" %(c.name, c.value)
        ctext = ctext + ("User-agent: %s" % USER_AGENT)

        args.append('--header="%s"' % ctext)
        args.append('"%s"' % item['url'])
        args.append('--out="Downloaded/%s"' % item['filename'])
        
        output = "Downloaded/%s.output" % item['filename']
        
        sf = tempfile.NamedTemporaryFile(delete=False)
        sf.seek(0)
        sf.write("%s %s\n" % (' '.join(args), item['url']))
        sf.close()
        
        os.chmod(sf.name, stat.S_IXUSR | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXGRP)
        
        log = open(output, "wb+")
        
        p = Popen(sf.name, shell=True, stdin=None, stdout=log, stderr=log)
        p.wait()
        rcode = p.returncode
        
        log.close()
        
        if rcode == 0:
            self.cur.execute("insert into songspk values (?, ?, ?, ?)", (item['title'],
              item['filename'], 0, item['size']))
            self.con.commit()
        self.cur.close()
        print "Downloading %s complete" % item['title']
        return item
