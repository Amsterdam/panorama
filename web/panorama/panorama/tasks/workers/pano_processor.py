from django.db import transaction


class PanoProcessor:
    status_queryset = None
    status_in_progress = None
    status_done = None

    def process(self):
        pano_to_process = self._get_next_pano()
        if not pano_to_process:
            return False

        self.process_one(pano_to_process)
        pano_to_process.status = self.status_done
        pano_to_process.save()

        return True

    def process_one(self, panorama):
        pass

    def _get_next_pano(self):
        try:
            with transaction.atomic():
                next_pano = self.status_queryset.select_for_update()[0]
                next_pano.status = self.status_in_progress
                next_pano.save()

            return next_pano
        except IndexError:
            return None
