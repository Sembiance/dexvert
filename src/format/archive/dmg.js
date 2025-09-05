import {Format} from "../../Format.js";

const _DMG_DISK_IMAGE_MAGIC = [/^fmt\/1071( |$)/];
export {_DMG_DISK_IMAGE_MAGIC};

const DMG_MAGIC = ["Macintosh Disk image", "zlib compressed data", "ZLIB compressed data", "Apple UDIF disk image", "Format: Universal Disk Image Format", "application/x-apple-diskimage"];

export class dmg extends Format
{
	name       = "Apple Disk Image";
	website    = "http://fileformats.archiveteam.org/wiki/Apple_Disk_Image";
	ext        = [".dmg"];
	priority   = this.PRIORITY.LOW;
	// for some reason, some DMG files identify as ZLIB data
	magic      = [...DMG_MAGIC, ..._DMG_DISK_IMAGE_MAGIC];
	weakMagic  = DMG_MAGIC;
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="dmg " && macFileCreator==="ddsk";
	converters = ["dmg2img", "sevenZip"];
}
