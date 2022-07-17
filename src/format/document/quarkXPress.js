import {Format} from "../../Format.js";

export class quarkXPress extends Format
{
	name           = "QuarkXPress";
	website        = "http://fileformats.archiveteam.org/wiki/QuarkXPress";
	ext            = [".qxd", ".qxp"];
	magic          = ["Quark XPress document", /Quark Express Document/, /^fmt\/(1318|1325|1442)( |$)/];
	notes          = "Could install QuarkXPress on WinXP, but haven't encountered very many of these files 'in the wild' yet.";
	unsupported    = true;
}
