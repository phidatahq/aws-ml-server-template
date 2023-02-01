#!/bin/bash

############################################################################
#
# Entrypoint script
#
############################################################################

if [[ "$PRINT_ENV_ON_LOAD" = true || "$PRINT_ENV_ON_LOAD" = True ]]; then
  echo "=================================================="
  printenv
  echo "=================================================="
fi

############################################################################
# Start App
############################################################################

case "$1" in
  api-dev)
    echo "Running: api start --reload"
    exec api start --reload
    ;;
  api-prd)
    echo "Running: api start"
    exec api start
    ;;
  chill)
    ;;
  *)
    echo "Running: $@"
    exec $@
    ;;
esac

echo ">>> hello world!"
while true; do sleep 18000; done
