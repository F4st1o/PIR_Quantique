from datetime import datetime

date_str1 = '2025-04-25T09:26:53.330Z'
date_str2 = '2025-04-26T11:30:00.000Z'

datetime.fromisoformat

dt1 = datetime.strptime(date_str1.replace('Z', '+0000'), '%Y-%m-%dT%H:%M:%S.%f%z')
dt2 = datetime.strptime(date_str2.replace('Z', '+0000'), '%Y-%m-%dT%H:%M:%S.%f%z')

delta = dt2 - dt1

total_seconds = int(delta.total_seconds())
days = total_seconds // 86400
hours = (total_seconds % 86400) // 3600
minutes = (total_seconds % 3600) // 60
seconds = total_seconds % 60

print(f"Durée : {days} jours, {hours} heures, {minutes} minutes, {seconds} secondes")
