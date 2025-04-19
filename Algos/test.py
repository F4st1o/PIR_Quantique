
from datetime import datetime

when = datetime.now()
when = str(when.date()).replace("-","_")
print(when)