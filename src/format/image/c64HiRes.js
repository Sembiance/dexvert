import {Format} from "../../Format.js";

export class c64HiRes extends Format
{
	name       = "C64 Hires-Bitmap";
	website    = "http://fileformats.archiveteam.org/wiki/Hires-Bitmap";
	ext        = [".hbm", ".hir", ".hpi", ".gih", ".fgs"];
	magic      = ["C64 Hires bitmap", "Koala Paint", "Hires C64 :hir:", "Fun Graphics Machine Hires :fgs:", "GigaPaint Hi-res :gih:"];
	weakMagic  = true;
	trustMagic = true;
	fileSize   = 8002;
	converters = ["recoil2png", "view64", "nconvert[format:hir]", "nconvert[format:fgs]", "nconvert[format:gih]"];
}
