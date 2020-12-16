from unicon.plugins.aci.n9k.connection import AciN9KConnection as GenericAciN9KConnection
from unicon.plugins.nxos.aci.n9k.connection import AciN9KConnectionProvider


class AciN9KConnection(GenericAciN9KConnection):
    os = 'nxos'
    series = 'aci'
    model = 'n9k'
    connection_provider_class = AciN9KConnectionProvider