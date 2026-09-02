from ..settings import FxosSettings


class FxosFp4kSettings(FxosSettings):
    """" FXOS/FP4k platform settings """

    def __init__(self):
        super().__init__()

        # What pattern to wait for after system restart
        self.BOOT_WAIT_PATTERN = r'^.*?vdc 1 has come online'
        # How many times the boot_wait_msg should occur to determine boot has finished
        self.BOOT_WAIT_PATTERN_COUNT = 1
