from scrapy import signals
from scrapy.exceptions import DropItem
import pdb, sqlite3, os
from subprocess import Popen, PIPE
from hurry.filesize import size

class SaveFilePipeline(object):

    def process_item(self, item, spider):
        self.con = sqlite3.connect("songspk.db")
        self.cur = self.con.cursor()
        self.cur.execute("select * from songspk where title=:who", {"who": item['title']})
        if self.cur.fetchone() != None:
            print "Item is already downloaded"
            self.cur.close()
            return item;

        print "*************************** Here *******************************************"
        args = ['aria2c',
                    '--file-allocation=none',
                    '--split=4',
                    '--max-concurrent-downloads=4',
                    '--max-connection-per-server=4']
        ctext = ""
        for c in item['cookie']:
          ctext = ctext + "%s: %s;" %(c.name, c.value)
        args.append('--header="%s"' % ctext)
        args.append(item['url'])
        args.append('--out=%s.zip' % item['title'])
        output = "%s.output" % item['title']

        output = Popen(args, stdin=PIPE, stdout=1, stderr=2)
        output.stdin.close()
        stdout, stderr = output.communicate()
        rcode = output.returncode
        fileS = size(os.path.getsize('%s.zip' % item['title']))
        self.cur.execute("insert into songspk values (?, ?, ?, ?)", (item['title'], "%s.zip" %
              item['title'], rcode, fileS))
        self.con.commit()
        self.cur.close()
        return item
