import {Format} from "../../Format.js";

export class s3m extends Format
{
	name         = "Scream Tracker Module";
	website      = "http://fileformats.archiveteam.org/wiki/S3M";
	ext          = [".s3m", ".stm"];
	magic        = ["ScreamTracker III Module sound data", "Scream Tracker 3 module", "Scream Tracker module", /^fmt\/(717|718)( |$)/];
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "zxtune123", "openmpt123", "adplay"];
}
