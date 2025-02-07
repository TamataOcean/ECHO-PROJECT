import time
from pygstc.gstc import *
from pygstc.logger import *

# Permet de tester le service gstd en affichant une mire vidéo. 

pipeline = 'videotestsrc ! videoconvert ! autovideosink'
# Create a custom logger that logs into stdout, named pygstc_example, with debug level DEBUG
gstd_logger = CustomLogger('pygstc_example', loglevel='DEBUG')
# Create the client and pass the logger as a parameter
gstd_client = GstdClient(logger=gstd_logger)
gstd_client.pipeline_create('p0', pipeline)
gstd_client.pipeline_play('p0')
# Wait for the pipeline to change state
time.sleep(0.1)
# This should print 'PLAYING'
print(gstd_client.read('pipelines/p0/state')['value'])

# Boucle principale (Garde le programme en vie)
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🔴 Arrêt du programme.")
    gstd_client.pipeline_stop('p0')
    gstd_client.pipeline_delete('p0')