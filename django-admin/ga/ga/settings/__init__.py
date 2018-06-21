from ga.settings.base import *
from ga.settings.production import *

# section production settings
if DEBUG:
    from ga.settings.development import *
