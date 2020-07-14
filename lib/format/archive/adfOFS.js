"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Amiga Disk Format (OFS)",
	website : "http://fileformats.archiveteam.org/wiki/ADF_(Amiga)",
	ext     : [".adf"],
	magic   : ["Amiga Disk image File (OFS)", "Amiga DOS disk"],
	unsupportedNotes : XU.trim`
		Not all ADF disk images are properly extracted by unar/unadf/adf-extractor.
		I've tried TONS of programs and they all fail on these disks, which are identified as the OFS variety.
		Yet fs-uae emulator loads the disks and runs them fine in an emulated amiga.
		So I could create an amiga workbench script that will convert all contents of an amiga disk into a ZIP file
		and put it on a shared folder/hard drive and get the contents that way. That's a lot more work, but doable.`
};

exports.steps = [() => ({program : "extract-adf"})];
