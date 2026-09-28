--------------------------------------------------------------------------------
Fix
--------------------------------------------------------------------------------
* iosxe/cat8k
    * Treated ``image_to_boot`` as a ROMMON fallback during reload instead of
      forcing devices that autoboot normally to transition through ROMMON.
