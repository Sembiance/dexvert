import {Format} from "../../Format.js";

export class broderbundMohawk extends Format
{
	name       = "Broderbund Mohawk";
	ext        = [".mhk"];
	magic      = ["Broderbund Mohawk game data archive"];
	converters = ["gameextractor"];
}
