from django.core.management import BaseCommand

from datasets.shared.object_store import ObjectStore

object_store = ObjectStore()


class Command(BaseCommand):
    def handle(self, *args, **options):
        self._set_content_type_on_imgs(object_store.panorama_conn, '2016', '/', '')
        self._set_content_type_on_imgs(object_store.datapunt_conn, 'panorama', '/', '')

    def _set_content_type_on_imgs(self, conn, container, delimiter, path):
        _, directory = conn.get_container(container, delimiter=delimiter, path=path)
        subdirs = [store_object['subdir'] for store_object in directory if 'subdir' in store_object]
        subdirs.extend([file['name']+'/' for file in directory if 'name' in file and \
                        file['content_type'] == 'application/directory'])
        imgs = [file['name'] for file in directory if 'name' in file and file['name'][-4:] == '.jpg' and \
                file['content_type'] == 'application/octet-stream']
        for img in imgs:
            self.stdout.write('setting content type on: {}'.format(img))
            conn.post_object(container, img, {'Content-Type': 'image/jpeg'})

        for subdir in subdirs:
            self.stdout.write('walking subdir: {}'.format(subdir))
            self._set_content_type_on_imgs(conn, container, delimiter, subdir)
