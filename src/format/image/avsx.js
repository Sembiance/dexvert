import {xu} from "xu";
import {fileUtil} from "xutil";
import {Format} from "../../Format.js";

export class avsx extends Format
{
	name       = "Stardent AVS X";
	website    = "http://fileformats.archiveteam.org/wiki/AVS_X_image";
	ext        = [".avs", ".mbfavs", ".x"];
	safeExt    = ".avs";
	idCheck    = async inputFile =>
	{
		if(inputFile.size<8)
			return false;
		
		const header = await fileUtil.readFileBytes(inputFile.absolute, 8);
		return (((header.getUInt32BE(0)*header.getUInt32BE(4))*4)+8)===inputFile.size;
	};
	mimeType   = "image/x-avsx";
	converters = [
		"wuimg",
		"imconv[format:x]",	// handles mandrill.x and EXPRESS.X but doesn't support transparency, but it's an acceptable tradeoff for now since wuimg appears to handle them
		"nconvert", `abydosconvert[format:${this.mimeType}]`,
		"tomsViewer"
	];
	verify     = ({meta}) => meta.height>1 && meta.width>1 && meta.colorCount>1;
}
