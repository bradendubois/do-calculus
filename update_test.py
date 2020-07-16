#########################################################
#                                                       #
#   Main Module Load Control                            #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# Update the software and *then* import/load

from config.config_manager import access

# Enabled to update?
if access("github_pull_on_launch"):
    import subprocess
    subprocess.call(["./scripts/git_update.sh"])


# Now import and launch
import main
