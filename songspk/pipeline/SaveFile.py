from scrapy import signals
from scrapy.exceptions import DropItem
import pdb, sqlite3, os
from subprocess import Popen, PIPE
from hurry.filesize import size
from songspk.settings import USER_AGENT


class SaveFilePipeline(object):

    def process_item(self, item, spider):
        self.con = sqlite3.connect("songspk.db")
        self.cur = self.con.cursor()
        self.cur.execute("select * from songspk where title=:who", {"who": item['title']})
        if self.cur.fetchone() != None:
            print "Item is already downloaded"
            self.cur.close()
            return item;

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
        args.append('--out="%s"' % item['filename'])
        output = "%s.output" % item['title']
        print " ".join(args)
        output = Popen(args, stdin=PIPE, stdout=1, stderr=2)
        output.stdin.close()
        stdout, stderr = output.communicate()
        rcode = output.returncode
        fileS = size(os.path.getsize('%s' % item['filename']))
        if rcode == 0:
            self.cur.execute("insert into songspk values (?, ?, ?, ?)", (item['title'], "%s.zip" %
                  item['title'], rcode, fileS))
            self.con.commit()
        self.cur.close()
        return item
