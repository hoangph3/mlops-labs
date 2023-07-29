#!/bin/sh

${HIVE_HOME}/bin/schematool -initSchema -dbType postgres
${HIVE_HOME}/bin/hive --service metastore
