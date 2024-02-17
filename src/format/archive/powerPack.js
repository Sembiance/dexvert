import {Format} from "../../Format.js";

export class powerPack extends Format
{
	name       = "PowerPacker Archive";
	website    = "http://fileformats.archiveteam.org/wiki/PowerPacker";
	ext        = [".pp"];
	magic      = [/^Power Packer.* compressed data/, "PowerPacker compressed", "PP: PowerPacker", /^PowerPacker$/];
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
}
