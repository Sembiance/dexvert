import {Format} from "../../Format.js";

export class sea extends Format
{
	name       = "Self Extracting Stuffit Archive";
	website    = "http://fileformats.archiveteam.org/wiki/StuffIt";
	ext        = [".sea"];
	magic      = ["Macintosh Application (MacBinary)", "Preferred Executable Format", "Mac StuffIt Self-Extracting Archive"];
	weakMagic  = ["Macintosh Application (MacBinary)", "Preferred Executable Format"];
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="APPL" && macFileCreator==="EXTR";
	converters = ["unar[mac]"];
	verify     = ({dexState, newFile}) =>
	{
		// some files like archive/sea/QReader.sea will infinite loop extract over and over. But unar throws an error in this case, so can check for that
		const unrarRan = dexState.ran.find(({programid}) => programid==="unar");
		if(!unrarRan || !unrarRan?.stdout?.includes("Archive parsing failed!"))
			return true;

		if(dexState.f?.files?.new?.length!==1)
			return true;

		if(newFile.base!==unrarRan.originalInput.base)
			return true;

		return false;
	};
}
