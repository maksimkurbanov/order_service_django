#!/bin/sh

make migrate
make truncate_db
make run