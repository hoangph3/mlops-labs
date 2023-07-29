#!/bin/sh

${HIVE_HOME}/bin/schematool -initSchema -dbType mysql
${HIVE_HOME}/bin/hive --service metastore
