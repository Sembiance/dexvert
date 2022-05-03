import {Format} from "../../Format.js";

export class quarkXPress extends Format
{
	name           = "QuarkXPress";
	website        = "http://fileformats.archiveteam.org/wiki/QuarkXPress";
	ext            = [".qxd", ".qxp"];
	magic          = ["Quark XPress document"];
	notes          = "Could install QuarkXPress on WinXP, but haven't encountered any of these files 'in the wild' yet.";
	unsupported    = true;
}
