#!/usr/bin/env bash
set -e

for lang in galaxy_ng/locale/* ; do
  echo "running msgattr for $lang"
  msgattrib --clear-fuzzy --empty -o $lang/LC_MESSAGES/django.po $lang/LC_MESSAGES/django.po
done
