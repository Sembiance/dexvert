import {Format} from "../../Format.js";

export class powerPack extends Format
{
	name       = "PowerPacker Archive";
	website    = "http://fileformats.archiveteam.org/wiki/PowerPacker";
	ext        = [".pp"];
	magic      = [/^Power Packer.* compressed data/, "PowerPacker compressed", "PP: PowerPacker", "Archive: PP20", "Archive: Power Peak's PowerPacker", "Archive: PowerPack", /^PowerPacker$/];
	notes      = "Some files (Image & Aonia) won't extract (tried unar, ancient, ppunpack). I could install PowerPacker on the amiga and decrunch there. I looked at v4.0 and it was a nightmare to install, so I punted.";
	packed     = true;
	untouched    = dexState =>
	{
		if(dexState.hasMagics("PowerPacker compressed (password protected)"))
		{
			dexState.meta.passwordProtected = true;
			return true;
		}

		return false;
	};
	converters = ["unar[filenameEncoding:iso-8859-1]", "ancient", "amigadepacker"];
	verify     = ({inputFile, newFile}) => newFile.size>(inputFile.size*0.9);	// Some files detect as Powerpacker but expand to something much smaller. This trys to prevent that: https://discmaster.textfiles.com/browse/94/0_EPISODE_12_APR_1995.iso/demos/heir/heir.z/INTRO.PCV
}
