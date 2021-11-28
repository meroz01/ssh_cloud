class Symbols(object):
    LOCAL = '[L]'
    REMOTE = '[R]'
    START_BANNER = f'''
        ╔═╗╔═╗╦ ╦  ╔═╗╦  ╔═╗╦ ╦╔╦╗
        ╚═╗╚═╗╠═╣  ║  ║  ║ ║║ ║ ║║
        ╚═╝╚═╝╩ ╩  ╚═╝╩═╝╚═╝╚═╝═╩╝
        
        {LOCAL} - local
        {REMOTE} - remote ssh server
        
        '''
    CONNECTING = f'{REMOTE} <~> {LOCAL}'
    CONNECTING_FAILED = f'{REMOTE} <X> {LOCAL}'
    CONNECTED = f'{REMOTE} >~< {LOCAL}'
    DISCONNECTED = f'{REMOTE} < > {LOCAL}'
    WATCHING = f'{REMOTE} > < {LOCAL}'
    SYNCHRONIZING = f'{REMOTE} <-> {LOCAL}'
    SYNCHRONIZED = f'{REMOTE} >-< {LOCAL}'
    CREATED = f'{REMOTE} *<== {LOCAL}'
    ADDED = f'{REMOTE} <== {LOCAL}'
    ADDED_LOCAL = f'{REMOTE} ==> {LOCAL}'
    REMOVED = f'{REMOTE} X <== {LOCAL}'
    REMOVED_REMOTE = REMOTE
    ERROR = f'{REMOTE} ? <== {LOCAL}'
    RECONNECTING = f'{REMOTE} < > {LOCAL}'
    ADD = '[+]'
    MODIFY = '[~]'
    DELETE = '[-]'
