import {Format} from "../../Format.js";

export class dl extends Format
{
	name    = "DL Video";
	website = "http://fileformats.archiveteam.org/wiki/DL";
	ext     = [".dl"];
	idMeta  = ({macFileType}) => macFileType==="DL  ";
	
	// dl files will start with 0x03, 0x02 or 0x01
	byteCheck  = [{offset : 0, match : [[0x03, 0x02, 0x01]]}];
	
	converters = ["xanim", "deark[module:dlmaker] -> *ffmpeg[fps:10]"];
}
