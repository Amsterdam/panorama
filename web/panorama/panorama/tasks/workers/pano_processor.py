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
        self._set_status_to(pano_to_process, self.status_done)
        return True

    def process_one(self, panorama):
        pass

    @transaction.atomic
    def _get_next_pano(self):
        try:
            next_pano = self.status_queryset.select_for_update()[0]
            self._set_status_to(next_pano, self.status_in_progress)

            return next_pano
        except IndexError:
            return None

    @transaction.atomic
    def _set_status_to(self, panorama, status):
        panorama.status = status
        panorama.save()
