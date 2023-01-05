import {Format} from "../../Format.js";

export class quarkXPress extends Format
{
	name       = "QuarkXPress";
	website    = "http://fileformats.archiveteam.org/wiki/QuarkXPress";
	ext        = [".qxd", ".qxp", ".qxd report"];
	safeExt    = "";
	magic      = ["Quark XPress document", "QuarkXPress Tags", /Quark Express Document/, /^fmt\/(650|1318|1325|1442)( |$)/];
	converters = ["quarkXPress6"];
}
