import {xu} from "xu";
import {Format} from "../../Format.js";

export class corelThumbnails extends Format
{
	name        = "Corel Thumbnails Archive";
	website     = "http://fileformats.archiveteam.org/wiki/CorelDRAW";
	filename    = [/^_thumbnail/i];
	unsupported = true;
	notes       = xu.trim`
		Contains a bunch of 'CDX' files that each start with CDRCOMP1. Wasn't able to locate anything on the internet that can process or open them.
		Even went so far as to install Corel ArtShow and tried to reverse engineer the DLL it uses (CDRFLT40.DLL) but failed.
		Sent an email to the libcdr creators, to see if they know of any info on the format, but never heard back.
		NOTE, if the only thing in this is images, then it should be moved to image family`;
}
