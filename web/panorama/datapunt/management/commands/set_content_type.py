from django.core.management import BaseCommand

from datasets.shared.object_store import ObjectStore

objs = ObjectStore()


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.set_content_type()

    def set_content_type(self):
        self._set_content_type_on_imgs(objs.panorama_conn, '2016', '/', '')
        self._set_content_type_on_imgs(objs.datapunt_conn, 'panorama', '/', '')

    def _set_content_type_on_imgs(self, conn, container, delimiter, path):
        _, directory = conn.get_container(container, delimiter=delimiter, path=path)
        subdirs = [store_object['subdir'] for store_object in directory if 'subdir' in store_object]
        subdirs.extend([file['name']+'/' for file in directory if 'name' in file and \
                        file['content_type'] == 'application/directory'])
        imgs = [file['name'] for file in directory if 'name' in file and file['name'][-4:] == '.jpg' and \
                file['content_type'] == 'application/octet-stream']
        for img in imgs:
            print('setting content type on: %s' % img)
            conn.post_object(container, img, {'Content-Type': 'image/jpeg'})

        for subdir in subdirs:
            print('walking subdir: %s' % subdir)
            self._set_content_type_on_imgs(conn, container, delimiter, subdir)
