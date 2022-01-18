import {Format} from "../../Format.js";

export class powerPack extends Format
{
	name       = "PowerPacker Archive";
	website    = "http://fileformats.archiveteam.org/wiki/PowerPacker";
	ext        = [".pp"];
	magic      = [/^Power Packer.* compressed data/, "PowerPacker compressed", "PP: PowerPacker"];
	notes      = "Some files (Image & Aonia) won't extract (tried unar, ancient, ppunpack). I could install PowerPacker on the QEMU amiga and decrunch there. I looked at v4.0 and it was a nightmare to install, so I punted.";
	converters = dexState =>
	{
		// if our original filename doesn't have a .pp extension, then keep the original filename (so mod.sway results in mod.sway) otherwise make sure we renameOut
		const rkf = dexState.phase.format.ext.includes(dexState.original.input.ext) ? "[renameOut]" : "[renameKeepFilename]";
		return [`unar[filenameEncoding:iso-8859-1]${rkf}`, `ancient${rkf}`, `amigadepacker${rkf}`];
	};
}
