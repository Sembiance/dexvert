import {Format} from "../../Format.js";

export class appleDOSDiskImage extends Format
{
	name           = "Apple DOS Disk Image";
	website        = "http://fileformats.archiveteam.org/wiki/DSK_(Apple_II)";
	ext            = [".dsk", ".po", ".hdv"];
	forbidExtMatch = true;
	magic          = [/^Apple DOS .*Image/, /^Apple ProDOS .*Image/, /^Apple II DOS .*disk image/, /^Apple II ProDOS .*disk image/];
	idMeta         = ({macFileType, macFileCreator}) => macFileType==="DSK5" && macFileCreator==="A2EM";
	converters     = ["cadius", "acx"];
	post            = dexState =>
	{
		const acxMeta = dexState.ran.find(({programid}) => programid==="acx")?.meta || {};
		if(acxMeta.volumeName)
			dexState.meta.comment = `${(dexState.meta.comment || "")} ${acxMeta.volumeName}`.trim();
	};
}
