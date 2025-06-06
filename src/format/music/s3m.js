import {Format} from "../../Format.js";

export class s3m extends Format
{
	name         = "Scream Tracker Module";
	website      = "http://fileformats.archiveteam.org/wiki/Scream_Tracker_3_module";
	ext          = [".s3m", ".stm"];
	magic        = ["ScreamTracker III Module sound data", "Scream Tracker 3 module", "Scream Tracker module", "Scream Tracker 2 song/module", "S3M Module", "audio/x-s3m", "audio/x-stm", /^fmt\/(717|718)( |$)/];
	idMeta       = ({macFileType, macFileCreator}) => macFileType==="S3M " || (macFileType==="SONG" && macFileCreator==="ZS3M");
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "zxtune123", "openmpt123", "adplay", "gamemus[format:s3m-screamtracker]"];
}
