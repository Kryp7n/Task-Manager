#!/bin/sh
source venv/bin/activate

echo Executing Database Upgrade Operation
flask db upgrade
echo Done!

echo Starting Server
exec flask run