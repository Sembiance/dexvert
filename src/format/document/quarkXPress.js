import {Format} from "../../Format.js";

export class quarkXPress extends Format
{
	name       = "QuarkXPress";
	website    = "http://fileformats.archiveteam.org/wiki/QuarkXPress";
	ext        = [".qxd", ".qxp", ".qxd report"];
	safeExt    = "";
	magic      = [
		"Quark XPress document", "QuarkXpress project", "QuarkXPress Tags", "Intel Quark Express Document", "QuarkXPress Document/Project", /Quark Express Document/,
		/^fmt\/(650|652|1317|1318|1319|1321|1323|1325|1442|1443|1444)( |$)/, /^x-fmt\/182( |$)/
	];
	converters = ["quarkXPress6", "pageMaker7QuarkConverter"];
	notes      = "Some samples don't convert: 1_8.5x11.qxd report, 10_11X14.qxd and 9_8.5X14.qxd report";
}
