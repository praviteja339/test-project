#!/bin/sh

bi() {
	dirname=$1

	echo Building ${dirname}...

	cd $dirname || exit 1

	docker build -t amps/$dirname . || exit 1

	cd ..
}

bi stretch-slim-xojo
bi stretch-slim-xojo-libreoffice
bi stretch-slim-node-11-libreoffice
