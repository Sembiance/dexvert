import {Format} from "../../Format.js";

export class venturaPublisher extends Format
{
	name        = "Ventura Publisher Graphic";
	website     = "http://fileformats.archiveteam.org/wiki/Ventura_Publisher";
	ext         = [".vgr"];
	magic       = ["Ventura Publisher Graphics bitmap"];
	unsupported = true;	// vibe coded a converter, but these are really just template files and exceedingly boring ones at that, no text, just boxes and circles and lines really, shelved it, see legacy/venturaPublisher
	notes       = "Tried both Ventura Publisher 4.1 and Corel Draw 5 (which includes it) and neither could open the sample VGR files I have.";
}
