import {Format} from "../../Format.js";

export class quarkXPress extends Format
{
	name       = "QuarkXPress";
	website    = "http://fileformats.archiveteam.org/wiki/QuarkXPress";
	ext        = [".qxd", ".qxp", ".qxd report"];
	safeExt    = "";
	magic      = ["Quark XPress document", "QuarkXPress Tags", "Intel Quark Express Document", /Quark Express Document/, /^fmt\/(650|1317|1318|1319|1325|1442)( |$)/];
	converters = ["quarkXPress6", "pageMaker7QuarkConverter"];
}
