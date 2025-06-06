import {xu} from "xu";
import {fileUtil} from "xutil";
import {Format} from "../../Format.js";

export class avsx extends Format
{
	name       = "Stardent AVS X";
	website    = "http://fileformats.archiveteam.org/wiki/AVS_X_image";
	ext        = [".avs", ".mbfavs", ".x"];
	magic      = ["Stardent AVS X image :avs:"];
	idCheck    = async inputFile =>
	{
		if(inputFile.size<8)
			return false;
		
		const header = await fileUtil.readFileBytes(inputFile.absolute, 8);
		return (((header.getUInt32BE(0)*header.getUInt32BE(4))*4)+8)===inputFile.size;
	};
	mimeType   = "image/x-avsx";
	converters = [
		"x2tga",	// properly handles mandrill.x & EXPRESS.X & AVS_LOGO.X but doesn't handle transparency, but that's a fine enough tradeoff for now
		"wuimg",
		"nconvert[format:avs]", `abydosconvert[format:${this.mimeType}]`,
		"imconv[format:x]",
		"tomsViewer"
	];
	verify = ({meta}) => meta.height>1 && meta.width>1 && meta.colorCount>1;
}
