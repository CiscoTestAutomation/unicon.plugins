"""C9800 wireless controller HA group connection implementation."""

from .. import IosXEc9800DualRPConnection
from .connection_provider import IosXEc9800HAGroupConnectionProvider


class IosXEc9800HAGroupConnection(IosXEc9800DualRPConnection):
    """Connect to two C9800 controllers through their individual consoles."""

    os = 'iosxe'
    platform = 'cat9k'
    model = 'c9800'
    chassis_type = 'ha_group'
    connection_provider_class = IosXEc9800HAGroupConnectionProvider

    def __init__(self, **kwargs):
        # The group selects this plugin, while each child is an ordinary
        # single-RP console whose hostname must be learned independently.
        kwargs.pop('chassis_type', None)
        kwargs.setdefault('learn_hostname', True)
        super().__init__(**kwargs)

    def create_subconnections(self, *args, aliases=None, **kwargs):
        """Enable hostname learning on topology-created group members."""
        kwargs.setdefault('learn_hostname', self.learn_hostname)
        return super().create_subconnections(
            *args,
            aliases=aliases or [],
            **kwargs,
        )
