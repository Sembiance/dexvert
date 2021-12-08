import {Format} from "../../Format.js";

export class installShieldCAB extends Format
{
	name          = "InstallShield CAB";
	website       = "http://fileformats.archiveteam.org/wiki/InstallShield_CAB";
	ext           = [".cab"];
	magic         = ["InstallShield CAB", "InstallShield Cabinet archive", "InstallShield compressed Archive"];
	keepFilename  = true;
	auxFiles     = (input, otherFiles) =>
	{
		if(input.ext.toLowerCase()===".hdr")
			return false;
		
		// .cab files often require .hdr files to extract, even a data2.cab would need a data1.hdr, so let's grab ALL .hdr files
		const hdrFiles = otherFiles.filter(file => file.ext.toLowerCase()===".hdr");
		return hdrFiles.length>0 ? hdrFiles : false;
	};
	converters = ["unshield", "unshield[oldCompression]", "winPack", "gameextractor", "UniExtract"];
	untouched  = ({f}) => f.input.ext.toLowerCase()===".hdr";
}
