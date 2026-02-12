import {Format} from "../../Format.js";

export class installShieldCAB extends Format
{
	name         = "InstallShield CAB";
	website      = "http://fileformats.archiveteam.org/wiki/InstallShield_CAB";
	ext          = [".cab"];
	magic        = ["InstallShield CAB", "InstallShield Cabinet archive", "InstallShield Compressed Archive", "ISC Archiv gefunden", "Archive: InstallShield Cabinet File"];
	keepFilename = true;
	auxFiles     = (input, otherFiles) =>
	{
		if(input.ext.toLowerCase()===".hdr")
			return false;
		
		// if we are a .cab file and there is another DATA1.CAB file, don't do anything further, as the extraction of data1.cab will get the files from this cab file
		if((/^data\d+.cab$/i).test(input.base) && otherFiles.some(file => file.base.toLowerCase()==="data1.cab"))
			return [];
		
		// .cab files often require .hdr files to extract, even a data2.cab would need a data1.hdr, so let's grab ALL .hdr files
		// also let's include all other .cab files so that multi-part cabs will extract properly
		const hdrAndCabFiles = otherFiles.filter(file => [".hdr", ".cab"].includes(file.ext.toLowerCase()));
		return hdrAndCabFiles.length>0 ? hdrAndCabFiles : false;
	};
	converters = ["unshield", "unshield[oldCompression]", "winPack[matchType:magic]", "gameextractor[codes:CAB_ISC_2,CAB_ISC_3]", "UniExtract[matchType:magic][hasExtMatch]"];
}
