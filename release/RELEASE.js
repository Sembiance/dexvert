import {xu} from "xu";
import {path} from "std";

const RELEASE = {};
RELEASE.WEBSITE_PREFIX = "https://telparia.com/dexvert";
RELEASE.VERSION = "1.0.0";
RELEASE.RELEASE_DIR = path.join(xu.dirname(import.meta));
RELEASE.TARBALL_DIR = path.join(xu.dirname(import.meta), "tarballs");
RELEASE.FILENAMES =
[
	"dexserver.sh",
	"dexvert-ssh-key",
	"dexvert.sh",
	"hd.qcow2",
	"readme.txt"
];

RELEASE.README_TEXT = `## Requirements
Linux with QEMU (qemu-system-x86_64) installed.
CPU with avx support (most modern CPUs have this)

## Install
Download the latest <a href="${RELEASE.WEBSITE_PREFIX}/dexvert-${RELEASE.VERSION}.tar.bz2">dexvert-${RELEASE.VERSION}.tar.bz2</a> (12GB) and extract it (42GB)

## Usage
Run \`dexserver.sh\` to start the server. Wait for it to say: **dexserver ready!!!**

In a seperate terminal run \`dexvert.sh <inputFile> <outputDir>\` to convert a file.

Add \`--keepGoing\` flag to automatically convert any new files it extracts.

Add \`--json\` flag to also output JSON metadata about each file it converts.`;

export {RELEASE};
