from unicon.plugins.aci.n9k.connection import AciN9KConnection as GenericAciN9KConnection


class AciN9KConnection(GenericAciN9KConnection):
    os = 'nxos'
    series = 'aci'
    model = 'n9k'
