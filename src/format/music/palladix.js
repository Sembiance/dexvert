import {Format} from "../../Format.js";

export class palladix extends Format
{
	name       = "Palladix";
	website    = "https://www.vgmpf.com/Wiki/index.php?title=PMA";
	ext        = [".plx", ".pma"];
	magic      = ["Palladix Ad Lib module"];
	converters = ["adplay"];
}
