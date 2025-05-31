import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class appleVolumeLabelImage extends Format
{
	name       = "Apple Volume Label Image";
	website    = "http://fileformats.archiveteam.org/wiki/Apple_volume_label_image";
	magic      = ["deark: applevol"];
	idCheck    = async inputFile =>
	{
		if(inputFile.size<18)
			return false;
		
		const declaredWidth = (await fileUtil.readFileBytes(inputFile.absolute, 2, 1)).getUInt16BE();
		if(((declaredWidth*12)+5)!==inputFile.size || [0, 12].includes(declaredWidth))
			return false;

		return true;
	};
	converters = ["deark[module:applevol]"];
}
